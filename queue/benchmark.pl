#!/usr/bin/perl

use warnings;
use strict;

srand(1);

use Time::HiRes qw(time);

use POE::Queue;

#create random sequence
for my $int (1..100) {
    my @seq;
    for(1..5000) {
	my $prio = int(rand($int));
	push(@seq,[$prio, $_]);
    }

    for my $impl (qw(Array PriorityHeap)) {
	my $queue = POE::Queue->new($impl);
	my $start_time = time();
	my $i = 0;
	for(@seq) {
	    $queue->enqueue(@$_);
	}
	my $end_time = time();
	my $time = $end_time - $start_time;

        print join("\t", $int, $impl, "enqueue 1", $time), "\n";
	
	$start_time = time();
	while($queue->dequeue) { $i++ };
	$end_time = time();
	$time = $end_time - $start_time;

        print join("\t", $int, $impl, "dequeue", $time), "\n";

        $start_time = time();
	$i = 0;
	for(@seq) {
	    $queue->enqueue(@$_);
	}
	$end_time = time();
        $time = $end_time - $start_time;

        print join("\t", $int, $impl, "enqueue 2", $time), "\n";

	$i = 0;
	$start_time = time();
	while(scalar @{$queue->dequeue_next_priority}) { $i++ };

	$end_time = time();
	$time = $end_time - $start_time;

        print join("\t", $int, $impl, "dequeue np", $time), "\n";
    }
}
