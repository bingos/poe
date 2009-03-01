#!/usr/bin/perl -w
# $Id$

# POE::XS::Loop::Poll wasn't handling errors correctly, this was
# particularly noticable for connect() failures, so check connection
# failures are handled correctly

use strict;

use Test::More;

unless (-f "run_network_tests") {
  plan skip_all => "Network access (and permission) required to run this test";
}

# to work around an issue on MSWin32+ActiveState 5.6.1
# it will always timeout via our alarm, and if we remove it - the OS never times out!
if ($^O eq 'MSWin32' and $] < 5.008) {
  plan skip_all => "This test always fails on MSWin32+perl older than 5.8.0";
}

plan tests => 3;

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
    #LocalPort => 0,    # 0 is the default, and as a bonus this works on MSWin32+ActiveState 5.6.1
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

pass("run() returned successfully");

1;
