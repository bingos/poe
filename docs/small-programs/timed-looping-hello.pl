#!/usr/bin/env perl

use warnings;
use strict;
use POE;

sub start_saying {
  my ($what, $delay) = @_;

  my $say_it = sub {
    print "$what\n";
    $_[KERNEL]->delay(say_it_again => $delay);
  };

  POE::Session->create(
    inline_states => {
      _start       => $say_it,
      say_it_again => $say_it,
    },
  );
}

start_saying("hello", 1);
start_saying("  world", 1.5);

POE::Kernel->run();
