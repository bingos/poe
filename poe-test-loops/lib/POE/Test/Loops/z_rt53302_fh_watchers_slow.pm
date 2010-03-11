#!/usr/bin/perl -w
# vim: ts=2 sw=2 expandtab

# Rocco Caputo noticed this bug in POE::Loop::Glib v0.037.
# LotR wanted this converted into a test in PTL so we can
# verify the bug is gone and help other loop authors :)

# TODO do we need a way to timeout the test?

use strict;

BEGIN {
  unless (-f "run_network_tests") {
    print "1..0 # Skip Network access (and permission) required to run this test\n";
    CORE::exit();
  }
}

sub POE::Kernel::ASSERT_DEFAULT () { 1 }
#sub POE::Kernel::TRACE_FILES () { 1 }

BEGIN {
  eval "sub POE::Kernel::TRACE_DEFAULT () { 1 }" if (
    exists $INC{'Devel/Cover.pm'}
  );
}

use Test::More;
plan tests => 8;

use POE qw( Component::Server::TCP Component::Client::TCP );
use Socket qw( sockaddr_in );

my $num_clients = 5;

# testing variables
my $num_server_connects = 0;
my $num_server_disconnects = 0;
my $num_server_inputs = 0;
my $num_server_flushes = 0;
my $acceptor_port;

my $num_client_connects = 0;
my $num_client_disconnects = 0;
my $num_client_inputs = 0;
my $num_client_flushes = 0;

# Spawn the TCP server.
POE::Component::Server::TCP->new(
  Alias => 'server',
  Address => 'localhost',
  Port => 0,
  Started => sub {
    $acceptor_port = (
      sockaddr_in($_[HEAP]->{listener}->getsockname())
    )[0];
  },

  ClientConnected => sub { $num_server_connects++ },

  ClientInput => sub {
    $num_server_inputs++;

    $_[HEAP]->{client}->put( 'from server' );
    $_[KERNEL]->yield( 'shutdown' );
  },

  ClientFlushed => sub { $num_server_flushes++ },

  ClientDisconnected => sub {
    $num_server_disconnects++;

    # end the test after N clients is done
    if ( $num_server_disconnects >= $num_clients ) {
      $_[KERNEL]->call( 'server', 'shutdown' );
    }
  },
);

# spawn the client
for ( 1 .. $num_clients ) {
  POE::Component::Client::TCP->new(
    RemoteAddress => 'localhost',
    RemotePort => $acceptor_port,
    ConnectTimeout => 2,

    Connected => sub {
      $num_client_connects++;

      $_[HEAP]->{server}->put( 'from client' );
    },
    Disconnected => sub { $num_client_disconnects++ },

    ServerInput => sub {
      $num_client_inputs++;

      $_[KERNEL]->delay( 'shutdown' => 1 );
    },
    ServerError => sub {},
    ServerFlushed => sub { $num_client_flushes++ },
  );
}

$poe_kernel->run();

# Okay, make sure we processed N connections
is( $num_server_connects, $num_clients, "Server got $num_clients client connections" );
is( $num_server_disconnects, $num_clients, "Server got $num_clients client disconnections" );
is( $num_server_inputs, $num_clients, "Client sent input $num_clients times" );
is( $num_server_flushes, $num_clients, "Server flushed $num_clients lines of data" );

is( $num_client_connects, $num_clients, "Client connected $num_clients times" );
is( $num_client_disconnects, $num_clients, "Client disconnected $num_clients times" );
is( $num_client_inputs, $num_clients, "Server sent input $num_clients times" );
is( $num_client_flushes, $num_clients, "Client flushed $num_clients lines of data" );

1;

