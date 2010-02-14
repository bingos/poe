#!/usr/bin/perl
# vim: ts=2 sw=2 expandtab

use warnings;
use strict;

use Test::More;

if ($^O eq "MSWin32" and not $ENV{POE_DANTIC}) {
  plan skip_all => "Sorry Perl crashes on $^O";
}

plan tests => 14;

my $port;

use POE;
use POE::Wheel::Run;

SKIP: {
  skip("The underlying event loop has trouble with ptys on $^O", 6)
  if $^O eq "darwin" and (
    exists $INC{"POE/Loop/IO_Poll.pm"} or
    exists $INC{"POE/Loop/Event.pm"} or
    $ENV{POE_LOOP_USES_POLL}
  ) and not $ENV{POE_DANTIC};

  eval "use IO::Pty";
  skip("IO::Pty is not available; skipping pty tests", 6) if $@;

  PoeTestWorker->spawn( 'pty' );
  PoeTestWorker->spawn( 'pty-pipe' );
}

PoeTestWorker->spawn( 'socketpair' );
PoeTestWorker->spawn( 'inet' );

pass( "Start" );

$poe_kernel->run;

pass( "Done" );


#############################################################################
package PoeTestWorker;

use strict;
use warnings;

use POE;
use Test::More;

sub DEBUG () { 0 }

sub seen
{
  my( $heap, $what ) = @_;
  $heap->{seen}{$what}++;
  DEBUG and diag "$$: seen $what\n";
  if( 3==keys %{$heap->{seen}} ) {
    delete $heap->{wheel};
    $poe_kernel->alarm_remove( delete $heap->{tid} ) if $heap->{tid};
  }
}


sub spawn 
{
  my( $package, $conduit ) = @_;
  POE::Session->create(
    args => [ $conduit ],
    inline_states => {
      _start => sub {
        my( $heap, $kernel, $conduit ) = @_[ HEAP, KERNEL, ARG0 ];
        $heap->{conduit} = $conduit;
        $heap->{seen} = {};
        $kernel->sig_child( TERM => 'TERM' );

        $heap->{wheel} = POE::Wheel::Run->new(
          StderrEvent => (
            $conduit eq 'pty' ? undef() : 'stderr'
          ),
          StdoutEvent => 'stdout',
          #ErrorEvent  => 'error',
          CloseEvent  => 'closeE',
          Conduit     => $conduit,
          Program     => sub {
            print "hello\n";
            sleep 1;
            print "hello world" x 1024, "\n";
            print "done\n";
          }
        );
        $kernel->sig_child( $heap->{wheel}->PID, 'CHLD' );
        $heap->{tid} = $kernel->delay_set( timeout => 600 );
      },
      _stop => sub {
        my( $heap, $kernel ) = @_[ HEAP, KERNEL ];
        ## This is the money shot
        foreach my $need ( qw( done close CHLD ) ) {
          is( $heap->{seen}{$need}, 1, "$heap->{conduit}: $need" );
        }
      },
      timeout => sub {
        my( $heap, $kernel ) = @_[ HEAP, KERNEL ];
        $poe_kernel->alarm_remove( delete $heap->{tid} ) if $heap->{tid};
        delete $heap->{wheel};
        delete $heap->{tid};
      },
      TERM => sub {
        my( $heap, $kernel ) = @_[ HEAP, KERNEL ];
        $poe_kernel->alarm_remove( delete $heap->{tid} ) if $heap->{tid};
        delete $heap->{wheel};
        $kernel->sig_handled;
      },
      closeE => sub {
        my( $heap, $kernel ) = @_[ HEAP, KERNEL ];
        seen( $heap, 'close' );
      },
      CHLD => sub {
        my( $heap, $kernel ) = @_[ HEAP, KERNEL ];
        seen( $heap, 'CHLD' );
        $kernel->sig_handled;
      },
      stdout => sub {
        my( $heap, $kernel, $line, $wid ) = @_[ HEAP, KERNEL, ARG0..$#_ ];
        seen( $heap, 'done' ) if $line eq 'done';
      },
      stderr => sub {
        my( $heap, $kernel, $line, $wid ) = @_[ HEAP, KERNEL, ARG0..$#_ ];
        warn "ERROR [$$]: $line\n";
        seen( $heap, 'error' );
        $poe_kernel->alarm_remove( delete $heap->{tid} ) if $heap->{tid};
      },
    }
  );
}

1;
