#!/usr/bin/perl

use warnings;
use strict;

use Whip;

sub DIR_BASE    () { "/home/troc/public_html/whip" }
sub DIR_DOCROOT () { DIR_BASE . "/docroot" }

#------------------------------------------------------------------------------
# Main code.

my $whip = Whip->new( docroot => DIR_DOCROOT );
$whip->execute_page("main.act");

exit 0;
