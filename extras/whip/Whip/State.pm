# $Id$

# Wrapper for a whip request/response transaction.

package Whip::State;

use warnings;
use strict;
use Carp qw(croak);
use YAML qw(Load Store);
use Digest::SHA1 qw(sha1_hex);
use Time::HiRes;
use Fcntl qw(:flock);
use Symbol qw(gensym);
use CGI qw(escapeHTML);

sub STATE_PARENT () { 0 }
sub STATE_VALUES () { 1 }
sub STATE_ID     () { 2 }

### Static functions to lock and unlock resources.  They should be
### moved into main or a general-purpose Whip class when other things
### need to do locking later.

my %locks;

sub _lock {
  my $resource = shift;
  my $lock_file = main::DIR_LOCK . "/$resource";

  if (exists $locks{$lock_file}) {
    main::error( 500,
                 "500 Attempt To Double Lock",
                 "Could not lock file <tt>" . escapeHTML($lock_file) .
                 "</tt> because it already is locked."
               );
  }

  my $lock_fh = gensym();
  unless (open $lock_fh, ">", $lock_file) {
    main::error( 500,
                 "500 Could Not Open Lock",
                 "Could not open lock file <tt>" . escapeHTML($lock_file) .
                 "</tt>: $!"
               );
  }

  unless (flock($lock_fh, LOCK_EX)) {
    main::error( 500,
                 "500 Could Not Acquire Lock",
                 "Could not acquire lock on <tt>" .
                 escapeHTML($lock_file) . "</tt>: $!"
               );
  }

  $locks{$lock_file} = $lock_fh;
}

sub _unlock {
  my $resource = shift;
  my $lock_file = main::DIR_LOCK . "/$resource";

  my $lock_fh = delete $locks{$lock_file};
  unless (defined $lock_fh) {
    main:error( 500,
                "500 Attempt To Unlock Unlocked Resource",
                "Could not unlock <tt>" . escapeHTML($lock_file) .
                "</tt> because it already is unlocked."
              );
  }

  unless (flock($lock_fh, LOCK_UN)) {
    main::error( 500,
                 "500 Could Not Release Lock",
                 "Could not release lock on <tt>" .
                 escapeHTML($lock_file) . "</tt>: $!"
               );
  }

  close $lock_fh;
}

### Create an initial state.

sub new {
  my ($class, $parent_state) = @_;
  my $self = bless
    [ $parent_state,  # STATE_PARENT
      {},             # STATE_VALUES
      undef,          # STATE_ID
    ], $class;
  return $self;
}

### Store a state into a file.  Return the state's unique ID.

sub freeze {
  my $self = shift;

  # Lock the state directory.
  _lock("state");

  # Create a new state ID if we don't have one.
  my $id = $self->[STATE_ID];
  my $state_path = &main::DIR_STATE;
  my $state_file;
  unless (defined $id) {
    while (1) {
      $id = sha1_hex(Time::HiRes::time() . "-$$-" . rand());
      $state_file = "$state_path/$id";
      last unless -e $state_file;
    }
    $self->[STATE_ID] = $id;
  }

  # Store the state there.
  unless (open(STATE, ">", $state_file)) {
    _unlock("state");
    main::error( 500,
                 "500 Error Saving State",
                 "Could not save state in <tt>" . escapeHTML($state_file) .
                 "</tt>: $!"
               );
  }

  print STATE Store($self);
  close STATE;

  # Unlock the state directory.
  _unlock("state");

  return $id;
}

### Fetch a state from a file.

sub thaw {
  my ($class, $id) = @_;

  # Lock the state directory.
  _lock("state");

  # Load and thaw a state.
  my $state_file = &main::DIR_STATE . "/" . $id;
  unless (open(STATE, "<", $state_file)) {
    _unlock("state");
    main::error( 500,
                 "500 Error Loading State",
                 "Could not load state from <tt>" . escapeHTML($state_file) .
                 "</tt>: $!"
               );
  }

  local $/;
  my $self = Load scalar <STATE>;
  close STATE;

  _unlock("state");

  die unless ref($self) eq __PACKAGE__;
  return $self;
}

### Destroy a state.  Removes its file.

sub destroy {
  my $self = shift;
  unless (defined $self->[STATE_ID]) {
    main::error( 500,
                 "500 Error Destroying State",
                 "Could not destroy non-existent state."
               );
  }

  my $state_file = &main::DIR_STATE . "/" . $self->[STATE_ID];
  _lock("state");
  my $unlink_status = unlink($state_file);
  _unlock("state");

  unless (unlink $state_file) {
    main::error( 500,
                 "500 Error Destroying State",
                 "Could not destroy state in <tt>" . escapeHTML($state_file) .
                 "</tt>: $!"
               );
  }
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
