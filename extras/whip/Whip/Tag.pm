# $Id$

# Whip::Tag is what all the whip tag handlers inherit from.  It
# supplies basic features for parsing and rendering tags.

package Whip::Tag;

use warnings;
use strict;

use Whip::Attribute;

sub TAG_NAME    () { 0 }
sub TAG_DATA    () { 1 }
sub TAG_SUBTAGS () { 2 }
sub TAG_WHIP    () { 3 }

sub ZERO   () { 0x00 }
sub ONE    () { 0x01 }
sub MANY   () { 0x02 }

sub QMARK () { ZERO | ONE }
sub STAR  () { ZERO | ONE | MANY }
sub PLUS  () { ONE | MANY }

use vars qw($whip_self);

# Handle inheritance and base class loading via the C<use> line.

sub import {
  my ($class, $base_class) = @_;

  my $caller_package = (caller)[0];
  foreach (qw(ZERO ONE MANY QMARK STAR PLUS)) {
    no strict 'refs';
    *{"$caller_package\::$_"} = \&{"$class\::$_"};
  }

  if (defined $base_class) {
    my $base_package = Whip->load_page("$base_class.tag");
    eval "package $caller_package; use base qw($base_package)";
    die if $@;
    undef $whip_self;
  }
}

# Create a new whip tag.

sub new {
  my ($class, $whip, $tag_name, $tag_data) = @_;

  my $self = bless [], $class;
  $self->[TAG_NAME]    = $tag_name;
  $self->[TAG_DATA]    = [ ];
  $self->[TAG_SUBTAGS] = { };
  $self->[TAG_WHIP]    = $whip;

  while (my ($name, $val) = each %$tag_data) {
    $self->set_contents( Whip::Attribute->new($name, $val) );
  }

  # Load the tag.
  $self->open();

  return $self;
}

# Determine whether a tag can contain another tag.

sub can_contain {
  my ($self, $child_tag) = @_;
  return 1 if exists $self->[TAG_SUBTAGS]->{$child_tag};

  foreach (keys %{$self->[TAG_SUBTAGS]}) {
    return 1 if $self->isa("Whip::Tag::$_");
  }
}

# Set the subtags for this tag.  Subtags are tags that this tag can
# contain.

sub set_subtags {
  my ($self, $sub_tags) = @_;
  $self->[TAG_SUBTAGS] = $sub_tags;
}

# Accessor: Return the name of the tag.

sub name {
  my $self = shift;
  return $self->[TAG_NAME];
}

# Virtual base methods: Open and close the tag.

sub open  { }
sub close { }

# Set the tag's contents.  Contents are data fields.

sub set_contents {
  my ($self, @contents) = @_;
  push @{$self->[TAG_DATA]}, @contents;
}

# Get the tag's contents as a list.

sub get_contents {
  my $self = shift;
  return @{$self->[TAG_DATA]};
}

# Get the tag's contents as a hash.  The list is flattened out.

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
      push @{$contents{$name}}, $value;
    }
    else {
      $contents{$name} = $value;
    }
  }
  return %contents;
}

# Fetch a single value from a tag.  In scalar context, the last value
# for an attribute name is returned.  In list context, all the values
# for the name are returned.

sub fetch {
  my ($self, $target_name, @default) = @_;
  my @value;

  foreach (@{$self->[TAG_DATA]}) {
    my $name = $_->name();
    next unless "Whip::Tag::$name"->isa("Whip::Tag::$target_name");
    push @value, $_->value();
  }

  @value = @default unless @value;
  return @value if wantarray;
  return $value[-1] if @value;
  return;
}

# Replace the contents of the tag with a new set of values.

sub replace_contents {
  my $self = shift;
  $self->[TAG_DATA] = [ ];
  while (my ($name, $value) = splice(@_, 0, 2)) {
    push @{$self->[TAG_DATA]}, Whip::Attribute->new($name, $value);
  }
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
