#!/usr/bin/perl -w
# vim: ts=2 sw=2 expandtab

# This test simply dumps some debug info to the console

use strict;

sub POE::Kernel::ASSERT_DEFAULT () { 1 }

BEGIN {
  eval "sub POE::Kernel::TRACE_DEFAULT () { 1 }" if (
    exists $INC{'Devel/Cover.pm'}
  );
}

use Test::More;
plan tests => 2;

use_ok( "POE" );
use_ok( "POE::Test::Loops" );

# idea from Test::Harness, thanks!
diag(
  "Testing POE $POE::VERSION, ",
  "POE::Test::Loops $POE::Test::Loops::VERSION, ",
  "Using Loop(",
    $POE::Kernel::poe_kernel->poe_kernel_loop(),
  "), Perl $], ",
  "$^X on $^O"
);

# TODO <@dngor> If it can glean the loop from the test generator, it could compare them to make sure they match.
# This would require parsing the "=for poe_tests" block and trying to extract the loop out of it...

1;

