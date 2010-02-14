#! /usr/bin/env perl
# vim: ts=2 sw=2 expandtab

# Verify that POE::Wheel::FollowTail does indeed follow a file's tail.

use strict;
use warnings;

use IO::Handle;
use POE qw(Wheel::FollowTail);

use constant TESTS => 10;
use Test::More;

my $tailfile = "/tmp/powh-followtail-test-$$";
my $write_count = 0;
my $write_fh;

open $write_fh, ">", $tailfile or plan(
	skip_all => "can't write to temporary file $tailfile: $!"
);
$write_fh->autoflush(1);

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
        Filename     => $tailfile,
        InputEvent   => "got_log_line",
				PollInterval => 3,
      );
			$_[KERNEL]->delay(timeout => 11);
    },
    got_log_line => sub {
			my ($write, $time) = split /\s+/, $_[ARG0];
			ok((time() - $time) < 3, "response time <3 seconds");
			delete $_[HEAP]{tailor} if $write >= TESTS;
    },
		timeout => sub {
			delete $_[HEAP]{tailor};
		},
  }
);

POE::Kernel->run();
unlink $tailfile;
