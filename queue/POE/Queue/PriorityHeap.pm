# $Id$
# Copyrights and documentation are at the end.

package POE::Queue::PriorityHeap;

use strict;

use constant VALUE => 0;  # The current value node's value.
use constant PRIO  => 0;  # The current priority node's priority.
use constant NEXT  => 1;  # The next priority/value node in the list.
use constant HEAD  => 2;  # The head of the value list at this node.
use constant TAIL  => 3;  # The tail of the value list at this node.

use vars qw(@ISA);
@ISA = qw(POE::Queue);

### Very simple constructor.

sub new {
  my $self;
  return bless \$self;
}

### Add a value to the queue.

sub enqueue {
  my ($self, $prio, $value) = @_;
  my $v;

  # The heap is empty.  Make the heap be the new value.

  unless($$self) {
    $v = [$value];
    $$self =
      [ $prio,  # PRIO
        undef,  # NEXT
        $v,     # HEAD
        $v,     # TAIL
      ];
    return;
  }

  # The new value has the same priority as the root node.  Store the
  # new value at the end of the linked list of values there.

  if($$self->[PRIO] == $prio) {
    $$self->[TAIL]->[NEXT] = [$value];
    $$self->[TAIL] = $$self->[TAIL]->[NEXT];
    return;
  }

  # The new value has a higher priority than the root node.  Walk the
  # heap until we find the proper place to put the new value.

  if($$self->[PRIO] < $prio) {
    my $p = $$self;  # Reference to the current node.
    my $o = $p;      # Old node (last one visited).

    # Walk through priorities until we find the appropriate place.

    while($p) {

      # The new priority is before the reference's.  Add this value
      # between the reference and the last value seen.

      if($p->[PRIO] > $prio) {
        $v = [$value];
        $o->[NEXT] =
          [ $prio,       # PRIO
            $o->[NEXT],  # NEXT
            $v,          # HEAD
            $v,          # TAIL
          ];
        last;
      }

      # If the new priority is the same as the reference node's, then
      # we add this value to the end of the list of valuess at the
      # priority.

      if($p->[PRIO] == $prio) {
        $p->[TAIL]->[NEXT] = [$value];   # Next value of last value.
        $p->[TAIL] = $p->[TAIL]->[NEXT]; # Last value of this node.
        last;
      }

      # If there's no place left to walk, then we add the new value at
      # the end of the path.

      unless($p->[NEXT]) {
        $v = [$value];
        $p->[NEXT] =
          [ $prio, # PRIO
            undef, # NEXT
            $v,    # HEAD
            $v,    # TAIL
          ];
        last;
      }

      # Otherwise continue to walk.

      $o = $p;
      $p = $p->[NEXT];
    }
    return;
  }

  # The new value comes before the root node.  Make the new value the
  # new root node.

  if($$self->[PRIO] > $prio) {
    $v = [$value];
    $$self =
      [ $prio,  # PRIO
        $$self, # NEXT
        $v,     # HEAD
        $v,     # TAIL
      ];
  }

  else {
    die;
  }
}

### Remove the next value from the queue.  The "next" value is the
### oldest one with the lowest priority.

sub dequeue {
  my $self = shift;

  # Special case: The queue is empty.

  return undef unless($$self);

  # The value to return.

  my $v = $$self->[HEAD];

  # If the value is the head of a list, then remove it.  Otherwise
  # remove the node.

  if($v->[NEXT]) {
    $$self->[HEAD] = $v->[NEXT];
  } elsif($$self->[NEXT]) {
    $$self = $$self->[NEXT];
  } else {
    $$self = undef;
  }

  # Return the value's value.

  return $v->[VALUE];
}

### Remove everything in the queue that has a priority at or before a
### specified one.

sub dequeue_through {
  my ($self,$prio) = @_;

  # Special case: The queue is empty.

  return [] unless $$self;

  # Walk the queue, dequeuing everything that counts.

  my @retval;

  while ($$self and $$self->[PRIO] <= $prio) {
    my $value = $$self->[HEAD];
    while ($value) {
      push @retval, $value->[VALUE];
      my $old_value = $value->[NEXT];
      $value = $value->[NEXT];
      undef $old_value->[NEXT];
    }
    $$self = $$self->[NEXT];
  }

  return \@retval;
}

### Return the next priority in the queue, or undef if the queue is
### empty.

sub get_next_priority {
  my $self = shift;
  return undef unless $$self;
  $$self->[PRIO];
}

### Remove everything from the queue that matches the next priority in
### the queue.

sub dequeue_next_priority {
  my $self = shift;

  # Special case: The queue is empty.

  return [] unless $$self;

  # Return everything in the next priority.  Walk the linked list that
  # HEAD heads.

  my @retval;

  my $value = $$self->[HEAD];
  while ($value) {
    push @retval, $value->[VALUE];
    my $old_value = $value;
    $value = $value->[NEXT];
    undef $old_value->[NEXT];
  }

  $$self = $$self->[NEXT];
  return \@retval;
}

### Remove things from the queue.  A coderef is supplied, and it will
### be called for everything in the queue, and things that it matches
### will be removed.

sub remove_items {
  my($self, $cref) = @_;

  my $p = $$self;

  while($p) {
    my $v = $p->[HEAD];

    my $ov;  # The old (last seen) value in the chain.

    while ($v) {

      # If the function returns false for this value, then it must be
      # removed.

      unless ($cref->($v->[VALUE])) {

        # If this value is at the head of the list for the priority,
        # then, move the head reference to the next value.

        if ($p->[HEAD] == $v) {
          $p->[HEAD] = $v->[NEXT];
        }

        # If there is an old value, its NEXT reference should skip the
        # removed value.  If we've removed the last item from the
        # value list, then fix the tail reference in the node.

        if ($ov) {
          $ov->[NEXT] = $v->[NEXT];

          # Fix the tail reference.

          if ($p->[TAIL] == $v) {
            $p->[TAIL] = $ov;
            last;
          }

          # The value pointer is the old value's next.

          $v = $ov->[NEXT];
          next;
        }
      }

      # The old value becomes the current value, and the current value
      # becomes the next one.

      $ov = $v;
      $v = $v->[NEXT];
    }

    # Move to the next priority in the queue.

    $p = $p->[NEXT];
  }
}

1;

__END__

=head1 NAME

POE::Queue::PriorityHeap - a priority heap implementation for POE::Queue

=head1 SYNOPSIS

To do.

=head1 DESCRIPTION

To do.

=head1 SEE ALSO

To do.

=head1 BUGS

To do.

=head1 AUTHORS & COPYRIGHT

POE::Queue::PriorityHeap is contributed by Artur Bergman.

Please see L<POE> for more information about authors and contributors.

=cut
