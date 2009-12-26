#!/usr/bin/perl -w
# vim: ts=2 sw=2 expandtab

# POE::XS::Loop::Poll wasn't handling errors correctly, this was
# particularly noticable for connect() failures, so check connection
# failures are handled correctly

use strict;

use Test::More;

unless (-f "run_network_tests") {
  plan skip_all => "Network access (and permission) required to run this test";
}

# MSWin32+ActiveState 5.6.1 and 5.10.1 always time out.  And if we remove the
# delay, then the OS never times out.  5.8.0 seems to work fine.  Since this
# behavior seems to come and go, we're skipping it for all versions of MSWin32.
if ($^O eq 'MSWin32') {
  plan skip_all => "This test fails for various versions of MSWin32 perl";
}

plan tests => 3;

sub POE::Kernel::ASSERT_DEFAULT () { 1 }

BEGIN {
  package POE::Kernel;
  use constant TRACE_DEFAULT => exists($INC{'Devel/Cover.pm'});
}

use POE qw( Wheel::ReadWrite Component::Client::TCP );

# Dynamically find an unused port for the failure-to-connect test.
# Listen on the port, but accept no connections there.

my $unused_port;
{
  use IO::Socket::INET;
  my $reserved = IO::Socket::INET->new(
    LocalAddr => '127.0.0.1',
    ReuseAddr => 0,
  );
  if (defined $reserved) {
    $unused_port = (sockaddr_in(getsockname($reserved)))[0];
    pass("found unused port: $unused_port");
  } else {
    fail("found unused port error: $@");
  }
}

# Timeout.

POE::Session->create(
  inline_states => {
    _start => sub {
      $poe_kernel->alias_set('watcher');
      $_[HEAP]{alarm} = $poe_kernel->delay_set(timeout => 10);
    },
    timeout => sub {
      $poe_kernel->post(client => 'shutdown');
      fail("timeout for connection");
    },
    shutdown => sub {
      $poe_kernel->alarm_remove($_[HEAP]{alarm});
    },
    _stop => sub { }, # Pacify assertions.
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

pass("run() returned successfully");

1;
