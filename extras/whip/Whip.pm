# $Id$

# Whip is where the basic stuff goes.

package Whip;

use warnings;
use strict;

use XML::Parser;
use Whip::Tag;
use CGI qw(:standard);
use Whip::State;

my %whip_tag_syntax;

sub WH_DOCROOT () { 0 }
sub WH_PAGE_ID () { 1 }
sub WH_COOKIE  () { 2 }
sub WH_QUERY   () { 3 }
sub WH_USER    () { 4 }

# Create the Whip singleton.  It's not truly a singleton, though,
# because we may have several of them handling requests in a given
# program.

sub new {
  my $class = shift;
  my %param = @_;

  my $query = delete $param{query};
  my $cookie = $query->cookie("whip_uid");

  # If we have a cookie from the browser, then try to load the state
  # for it.  Failure to load a state isn't bad; we'll just create a
  # new one.

  my $user;
  if (defined $cookie and length $cookie) {
    eval {
      $user = Whip::State->thaw($cookie);
    }
  }

  # The user state was loaded from the cookie, so we don't need to
  # create a new cookie.  Otherwise the user state was stale/removed,
  # and we build a new one and a cookie to go with it.

  if (defined $user) {
    undef $cookie;
  }
  else {
    $user   = Whip::State->new({});
    $cookie = $query->cookie( -name => "whip_uid", -value => $user->freeze() );
  }

  my $self = bless
    [ delete $param{docroot},   # WH_DOCROOT
      undef,                    # WH_PAGE_ID
      $cookie,                  # WH_COOKIE
      $query,                   # WH_QUERY
      $user,                    # WH_USER
    ], $class;

  return $self;
}

### Emit a document.

sub emit_document {
  my $self = shift;
  my %param = @_;

  # If we have a cookie, be sure to send it to the browser so the user
  # may be identified later.
  my @cookie;
  if (defined $self->[WH_COOKIE]) {
    push @cookie, -cookie => $self->[WH_COOKIE];
  }

  # This should never happen, but it just might.
  unless (defined $self->[WH_USER]) {
    die "No user";
  }

  # Flush any changes to the user state.
  $self->[WH_USER]->freeze();

  print( header( -status => delete $param{status},
                 @cookie,
               ),
         start_html(delete $param{title}),
         delete $param{body},
         end_html(),
       );
  exit 0;
}

### Throw an error.

sub error {
  my ($self, $status, $title, $body) = @_;
  die [ $status, $title, $body ];
}

### Set syntax for a package.

sub set_syntax {
  my ($self, $pkg, $syntax) = @_;
  $whip_tag_syntax{$pkg} = $syntax;
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
    $self->error( 404, "Page Not Found",
                  "<tt>" . escapeHTML($page_id) .
                  "</tt> is not a valid whip page ID."
                );
  }

  my $package = $1;
  $package =~ tr[a-zA-Z_0-9:][_]cs;

  if ($2 eq "tag") {
    return "Whip::Tag::$package";
  }

  if ($2 eq "do") {
    return "Whip::Action::$package";
  }

  if ($2 eq "form") {
    return "Whip::Form::$package";
  }

  $self->error( 500, "Error Executing Page",
                "<tt>" . escapeHTML($page_id) .
                "</tt> is not executable."
              );
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
    $self->error( 404, "Page Not Found",
                  "The file for <tt>" . escapeHTML($page_id) .
                  "</tt> does not exist."
                );
  }

  unless ($self->cache_outdated($path)) {
    return $page_cache{$path}->[CACHE_DATA];
  }

  unless (open PAGE, $path) {
    $self->error( 500, "Error Loading Page",
                  "The file for <tt>" . escapeHTML($page_id) .
                  "</tt> could not be opened: $!"
                );
  }

  # If page is executable, then load it.
  my $page_data;
  if ($page_id =~ /\.(do|tag|form)$/) {
    require $path;
    $page_data = $self->page_to_package($page_id);

    # Tags have special on-load needs.
    if ($page_id =~ /\.tag$/) {
      $page_data->set_syntax();
    }
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
  my ($self, $param, $parser, $tag, $args) = @_;

  my $page_package = $self->load_page("$tag.tag");

  # Page tag is special.

  if ($tag eq "page") {
    if (@tag_stack) {
      $self->error( 500, "Invalid Whip Content",
                    "<tt>" . escapeHTML("$tag.tag") .
                    "</tt> <tt>&lt;page&gt;</tt> must be the outermost tag."
                  );
    }
  }
#  else {
#    unless (@tag_stack) {
#      $self->error( 500, "Invalid Whip Content",
#                    "<tt>" . escapeHTML("$tag.tag") .
#                    "</tt> <tt>" . escapeHTML("<$tag>") .
#                    "</tt> must be within a &lt;page&gt; tag."
#                  );
#    }
#  }

  push @tag_stack, $page_package->new($self, $tag, $args, $param);
}

# Parser callback for an ending tag.

sub end_element {
  my ($self, $param, $parser, $tag) = @_;

  unless (@tag_stack) {
    $self->error( 500, "Invalid Whip Content",
                  "<tt>" . escapeHTML("</$tag>") .
                  "</tt> has no corresponding <tt>" .
                  escapeHTML("<$tag>") . "</tt>."
                );
  }

  my $open_tag = $tag_stack[-1]->name();
  unless ($tag eq $open_tag) {
    $self->error( 500, "Invalid Whip Content",
                  "<tt>" . escapeHTML("</$tag>") .
                  "</tt> attempts to close <tt>" .
                  escapeHTML("<$open_tag>") . "</tt>."
                );
  }

  # Pop the tag off the stack, validate its data, build a hash of
  # useful parameters, and close the tag with that.

  my $done_tag = pop @tag_stack;

  # Validate parameters, and build a data hash.

  my @data;
  if (exists $whip_tag_syntax{ref($done_tag)}) {
    my @syntax = @{$whip_tag_syntax{ref($done_tag)}};
    while (my ($sub_tag, $flags) = splice(@syntax, 0, 2)) {
      my @default;
      if (ref($flags) eq "ARRAY") {
        ($flags, @default) = @$flags;
      }

      my $legal = 1;
      if ($flags & LIST) {
        my @value = $done_tag->fetch($sub_tag, @default);
        push @data, [@value];
        if ($flags & REQ and !@value) {
          $legal = 0;
          last;
        }
      }
      elsif ($flags & SCALAR) {
        my $value = $done_tag->fetch($sub_tag, @default);
        unless (defined $value) {
          if ($flags & REQ) {
            $legal = 0;
            last;
          }
          $value = "";
        }
        push @data, $value;
      }
      else {
        $self->error( 500, "Invalid Whip Syntax",
                      "<tt>" . escapeHTML("<$tag>") .
                      "</tt> has unknown flags for subtag <tt>" .
                      escapeHTML("<$sub_tag>") . "</tt>."
                    );
      }

      unless ($legal) {
        $self->error( 500, "Invalid Whip Content",
                      "<tt>" . escapeHTML("<$tag>") .
                      "</tt> requires <tt>" .
                      escapeHTML("<$sub_tag>") . "</tt>."
                    );
      }
    }
  }

  # Pass the data to the close tag.
  $done_tag->close(@data);
}

### Give this tag's contents to some container.  Propagates up the
### container thingy.

sub emit {
  my ($self, $type, $value) = @_;
  my $take_method = "take_$type";

  # Give its content to its container.
  my $i = @tag_stack;
  while ($i--) {
    if ($tag_stack[$i]->can($take_method)) {
      $tag_stack[$i]->$take_method($value);
      return;
    }
  }
}

### Parser callback for some random text.

sub text {
  my ($self, $param, $parser, $text) = @_;

  # Ignore all-whitespace text.
  return unless $text =~ /\S/;

  $self->start_element($param, $parser, "text", { text => $text });
  $self->end_element($param, $parser, "text");
}

# Render a page.

sub render_page {
  my ($self, $page_id, $param) = @_;

  unless ($page_id =~ /\.page$/) {
    $self->error( 500, "Error Rendering Page",
                  "<tt>" . escapeHTML($page_id) .
                  "</tt> is not renderable."
                );
  }

  my $parser = XML::Parser->new
    ( Handlers =>
      { Start => sub { $self->start_element($param, @_) },
        End   => sub { $self->end_element($param, @_) },
        Char  => sub { $self->text($param, @_) },
      }
    );

  my $page_data = $self->load_page($page_id);
  $self->[WH_PAGE_ID] = $page_id;
  $parser->parse($page_data);
  undef $self->[WH_PAGE_ID];
}

### Accessor: Get the current page ID.

sub get_page_id {
  my $self = shift;
  return $self->[WH_PAGE_ID];
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

### Submit something.

sub submit_page {
  my ($self, $page_id, $param) = @_;
  my $package_name = $self->load_page($page_id);
  $package_name->submit_form($self, $page_id, $param);
}

1;
