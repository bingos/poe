# $Id$

# Wrapper for a whip request/response transaction.

package Whip::State;

use warnings;
use strict;
use Carp qw(croak);

sub STATE_PARENT () { 0 }
sub STATE_VALUES () { 1 }

### Create an initial state.

sub new {
  my ($class, $parent_state) = @_;
  my $self = bless
    [ $parent_state,  # STATE_PARENT
      {},             # STATE_VALUES
    ], $class;
  return $self;
}

### Return the values hash from this state.

sub get_values {
  my $self = shift;
  return %{$self->[STATE_VALUES]};
}

### Absorb another state into this one.

sub absorb {
  my ($self, $other_state) = @_;

  my %other_state = $other_state->get_values();
  while (my ($attribute, $value) = each %other_state) {
    $self->store($attribute, $value);
  }
}

### Store a value into a state.

sub store {
  my $self = shift;

  while (@_ >= 2) {
    my $attribute = lc(shift);
    my $value = shift;

    my @value;
    if (ref($value) eq "ARRAY") {
      @value = @$value;
    }
    else {
      @value = $value;
    }

    unless (exists $self->[STATE_VALUES]->{$attribute}) {
      $self->[STATE_VALUES]->{$attribute} = [ ];
    }

    push @{$self->[STATE_VALUES]->{$attribute}}, @value;
  }

  croak "Whip::State->store() called with an odd number of parameters" if @_;
}

### Remove a value and return it.

sub delete {
  my ($self, $attribute) = @_;
  my $value = delete $self->[STATE_VALUES]->{lc($attribute)};
  return unless $value;

  if (wantarray) {
    return @$value;
  }
  return $value->[0];
}

### Fetch a scalar, possibly inheriting it from elsewhere.

sub fetch {
  my ($self, $attribute, @default) = @_;
  $attribute = lc($attribute);

  if (exists $self->[STATE_VALUES]->{$attribute}) {
    if (wantarray) {
      return @{$self->[STATE_VALUES]->{$attribute}};
    }
    return $self->[STATE_VALUES]->{$attribute}->[0];
  }

  if (defined $self->[STATE_PARENT]) {
    if (wantarray) {
      my @return = $self->[STATE_PARENT]->fetch($attribute);
      return @return;
    }
    my $return = $self->[STATE_PARENT]->fetch($attribute);
    return $return;
  }

  return @default;
}

### Rename _value to something else.

sub rename_value {
  my ($self, $new_name) = @_;
  $new_name = lc($new_name);
  $self->[STATE_VALUES]->{$new_name} = delete $self->[STATE_VALUES]->{_value};
}

1;
