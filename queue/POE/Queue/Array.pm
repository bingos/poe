# $Id$
# Copyrights and documentation are at the end.

package POE::Queue::Array;

use strict;

use vars qw(@ISA);
@ISA = qw(POE::Queue);

use constant PRIO  => 0;
use constant VALUE => 1;

sub LARGE_QUEUE_SIZE () { 512 }


### Very simple constructor.

sub new {
  return bless [];
}

### Add a value to the queue.

sub enqueue {
  my ($self, $prio, $value) = @_;

  my $event =
    [ $prio,   # PRIO
      $value,  # VALUE
    ];

  # Special case: No events in the queue.  Put the new event in the
  # queue, and be done with it.

  unless (@$self) {
    $self->[0] = $event;
    return;
  }

  # Special case: New event belongs at the end of the queue.  Push it,
  # and be done with it.

  if ($prio >= $self->[-1]->[PRIO]) {
    push @$self, $event;
    return;
  }

  # Special case: New event comes before earliest event.  Unshift it,
  # and be done with it.

  if ($prio < $self->[0]->[PRIO]) {
    unshift @$self, $event;
    return;
  }

  # Special case: Two events in the queue.  The new event enters
  # between them, because it's not before the first one or after the
  # last one.

  if (@$self == 2) {
    splice @$self, 1, 0, $event;
    return;
  }

  # Small queue.  Perform a reverse linear search on the assumption
  # that (a) a linear search is fast enough on small queues; and (b)
  # most events will be posted for "now" or some future time, which
  # tends to be towards the end of the queue.

  if (@$self < LARGE_QUEUE_SIZE) {
    my $index = @$self;
    $index--
      while ( $index and
              $prio < $self->[$index-1]->[PRIO]
            );
    splice @$self, $index, 0, $event;
    return;
  }

  # And finally, we have this large queue, and the program has already
  # wasted enough time.  -><- It would be neat for POE to determine
  # the break-even point between "large" and "small" event queues at
  # start-up and tune itself accordingly.

  my $upper = @$self - 1;
  my $lower = 0;
  while ('true') {
    my $midpoint = ($upper + $lower) >> 1;

    # Upper and lower bounds crossed.  No match; insert at the lower
    # bound point.

    if ($upper < $lower) {
      splice @$self, $lower, 0, $event;
      return;
    }

    # The key at the midpoint is too high.  The element just below the
    # midpoint becomes the new upper bound.

    if ($prio < $self->[$midpoint]->[PRIO]) {
      $upper = $midpoint - 1;
      next;
    }

    # The key at the midpoint is too low.  The element just above the
    # midpoint becomes the new lower bound.

    if ($prio > $self->[$midpoint]->[PRIO]) {
      $lower = $midpoint + 1;
      next;
    }

    # The key matches the one at the midpoint.  Scan towards higher
    # keys until the midpoint points to an element with a higher key.
    # Insert the new event before it.

    $midpoint++
      while ( ($midpoint < @$self)
              and ($prio == $self->[$midpoint]->[PRIO])
            );
    splice @$self, $midpoint, 0, $event;
    return;
  }

  die;
}

### Remove the next value from the queue.  The "next" value is the
### oldest one with the lowest priority.

sub dequeue {
  my $self = shift;
  return undef unless @$self;
  return shift(@$self)->[VALUE];
}

### Remove everything in the queue that has a priority at or before a
### specified one.

sub dequeue_through {
  my ($self, $prio) = @_;

  my $search = 0;
  $search++ while ($search < @$self and $self->[$search]->[PRIO] <= $prio);

  return [ map { $_->[VALUE] } splice(@$self, 0, $search) ];
}

### Return the next priority in the queue, or undef if the queue is
### empty.

sub get_next_priority {
  my $self = shift;
  return undef unless @$self;
  return $self->[0]->[PRIO];
}

### Remove everything from the queue that matches the next priority in
### the queue.

sub dequeue_next_priority {
  my $self = shift;
  return [] unless @$self;

  my $prio = $self->[0]->[PRIO];
  my $search = 0;
  $search++ while ($search < @$self and $self->[$search]->[PRIO] <= $prio);

  return [ map { $_->[VALUE] } splice(@$self, 0, $search) ];
}

### Remove things from the queue.  A coderef is supplied, and it will
### be called for everything in the queue, and things that it matches
### will be removed.

sub remove_items {
  my ($self, $cref) = @_;

  my $i = @$self;
  while ($i--) {
    splice(@$self, $i, 1) unless $cref->($self->[$i]->[VALUE]);
  }
}

1;

__END__

=head1 NAME

POE::Queue::Array - an array implementation for POE::Queue

=head1 SYNOPSIS

To do.

=head1 DESCRIPTION

To do.

=head1 SEE ALSO

To do.

=head1 BUGS

To do.

=head1 AUTHORS & COPYRIGHT

POE::Queue::Array is contributed by Artur Bergman.

Please see L<POE> for more information about authors and contributors.

=cut
