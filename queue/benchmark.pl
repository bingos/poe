#!/usr/bin/perl

use warnings;
use strict;

$|=1;

use POE::Queue;

# The sequence length should be at least as many items as there are
# priorities.

sub MAX_PRIORITIES  () { 200 }
sub SEQUENCE_LENGTH () { 5000 }

die if SEQUENCE_LENGTH < MAX_PRIORITIES;

# Fisher-Yates shuffle them, for extra yummy randomness.  Use srand
# with the same seed each time so every @seq list represents different
# lengths of the same "random" sequence.

my @seq;
sub build_list {
  my $priorities = shift;
  my $factor = SEQUENCE_LENGTH / $priorities;

  @seq = map { [ int($_ / $factor), $_ ] } (0..(SEQUENCE_LENGTH-1));

  { srand(1);
    my $i = @seq;
    while (--$i) {
      my $j = int rand($i+1);
      @seq[$i,$j] = @seq[$j,$i];
    }
  }
}

# Run through the list for a number of benchmarks.  Each benchmark has
# a different number of priorities.

for my $priorities (1..MAX_PRIORITIES) {

  build_list($priorities);

  # One for each queue implementation.
  for my $impl (qw(Array PriorityHeap)) {

    my $queue = POE::Queue->new($impl);

    ### Plain enqueue/dequeue.

    my ($begin_usr, $begin_sys) = (times)[0,1];
    $queue->enqueue(@$_) for @seq;
    my ($cease_usr, $cease_sys) = (times)[0,1];

    my $elapsed = ($cease_usr - $begin_usr) + ($cease_sys - $begin_sys);

    print( join( "\t",
                 $priorities,
                 $impl, "enqueue-plain",
                 $elapsed/SEQUENCE_LENGTH, # Time per operation.
               ),
           "\n"
         );

    ($begin_usr, $begin_sys) = (times)[0,1];
    1 while $queue->dequeue;
    ($cease_usr, $cease_sys) = (times)[0,1];

    $elapsed = ($cease_usr - $begin_usr) + ($cease_sys - $begin_sys);

    print( join( "\t",
                 $priorities,
                 $impl, "dequeue-plain",
                 $elapsed/SEQUENCE_LENGTH, # Time per operation.
               ),
           "\n"
         );

    ### Next-priority enqueue/dequeue.  The enqueue is actually just a
    ### plain one, but we get to see the effect of internal data
    ### structure freeing tradeoffs.

    ($begin_usr, $begin_sys) = (times)[0,1];
    $queue->enqueue(@$_) for @seq;
    ($cease_usr, $cease_sys) = (times)[0,1];

    $elapsed = ($cease_usr - $begin_usr) + ($cease_sys - $begin_sys);

    print( join( "\t",
                 $priorities,
                 $impl, "enqueue-np",
                 $elapsed/SEQUENCE_LENGTH, # Time per operation.
               ),
           "\n"
         );

    ($begin_usr, $begin_sys) = (times)[0,1];
    1 while scalar(@{$queue->dequeue_next_priority});
    ($cease_usr, $cease_sys) = (times)[0,1];

    $elapsed = ($cease_usr - $begin_usr) + ($cease_sys - $begin_sys);

    print( join( "\t",
                 $priorities,
                 $impl, "dequeue-np",
                 $elapsed/SEQUENCE_LENGTH, # Time per operation.
               ),
           "\n"
         );
  }
}
