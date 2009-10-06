#!/usr/bin/perl -w
# vim: ts=2 sw=2 expandtab

# POE::Kernel->run() should return right away if there are no
# sessions.

use strict;

use lib qw(./mylib ../mylib);

sub POE::Kernel::ASSERT_DEFAULT () { 1 }

BEGIN {
  package POE::Kernel;
  use constant TRACE_DEFAULT => exists($INC{'Devel/Cover.pm'});
}

use POE;
use Test::More tests => 1;

{
  my $death_note = "never returned\n";
  local $SIG{ALRM} = sub { die $death_note };
  alarm(10);
  eval { POE::Kernel->run() };
  alarm(0);

  is($@, "", "POE::Kernel->run() returned right away");
}

1;
