# -*- perl -*-
# $Id$

# Whip's main entry point.  This code finds the page a user is looking
# for, fetches it, and renders it.  We C<use vars> here so that $req
# is available to other whip files.

package Whip::Handler::main;

use warnings;
use strict;

use CGI qw(:standard);

my %tags =
  ( title  => \&Whip::Tag::from_value,
    status => \&Whip::Tag::from_value,
  );

sub run {
  my ($pkg, $state) = @_;

  my $req = CGI->new();

  my $query = $req->query_string();
  $query = "keywords=index" unless length $query;

  if ( $query =~ /^keywords=(\S+)/ ) {
    my $page = main::load_page("$1.page");

    $state->store(_input => \$page);

    my $new_state = main::render_thing($state, "PAGE", \%tags);

    # auth_type() gets the auth method
    # remote_user() returns the auth user

    #    unless ($req->auth_type()) {
    #      Whip::throw( "401 Not Authenticated",
    #                   "Not Authenticated",
    #                   "Booga."
    #                 )
    #    }

    my $status = $new_state->fetch("status", 200);
    my $title  = $new_state->fetch("title", "Untitled");
    my $html   =
      join( "",
            $new_state->fetch("_output", "No page content.")
          );

    print( header(-status => $status),
           start_html($title),
           $html
         );
    exit 0;
  }

  error( 404, "Page not found",
         "Could not find page <tt>" . encodeHTML($1) . "</tt>"
       );
}

1;
