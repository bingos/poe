#!/usr/bin/perl
# $Id$

use warnings;
use strict;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use Text::Template;
use Symbol qw(delete_package);

sub DIR_BASE    () { "/home/troc/public_html/whip" }
sub URL_BASE    () { "http://poe.dyndns.org/~troc/whip" }
sub DIR_DOCROOT () { DIR_BASE . "/docroot" }
sub PAGE_MAIN   () { "main.do" }

use Whip::State;
use Whip::Tag;

### Fetch and execute the main page.  It will take over from here.  If
### the main page has a problem executing, or some sub-page has thrown
### an error, display a default oops or something.

my $dummy_input = "";
my $root_state = Whip::State->new();
$root_state->store
  ( _input  => \$dummy_input,
    _output => "",
  );

eval { execute_page($root_state, PAGE_MAIN, {}) };
catch();

print( header(-status => 500),
       start_html("Error 500"),
       "Main whip renderer did not exit when it was done"
     );
exit 0;

### Throw an error.  It will be caught and rendered by the main eval.

sub error {
  my ($status, $title, $body) = @_;
  die [ $status, $title, $body ];
}

### Catch an error and format it for the browser.  Exits if an error
### was caught; otherwise it returns having done nothing.

sub catch {
  if ($@) {
    if (ref($@) eq "ARRAY") {
      my ($status, $title, $body) = @{$@};
      print header(-status => $status), start_html($title), $body;
      exit 0;
    }

    my $error = $@; $error = escapeHTML($error);
    print( header(-status => 500),
           start_html("Error 500"),
           "Generic error:<br><pre>$error</pre",
         );
    exit 0;
  }
}

### Helper to fix a path from a page ID.

sub absolute_path {
  my $page_id = shift;

  my $path = DIR_DOCROOT . "/$page_id";
  $path =~ s{/\.+/}{/}g;
  $path =~ s{^\.+/}{/};

  return $path;
}

### Load a page.

my %page_cache;
sub CACHE_DATA () { 0 }
sub CACHE_AGE  () { 1 }

sub cache_outdated {
  my $path = shift;
  my $page_age = -M $path;
  if ( exists($page_cache{$path}) and
       $page_cache{$path}->[CACHE_AGE] <= $page_age
     ) {
    return 0;
  }
  return 1;
}

sub load_page {
  my $page = shift;

  my $path = absolute_path($page);

  unless (-e $path) {
    error( 404,
           "404 Page Not Found",
           "The page <tt>" . escapeHTML($page) . "</tt> does not exist."
         );
  }

  unless (cache_outdated($path)) {
    return $page_cache{$path}->[CACHE_DATA];
  }

  unless (open PAGE, $path) {
    error( 500, "500 Error Loading Page",
           "The page <tt>" . escapeHTML($page) .
           "</tt> could not be loaded: " . escapeHTML($!)
         );
  }

  local $/;
  my $page_data;
  $page_data = <PAGE>;
  close PAGE;

  $page_cache{$path} =
    [ $page_data,  # CACHE_DATA
      -M $path,    # CACHE_AGE
    ];

  return $page_data;
}

### Execute a page to parse some $data.  Expects $page to be a
### document name, $args is a hashref of attributes for the tag that
### triggered the execution, and $data is a reference to the remainder
### of the page being rendered.  Returns ($html, $state), which are
### HTML and state variables that will be assimilated by the parent
### thing.

sub execute_page {
  my ($state, $page, $args) = @_;
  my $new_state = Whip::State->new($state);
  $new_state->store(%$args);

  # Transform page ID into a package.
  my $package;
  if ($page =~ /^(.+)\.(do|tag)$/) {
    $package = "Whip::Handler::$1" if $2 eq "do";
    $package = "Whip::Tag::$1"     if $2 eq "tag";
  }
  else {
    error( "403 Forbidden", "Not permitted to execute $page",
           "Page <tt>$page</tt> is not executable."
         );
  }

  my $path = absolute_path($page);
  require $path;

#
#  if (cache_outdated($path)) {
#    delete_package($package);
#    my $code = load_page($page);
#    eval $code;
#    catch();
#  }

  $package->run($new_state);
}

### Render a thing.  Expects $open_tag, which is the tag that started
### the thing (and will end it); $args is a hashref of attributes for
### the opening tag; and $data is a reference to the remainder of the
### page being rendered.

sub render_thing {
  my ($state, $open_tag, $tags) = @_;
  my $new_state = Whip::State->new($state);

  my $data = $new_state->fetch("_input");
  my $last_data;

  # Render the data into HTML while there still is some data to
  # render, and while there are tags that need closing.

  while (length($$data)) {

    # Bail out if the data hasn't changed.

    if (defined($last_data) and ($last_data eq $$data)) {
      error( 500, "Render bailed out",
             "Error rendering <tt>" . escapeHTML($open_tag) .
             "</tt>: Could not transform page"
           );
    }

    $last_data = $$data;

    # Discard comments.

    if ($$data =~ s/^\s*\<\!--[^>]*--\>//) {
      next;
    }

    # This tag is a closer.  Verify that it's ours.

    if ($$data =~ s/^\s*(\<\s*\/\s*\Q$open_tag\E\s*\>)//) {
      return $new_state;
    }

    # Handle the next tag in the data.

    if ($$data =~ s/^\s*(\<\s*([^<>\s]+)\s*(.*?)\s*(\/)?\s*\>)//) {
      my ($err_tag, $tag, $att, $single) = ($1, lc($2), $3, $4);
      $att = "" unless defined $att and length $att;

      # Transform the attributes into a state.

      my %args;
      if (defined $att) {
        while ($att =~ s/(\S+)\s*=\s*([\"\'])(.*?)\2//) {
          $args{lc($1)} = $3;
        }
        while ($att =~ s/(\S+)\s*=\s*(\S+)//) {
          $args{lc($1)} = $2;
        }
        if ($att =~ /\S/) {
          error( 500, "Ill-formed tag",
                 "Syntax error in tag <tt>" . escapeHTML($err_tag) .
                 "</tt> in <tt>" . escapeHTML($open_tag) . "</tt>"
               );
        }
      }

      # If this is a whip tag, execute the renderer with the remainder
      # of the page.  The renderer may change the page.

      if ($tag =~ /^whip\.(\S+)$/) {
        if (defined $single) {
          error( 500, "Whip tags must open regions",
                 "Tag <tt>" . escapeHTML($err_tag) . "</tt> in <tt>" .
                 escapeHTML($open_tag) . "</tt> is a self-closing whip tag"
               );
        }

        my $child_state = execute_page($new_state, lc($1) . ".tag", \%args);

        $new_state->absorb($child_state);
        next;
      }

      # This tag opens something we know.  Call recursively, and
      # absorb the child state.

      if (exists $tags->{$tag}) {
        my $rendered_state = render_thing($new_state, $tag, {});
        $tags->{$tag}->($rendered_state, $tag);
        $new_state->absorb($rendered_state);
        next;
      }

      # Otherwise we don't know what to do.

      error( 500, "Unknown tag",
             "Unknown tag <tt>" . escapeHTML($err_tag) .
             "</tt> in <tt>" . escapeHTML($open_tag) . "</tt>"
           );
    }

    # There's non-tag stuff here.  Add it to the internal _value
    # attribute.

    if ($$data =~ s/^\s*([^<]+)\s*//) {
      $new_state->store(_value => $1);
      next;
    }

    # Otherwise we don't know what to do.

    error( 500, "Unknown data",
           "Unknown data in <tt>" . escapeHTML($open_tag) .
           "</tt>:<br><pre>" . escapeHTML($$data) . "</pre>"
         );
  }

  if ($open_tag ne "PAGE") {
    error( 500, "Unclosed tag",
           "Tag <tt>" . escapeHTML($open_tag) .
           "</tt> has no closer:<br><pre>" . escapeHTML($$data) . "</pre>"
         );
  }

  return $new_state;
}
