# $Id$

# Whip::Tag is what all the whip tag handlers inherit from.  It
# supplies basic features for parsing and rendering tags.

package Whip::Tag;

use warnings;
use strict;

use Whip::Attribute;

sub TAG_NAME    () { 0 }
sub TAG_DATA    () { 1 }
sub TAG_WHIP    () { 2 }
sub TAG_PARAM   () { 3 }

sub SCALAR () { 0x0100 }
sub LIST   () { 0x0200 }

sub REQ    () { 0x1000 }

use vars qw($whip_self);

### Helper: Render something.

sub render_page {
  my ($self, $page_id) = @_;
  $self->[TAG_WHIP]->render_page($page_id, {});
}

### Accessor: Get a parameter.

sub get_param {
  my ($self, $field_name) = @_;
  return $self->[TAG_PARAM]->{$field_name};
}

### Helper: Emit a document.

sub emit_document {
  my $self = shift;
  $self->[TAG_WHIP]->emit_document(@_);
}

### Accessor: Find out why something failed.

sub get_fail_flags {
  my ($self, $field_name) = @_;
  if (exists $self->[TAG_PARAM]->{_whip_failed}->{$field_name}) {
    return
      join( ", ",
            sort values %{$self->[TAG_PARAM]->{_whip_failed}->{$field_name}}
          );
  }
  return ();
}

### Handle inheritance and base class loading via the C<use> line.

sub import {
  my ($class, $base_class) = @_;

  my $caller_package = (caller)[0];
  foreach (qw(SCALAR LIST REQ)) {
    no strict 'refs';
    *{"$caller_package\::$_"} = \&{"$class\::$_"};
  }

  if (defined $base_class) {
    my $base_package = Whip->load_page("$base_class.tag");
    eval "package $caller_package; use base qw($base_package)";
    die if @$;
    undef $whip_self;
  }
}

### Create a new whip tag.

sub new {
  my ($class, $whip, $tag_name, $tag_data, $page_params) = @_;

  my $self = bless [], $class;
  $self->[TAG_NAME]    = $tag_name;
  $self->[TAG_DATA]    = [ ];
  $self->[TAG_WHIP]    = $whip;
  $self->[TAG_PARAM]   = $page_params;

  while (my ($name, $val) = each %$tag_data) {
    $self->set_contents(Whip::Attribute->new($name, $val));
  }

  # Open the tag.
  $self->open();

  return $self;
}

### Virtual base method.

sub get_syntax { () }

### Accessor to get the page ID.

sub get_page_id {
  my $self = shift;
  return $self->[TAG_WHIP]->get_page_id();
}

### Simple takes.  These create "take_foo" accessors for the simple
### cases.

sub set_syntax {
  my $package = shift;

  my @syntax = $package->get_syntax();
  if (@syntax % 2) {
    Whip->error( 500, "Error Loading Tag Syntax",
           "<tt>$package\::get_syntax()</tt> returned an odd number of things."
         );
  }

  my %syntax = @syntax;

  foreach my $name (keys %syntax) {
    no strict 'refs';
    *{"$package\::take_$name"} =
      sub {
        my $self = shift;
        $self->push($name => @_);
      }
  }

  Whip->set_syntax($package, \@syntax);
}

### Accessor: Return the name of the tag.

sub name {
  my $self = shift;
  return $self->[TAG_NAME];
}

### Virtual base methods: Open and close the tag.

sub open  { }
sub close { }

### Set the tag's contents.  Contents are data fields.

sub set_contents {
  my ($self, @contents) = @_;
  CORE::push @{$self->[TAG_DATA]}, @contents;
}

### Get the tag's contents as a list.

sub get_contents {
  my $self = shift;
  return @{$self->[TAG_DATA]};
}

### Get the tag's contents as a hash.  The list is flattened out.

sub get_contents_as_hash {
  my $self = shift;
  my %contents;
  foreach (@{$self->[TAG_DATA]}) {
    my $name = $_->name();
    my $value = $_->value();

    if (exists $contents{$name}) {
      if (ref $contents{$name} eq "") {
        $contents{$name} = [ $contents{$name} ];
      }
      CORE::push @{$contents{$name}}, $value;
    }
    else {
      $contents{$name} = $value;
    }
  }
  return %contents;
}

### Fetch a single value from a tag.  In scalar context, the last
### value for an attribute name is returned.  In list context, all the
### values for the name are returned.

sub fetch {
  my ($self, $target_name, @default) = @_;
  my @value;

  foreach (@{$self->[TAG_DATA]}) {
    my $name = $_->name();
    next unless "Whip::Tag::$name"->isa("Whip::Tag::$target_name");
    CORE::push @value, $_->value();
  }

  @value = @default unless @value;
  return @value if wantarray;
  return $value[-1] if @value;
  return;
}

sub push {
  my ($self, $target_name, @values) = @_;
  foreach (@values) {
    CORE::push @{$self->[TAG_DATA]}, Whip::Attribute->new($target_name, $_);
  }
}

### Replace the contents of the tag with a new set of values.  May be
### obsolete.

sub replace_contents {
  my $self = shift;
  die;
  $self->[TAG_DATA] = [ ];
  while (my ($name, $value) = splice(@_, 0, 2)) {
    CORE::push @{$self->[TAG_DATA]}, Whip::Attribute->new($name, $value);
  }
}

### Emit a data event.

sub emit {
  my ($self, $type, $value) = @_;
  $self->[TAG_WHIP]->emit($type, $value);
}

1;

__END__

use CGI qw(escape escapeHTML);

### Move the _value of a tag into an attribute named after the tag.
### This is used by tags that augment their parent structures.

sub from_value {
  my ($state, $tag) = @_;
  $state->rename_value($tag);
}

### Wiki-parse the value.

sub wiki_value {
  my ($state, $tag) = @_;

  my $input = $state->delete("_value");
  my $output = "";

  while ( length($input) and
          $input =~ s/^(.*?)\[\s*([^\]\s]+)\s*([^\]]*)\s*\]//
        ) {
    my ($prefix, $url, $text) = ($1, $2, $3);

    $text = $url unless defined $text;
    $text = escapeHTML($text);

    $prefix = "" unless defined $prefix;

    $output .=
      ( $prefix .
        "<a href='?" . escape($url) . "'>$text</a>"
      );
  }

  $output .= $input if defined $input;

  $state->store($tag => $output);
}

1;
