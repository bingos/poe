# $Id$

# Whip is where the basic stuff goes.

package Whip;

use warnings;
use strict;

use XML::Parser;
use Whip::Tag;

sub WH_DOCROOT () { 0 }

# Create the Whip singleton.  It's not truly a singleton, though,
# because we may have several of them handling requests in a given
# program.

sub new {
  my $class = shift;
  my %param = @_;

  my $self = bless
    [ delete $param{docroot},   # WH_DOCROOT
    ], $class;

  return $self;
}

### Manage a page cache.

sub CACHE_DATA () { 0 }
sub CACHE_AGE  () { 1 }

my %page_cache;

# Translate a page ID into an absolute path, via the docroot.

sub absolute_path {
  my ($self, $page_id) = @_;

  my $path = $self->[WH_DOCROOT] . "/$page_id";
  $path =~ s{/\.+/}{/}g;
  $path =~ s{^\.+/}{/};

  return $path;
}

# Translate a page ID into a perl package name.

sub page_to_package {
  my ($self, $page_id) = @_;
  unless ($page_id =~ /^(.+?)\.([^\.]+)$/) {
    die "$page_id is not a valid page ID";
  }

  if ($2 eq "tag") {
    return "Whip::Tag::$1";
  }

  if ($2 eq "act") {
    return "Whip::Action::$1";
  }

  die "$page_id is not a known executable page type";
}

# Determine if the data for a page ID is stale.

sub cache_outdated {
  my ($self, $path) = @_;
  my $page_age = -M $path;
  if ( exists($page_cache{$path}) and
       $page_cache{$path}->[CACHE_AGE] <= $page_age
     ) {
    return 0;
  }
  return 1;
}

# Load a page, or return a cached page if it's still fresh.  We use
# $held_self for import() routines, which cannot accept $self as a
# parameter.

my $held_self;

sub load_page {
  my ($self, $page_id) = @_;

  # Whip::Tag's import can't refer to this object as itself, so it
  # calls load_page by package instead.  This if/else saves $self when
  # called by object, and restores $self when called by package.

  if ($self eq __PACKAGE__) {
    $self = $held_self;
  }
  else {
    $held_self = $self;
  }

  my $path = $self->absolute_path($page_id);

  unless (-e $path) {
    die "404 page $path not found";
  }

  unless ($self->cache_outdated($path)) {
    return $page_cache{$path}->[CACHE_DATA];
  }

  unless (open PAGE, $path) {
    die "500 error loading page";
  }

  # If page is executable, then load it.
  my $page_data;
  if ($page_id =~ /\.(act|tag)$/) {
    require $path;
    $page_data = $self->page_to_package($page_id);
  }
  else {
    local $/;
    $page_data = <PAGE>;
    close PAGE;
  }

  $page_cache{$path} =
    [ $page_data,  # CACHE_DATA
      -M $path,    # CACHE_AGE
    ];

  return $page_data;
}

### XML parser and tag stack.

my @tag_stack;

# Parser callback for a beginning tag.

sub start_element {
  my ($self, $parser, $tag, $args) = @_;

  my $page_package = $self->load_page("$tag.tag");

  # Page tag is special.

  if ($tag eq "page") {
    die "<page> must be outermost tag" if @tag_stack;
  }
  else {
    unless (@tag_stack) {
      die "<$tag> must be within a page";
    }

    # See if the tag's legal.
    unless ($tag_stack[-1]->can_contain($tag)) {
      my $tag_container = $tag_stack[-1]->name();
      die "<$tag> is not part of <$tag_container>";
    }
  }

  push @tag_stack, $page_package->new($self, $tag, $args);
}

# Parser callback for an ending tag.

sub end_element {
  my ($self, $parser, $tag) = @_;

  unless (@tag_stack) {
    die "</$tag> has no corresponding <$tag>";
  }

  my $open_tag = $tag_stack[-1]->name();
  unless ($tag eq $open_tag) {
    die "</$tag> attempts to close <$tag>";
  }

  # Close the tag, and pop it off the stack.
  $tag_stack[-1]->close($self);
  my $done_tag = pop @tag_stack;

  # Give its content to its container.
  if (@tag_stack) {
    my @contents = $done_tag->get_contents();
    $tag_stack[-1]->set_contents(@contents);
  }
}

# Parser callback for some random text.

sub text {
  my ($self, $parser, $text) = @_;

  # Ignore all-whitespace text.
  return unless $text =~ /\S/;

  $self->start_element($parser, "text", { text => $text });
  $self->end_element($parser, "text");
}

# Render a page.

sub render {
  my ($self, $page_id) = @_;

  die unless $page_id =~ /\.page$/;

  my $parser = XML::Parser->new
    ( Handlers =>
      { Start => sub { $self->start_element(@_) },
        End   => sub { $self->end_element(@_) },
        Char  => sub { $self->text(@_) },
      }
    );

  my $page_data = $self->load_page($page_id);
  $parser->parse($page_data);
}

### Execute a page to parse some $data.  Expects $page to be a
### document name, $args is a hashref of attributes for the tag that
### triggered the execution, and $data is a reference to the remainder
### of the page being rendered.  Returns ($html, $state), which are
### HTML and state variables that will be assimilated by the parent
### thing.

sub execute_page {
  my ($self, $page_id) = @_;
  my $package_name = $self->load_page($page_id);
  $package_name->run($self);
}


1;
