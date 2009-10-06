#!/usr/bin/perl
# vim: ts=2 sw=2 expandtab

# Tests whether POE::Kernel affects signal handlers at initialization
# time.  Based on test code provided by Stuart Kendrick, in
# rt.cpan.org ticket 19529.

use warnings;
use strict;

# perl-5.6.x on Win32 does not support alarm()
BEGIN {
  if ( $^O eq 'MSWin32' and $] < 5.008 ) {
    print "1..0 # Skip perl-5.6.x on $^O does not support alarm()";
    exit();
  }
}

use Test::More tests => 1;

BEGIN {
  $SIG{ALRM} = \&dispatch_normal_signal;
}

my $signal_dispatched = 0;

sub dispatch_normal_signal { $signal_dispatched = 1 }

use POE;

alarm(1);

if ($^O eq "MSWin32") {
	# Cant' select. Windows will get me!
	# Windows has trouble with select() and undefined input vectors.
	sleep(5);
}
else {
	# Can't sleep. HP-UX will get me!
	# HP-UX implements sleep() with alarm(), so they don't mix.
	select(undef, undef, undef, 5);
}

ok($signal_dispatched, "normal SIGALRM dispatched");

1;
