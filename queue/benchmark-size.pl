#!/usr/bin/perl

use warnings;
use strict;

$|=1;

use lib ".";
use POE::Queue;

# The sequence length should be at least as many items as there are
# priorities.

sub MAX_SEQ_LENGTH  () { 800 }

# Fisher-Yates shuffle them, for extra yummy randomness.  Use srand
# with the same seed each time so every @seq list represents different
# lengths of the same "random" sequence.

my @seq;
sub build_list {
  my $priorities = shift;

  @seq = map { [ $_, $_ ] } (0..($priorities-1));

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

for my $priorities (1..MAX_SEQ_LENGTH) {

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
                 $elapsed/$priorities, # Time per operation.
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
                 $elapsed/$priorities, # Time per operation.
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
                 $elapsed/$priorities, # Time per operation.
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
                 $elapsed/$priorities, # Time per operation.
               ),
           "\n"
         );
  }
}
