#! /usr/bin/env perl
# vim: ts=2 sw=2 expandtab

# Verify that POE::Wheel::FollowTail does indeed follow a file's tail.

use strict;
use warnings;

use IO::Handle;
use POE qw(Wheel::FollowTail);

use constant TESTS => 10;
use Test::More;

use File::Temp;

# Sanely generate the tempfile
my $write_fh;
eval { $write_fh = File::Temp->new( UNLINK => 1 ) };
plan skip_all => "Unable to create tempfile for testing" if $@;

$write_fh->autoflush(1);
my $write_count = 0;

plan tests => 10;

POE::Session->create(
  inline_states => {
    _start => sub {
      $_[KERNEL]->yield("on_tick");
    },
    on_tick => sub {
      print $write_fh ++$write_count, " ", time(), "\n";
      $_[KERNEL]->delay("on_tick" => 1) if $write_count < TESTS;
    },
  }
);

POE::Session->create(
  inline_states => {
    _start => sub {
      $_[HEAP]{tailor} = POE::Wheel::FollowTail->new(
        Filename     => $write_fh->filename,
        InputEvent   => "got_log_line",
        PollInterval => 3,
      );
      $_[KERNEL]->delay(timeout => 15);
    },
    got_log_line => sub {
      my ($write, $time) = split /\s+/, $_[ARG0];
      my $elapsed = time() - $time;
      ok($elapsed <= 3, "response time <=3 seconds ($elapsed)");
      delete $_[HEAP]{tailor} if $write >= TESTS;
    },
    timeout => sub {
      delete $_[HEAP]{tailor};
    },
  }
);

POE::Kernel->run();

1;
