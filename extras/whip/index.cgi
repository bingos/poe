#!/usr/bin/perl

use warnings;
use strict;

sub DIR_BASE    () { "/home/troc/public_html/whip" }
sub DIR_DOCROOT () { DIR_BASE . "/docroot" }
sub DIR_LOCK    () { DIR_BASE . "/lock"    }
sub DIR_STATE   () { DIR_BASE . "/state"   }
sub DIR_USER    () { DIR_BASE . "/user"    }
use Whip;

#------------------------------------------------------------------------------
# Main code.

use CGI;
my $query = new CGI;

eval {
  my $whip = Whip->new( docroot => DIR_DOCROOT,
                        query   => $query,
                      );
  $whip->execute_page("main.do");
};

if ($@) {
  if (ref($@) eq "ARRAY") {
    my ($status, $title, $body) = @{$@};
    print( header(-status => $status),
           start_html("$status $title"),
           "<h1>$title</h1><p>$body</p>",
           end_html(),
         );
    exit 0;
  }

  my $error = $@; $error = escapeHTML($error);
  print( header(-status => 500),
         start_html("Error 500"),
         "<h1>Generic Server Error</h1><p><pre>$error</pre></p>",
         end_html(),
       );
  exit 0;
}

print( header(-status => 500),
       start_html("500 Internal Whip Error"),
       "<h1>Internal Whip Error</h1>",
       "<p>Main whip renderer did not exit when it was done.</p>",
       end_html(),
     );

exit 0;
