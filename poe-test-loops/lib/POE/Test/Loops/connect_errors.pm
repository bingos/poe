#!/usr/bin/perl -w
# $Id$

# POE::XS::Loop::Poll wasn't handling errors correctly, this was
# particularly noticable for connect() failures, so check connection
# failures are handled correctly

use strict;

BEGIN {
  unless (-f "run_network_tests") {
    print "1..0 # Skip Network access (and permission) required to run this test\n";
    CORE::exit();
  }
}

use Test::More tests => 1;

sub POE::Kernel::ASSERT_DEFAULT () { 1 }
sub POE::Kernel::TRACE_DEFAULT  () { 1 }
sub POE::Kernel::TRACE_FILENAME () { "./test-output.err" }

use POE qw( Wheel::ReadWrite Component::Client::TCP );

# Dynamically find an unused port for the failure-to-connect test.

my $unused_port;
{
	use IO::Socket::INET;
	my $reserved = IO::Socket::INET->new(
		LocalAddr => '127.0.0.1',
		LocalPort => 0,
		ReuseAddr => 0,
	);
	$unused_port = (sockaddr_in(getsockname($reserved)))[0];
}

# Timeout.

POE::Session->create(
	inline_states => {
    _start => sub {
      $poe_kernel->alias_set('watcher');
      $_[HEAP]{alarm} = $poe_kernel->alarm_set(timeout => time() + 10);
    },
    timeout => sub {
      $poe_kernel->post(client => 'shutdown');
      fail("timeout for connection");
    },
    shutdown => sub {
      $poe_kernel->alarm_remove($_[HEAP]{alarm});
    },
  }
);

# Test connection failure.

POE::Component::Client::TCP->new(
  RemotePort => $unused_port,
  RemoteAddress => '127.0.0.1',
  Alias => 'client',
  Connected => sub {
    fail("should have failed to connect");
  },
  ConnectError => sub {
    $poe_kernel->post(watcher => 'shutdown');
    pass("expected connection failure occurred");
  },
  ServerInput => sub {
    warn "ServerInput called unexpectedly\n";
  },
);

# Run the tests.

POE::Kernel->run();

1;
