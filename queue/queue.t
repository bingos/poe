# $Id$

# Various basic queue tests.

use Test::More tests => 1072;

use strict;

my $implementation = $ENV{POE_QUEUE};
$implementation  = shift  unless $implementation;
$implementation = "Array" unless $implementation;

use_ok("POE::Queue");
$|++;

print "# Using $implementation implementation\n";

my $queue = POE::Queue->new($implementation);

isa_ok($queue, 'POE::Queue');
isa_ok($queue, "POE::Queue::$implementation");

is($queue->dequeue, undef, "The queue should be empty");
is($queue->get_next_priority, undef, "There should be no priority");
is_deeply($queue->dequeue_next_priority, [], "Check that deqeue is empty");
is_deeply($queue->dequeue_through, [], "Check that deqeueu throught is empty");

# Test edge case one, empty queue

{
    $queue->enqueue(1,"hej1");
    is($queue->dequeue(), "hej1", "Check that it returns what we want");
    is($queue->dequeue, undef, "And now we are empty");
}

# Test edge case where item belongs at the end of queue, two versions

{
    $queue->enqueue(1,"hej1");
    $queue->enqueue(1,"hej2");
    is($queue->dequeue, "hej1", "First object, check FIFO Order");
    is($queue->dequeue, "hej2", "Second object, check FIFO order");
    is($queue->dequeue, undef, "And now we are empty");

    $queue->enqueue(1,"hej1");
    $queue->enqueue(2,"hej2");
    is($queue->dequeue, "hej1", "First object, check FIFO Order");
    is($queue->dequeue, "hej2", "Second object, check FIFO order");
    is($queue->dequeue, undef, "And now we are empty");

}

# Edge case, beginning of queue

{
    $queue->enqueue(2,"hej2");
    $queue->enqueue(1,"hej1");
    is($queue->dequeue, "hej1", "First object, check FIFO Order");
    is($queue->dequeue, "hej2", "Second object, check FIFO order");
    is($queue->dequeue, undef, "And now we are empty");
}

# Edge case, contains two items, we put it in the middle

{
    $queue->enqueue(1,"hej1");
    $queue->enqueue(3,"hej3");
    $queue->enqueue(2,"hej2");
    is($queue->dequeue, "hej1");
    is($queue->dequeue, "hej2");
    is($queue->dequeue, "hej3");
    is($queue->dequeue, undef, "And now we are empty");
}

# Test a lot of items, inserted out of order and dequeued in order.

{
  for my $item (1..5) {
    for my $prio (qw(2 1 5 3 4)) {
      $queue->enqueue($prio, "$prio-$item");
    }
  }
  for my $prio (1..5) {
    for my $item (1..5) {
      is($queue->dequeue, "$prio-$item", "Check that we return correctly");
    }
  }
  is($queue->dequeue, undef, "And now we are empty");
}

print "# Test get_next_priority\n";

{
    $queue->enqueue(2,"hej2");
    is($queue->get_next_priority, 2, "Heighest prio is 2");
    $queue->enqueue(3,"hej3");
    is($queue->get_next_priority, 2, "Heighest prio is still 2");
    $queue->enqueue(1,"hej1");
    is($queue->get_next_priority, 1, "And now it is 1");
    $queue->enqueue(2,"hej2-2");
    is($queue->get_next_priority, 1, "And it should still be 1");

    is_deeply($queue->dequeue_through(1), ["hej1"]);
    is_deeply($queue->dequeue_through(1), []);
    is($queue->get_next_priority, 2, "Now it should be 2");
    is_deeply($queue->dequeue_through(4), ['hej2','hej2-2','hej3']);
}

{
    print "Test dequeue_next_priority()\n";
    $queue->enqueue(2,"hej2");
    $queue->enqueue(2,"hej2-2");
    $queue->enqueue(1,"hej1");
    $queue->enqueue(1,"hej1-2");
    $queue->enqueue(3,"hej3");
    $queue->enqueue(2,"hej2-3");
    is_deeply($queue->dequeue_next_priority, ['hej1','hej1-2']);
    is_deeply($queue->dequeue_next_priority, ['hej2','hej2-2','hej2-3']);
    is_deeply($queue->dequeue_next_priority, ['hej3']);
    is_deeply($queue->dequeue_next_priority, []);
}

sub removal {
    return 0 if($_[0]=~/\Ad/);
    return 1;
}

{
    print "Test removal!\n";

    $queue->enqueue(10,"dtest1");
    $queue->enqueue(10,"test2");
    $queue->remove_items(\&removal);
    is($queue->dequeue, 'test2');
    is($queue->dequeue, undef);

    $queue->enqueue(10,"test2");
    $queue->enqueue(10,"dtest1");
    $queue->remove_items(\&removal);
    is($queue->dequeue, 'test2');
    is($queue->dequeue, undef);

    $queue->enqueue(10,"dtest1");
    $queue->enqueue(10,"test1");
    $queue->enqueue(10,"dtest2");
    $queue->remove_items(\&removal);
    is_deeply($queue->dequeue_through(10), ['test1']);

    $queue->enqueue(10,"test1");
    $queue->enqueue(10,"dtest3");
    $queue->enqueue(11,"test2");
    $queue->enqueue(9,"dtest2");
    $queue->enqueue(8,"test3");
    $queue->enqueue(7,"dtest1");
    $queue->enqueue(12,"dtest4");
    $queue->enqueue(10,"test4");
    $queue->remove_items(\&removal);
    is_deeply($queue->dequeue_through(12), ['test3','test1','test4','test2']);

    $queue->enqueue(10,"dtest");
    $queue->enqueue(11,"test");
    $queue->remove_items(\&removal);
    is_deeply($queue->dequeue_through(12), ['test']);

    $queue->enqueue(10,'dtest1');
    $queue->enqueue(10,'dtest2');
    $queue->enqueue(11,'test');
    $queue->remove_items(\&removal);
    is_deeply($queue->dequeue_through(12), ['test']);

    $queue->enqueue(10,'test1');
    $queue->enqueue(10,'dtest');
    $queue->enqueue(10,'dtest');
    $queue->enqueue(10,'test2');
    $queue->remove_items(\&removal);
    is_deeply($queue->dequeue_through(12), ['test1', 'test2']);

    $queue->enqueue(10,'dtest');
    $queue->enqueue(9,'dtest');
    $queue->enqueue(11,'test');
    $queue->remove_items(\&removal);
    is_deeply($queue->dequeue_through(12), ['test']);

    $queue->enqueue(10,'hi');
    is_deeply($queue->dequeue_through(10), ['hi']);
}

print "# larger test case to check ordering\n";

{
    for my $prio (qw(20 18 16 14 12 10 1 3 5 7 9 19 17 15 13 11 2 4 6 8)) {
	for my $item (1..50) {
	    $queue->enqueue($prio, "$prio-$item");
	}
    }
    for my $prio (1..20) {
	for my $item (1..50) {
	    is( $queue->dequeue, "$prio-$item",
                "Check that we return correctly"
              );
	}
    }
    is($queue->dequeue, undef, "And now we are empty");
}
