#!/usr/bin/perl -w -I..
# $Id$

# This is a fake login prompt I wrote after noticing that someone's
# IRC 'bot was probing telnet whenever I joined a particular channel.
# It wasn't originally going to be a POE test, but it turns out to be
# a good exercise for wheel event renaming.

use strict;
use IO::Socket;

use POE qw(Wheel::SocketFactory Wheel::ReadWrite Driver::SysRW Filter::Line);

#==============================================================================
# This is the login state group.

#------------------------------------------------------------------------------
# Enter the "login" prompt state.  Prompt user, and wait for input.

sub login_login_start {
  my ($session, $heap) = @_[SESSION, HEAP];

  print "$session - entering login state\n";
                                        # switch the output filter to stream
  # -><- code
                                        # switch the input event to login_input
  $heap->{'wheel'}->event( InputState => 'login_input' );
                                        # display the prompt
  $heap->{'wheel'}->put('login: ');
}

sub login_login_input {
  my ($kernel, $session, $heap, $input) = @_[KERNEL, SESSION, HEAP, ARG0];

  print "$session - received login input\n";

  if ($input ne '') {
    $kernel->yield('password_start');
  }
  else {
    $kernel->yield('login_start');
  }
}

#==============================================================================
# This is the password state group.

sub login_password_start {
  my ($session, $heap) = @_[SESSION, HEAP];

  print "$session - entering password state\n";

                                        # switch output filter to stream
  # -><- code
                                        # switch input event to password_input
  $heap->{'wheel'}->event( InputState => 'password_input' );
                                        # display the prompt
  $heap->{'wheel'}->put('Password:');
}

sub login_password_input {
  my ($kernel, $session, $heap, $input) = @_[KERNEL, SESSION, HEAP, ARG0];

  print "$session - received password input\n";

                                        # switch output filter to line
  # -><- code
                                        # display the response
  $heap->{'wheel'}->put('Login incorrect');
                                        # move to the login state
  $kernel->yield('login_start');
}

sub login_error {
  my ($heap, $operation, $errnum, $errstr) = @_[HEAP, ARG0, ARG1, ARG2];

  print "login: $operation error $errnum: $errstr\n";

  delete $heap->{'wheel'};
}

#==============================================================================
# This is the main entry point for the login session.

sub login_session_start {
  my ($kernel, $session, $heap, $handle, $peer_addr, $peer_port) =
    @_[KERNEL, SESSION, HEAP, ARG0, ARG1, ARG2];

  print "$session - received connection\n";

                                        # start reading and writing
  $heap->{'wheel'} = new POE::Wheel::ReadWrite
    ( 'Handle'     => $handle,
      'Driver'     => new POE::Driver::SysRW,
      'Filter'     => new POE::Filter::Line,
      'ErrorState' => 'error',
    );
                                        # hello, world!\n
  $heap->{'wheel'}->put('FreeBSD (localhost) (ttyp2)', '', '');
  $kernel->yield('login_start');
}

sub login_session_create {
  my ($handle, $peer_addr, $peer_port) = @_[ARG0, ARG1, ARG2];

  new POE::Session( _start => \&login_session_start,
                                        # start parameters
                    [ $handle, $peer_addr, $peer_port],
                                        # general error handler
                    error => \&login_error,
                                        # login prompt states
                    login_start => \&login_login_start,
                    login_input => \&login_login_input,
                                        # password prompt states
                    password_start => \&login_password_start,
                    password_input => \&login_password_input
                  );
  undef;
}

#==============================================================================

package main;

my $port = shift || 23;

new POE::Session
  ( '_start' => sub
    { my $heap = $_[HEAP];

      $heap->{'wheel'} = new POE::Wheel::SocketFactory
        ( BindPort       => $port,
          SuccessState   => 'socket_ok',
          FailureState   => 'socket_error',
          Reuse          => 'yes',
        );
    },

    'socket_error' => sub
    { my ($heap, $operation, $errnum, $errstr) = @_[HEAP, ARG0, ARG1, ARG2];
      print "listener: $operation error $errnum: $errstr\n";
    },

    'socket_ok' => \&login_session_create,
  );

$poe_kernel->run();
      
__END__
