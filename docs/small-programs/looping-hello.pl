#!/usr/bin/env perl

use warnings;
use strict;
use POE;

POE::Session->create(
	inline_states => {
		_start         => \&say_what,
		say_what_again => \&say_what,
	},
);

POE::Kernel->run();

sub say_what {
	print "what\n";
	$_[KERNEL]->yield("say_what_again");
}
