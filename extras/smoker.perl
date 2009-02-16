# smoker.perl - Smoking is good, mmmkay
#
# Author - Chris 'BinGOs' Williams
#
# This module may be used, modified, and distributed under the same
# terms as Perl itself. Please see the license that came with your Perl
# distribution for details.
#

use strict;
use warnings;
use Config;
use Cwd;
use File::Basename;
use Getopt::Long;
use POE qw(Wheel::Run);
use LWP::UserAgent;

my $make = ( $^O eq 'MSWin32' ? 'nmake.exe' : 'make' );
my $perl = ( $^O eq 'MSWin32' ? 'perl.exe' : '/usr/bin/perl' );
my $pasteurl = 'http://nopaste.snit.ch';
my $channel = '#poe';
my $name = 'POlEsmoker';
my $working = getcwd();
my $result = fileparse($working);
my $help;
my $verbose = 0;

GetOptions ("workdir=s" => \$working,
	    "make=s"    => \$make,
	    "perl=s"	=> \$perl,
	    "name=s"    => \$name,
	    "url=s"	=> \$pasteurl,
	    "channel=s" => \$channel,
	    "help"	=> \$help,
	    "verbose"   => \$verbose,
	    "result=s"  => \$result );

if ( $help ) {
  print "Help is available using 'perldoc -F $0'\n";
  exit 0;
}

print "Using the following settings:\n";
print "Make program      = $make\n";
print "Perl executable   = $perl\n";
print "working directory = $working\n";
print "Paste URL         = $pasteurl\n";
print "Name for paste    = $name\n";
print "Channel for paste = $channel\n";
print "Result string     = $result\n";
print "Pod tests will be run\n" if $ENV{POE_TEST_POD};

$pasteurl .= ( ( $pasteurl !~ m,/$, ) ? '/' : '' ) . 'paste';

POE::Session->create(
  package_states => [
	'main' => [qw(_start _stop _output _wheel_error _wheel_close sig_chld process _response)],
  ],
  options => { trace => 0 },
);

$poe_kernel->run();
exit 0;

sub sig_chld {
  my ($kernel,$heap,$thing,$pid,$status) = @_[KERNEL,HEAP,ARG0,ARG1,ARG2];
  my $processed = delete $heap->{processing}->{ $pid };
  return $poe_kernel->sig_handled() unless $processed;
  print STDOUT "Cmd: ", join(' ', @{ $processed }), " Status: $status\n";
  $heap->{status} = $status unless $status == 0;
  $poe_kernel->sig_handled();
}

sub _start {
  my ($kernel,$heap) = @_[KERNEL,HEAP];
  $kernel->alias_set("Smoker");
  chdir $working or die "Couldn\'t chdir to $working : $!\n";
  $heap->{status} = 0;
  $heap->{output} = [ ];
  $heap->{todo} = [ [ "$perl Makefile.PL", '--default' ],
		    [ $make ], [ $make, 'test' ], [ $make, 'distclean' ], ];
  $heap->{processing} = { };
  #$kernel->sig( CHLD => 'sig_chld' );
  $poe_kernel->yield( 'process' );
  undef;
}

sub process {
  my ($kernel,$heap) = @_[KERNEL,HEAP];
  my $todo = shift @{ $heap->{todo} };
  unless ( $todo ) {
	my %formdata = ( channel => $channel, nick => $name, summary => "Results of $result smoke (" . $Config{archname} . "): " . ( $heap->{status} ? 'Problem with tests' : 'All tests successful' ), paste => join( "\n", @{ $heap->{output} }, "\n\n", Config::myconfig() ) );
	my $ua = LWP::UserAgent->new;
	$ua->env_proxy;
	my $response = $ua->post( $pasteurl, \%formdata );
	print STDOUT $response->status_line, "\n";
	#$kernel->sig( 'CHLD' );
  	return;
  }
  my $cmd = shift @{ $todo };
  my $wheel = POE::Wheel::Run->new(
	Program => $cmd,
	ProgramArgs => $todo,
	StdoutEvent => '_output',
	StderrEvent => '_output',
	ErrorEvent => '_wheel_error',
        CloseEvent => '_wheel_close',
  );
  if ( $wheel ) {
    my $wheel_pid = $wheel->PID();
    $heap->{wheels}->{ $wheel->ID() } = $wheel;
    $heap->{processing}->{ $wheel_pid } = [ $cmd, @{ $todo } ];
    $kernel->sig_child( $wheel_pid, 'sig_chld' );
  }
  undef;
}

sub _stop {
  print STDOUT $_, "\n" for @{ $_[HEAP]->{output} };
  print STDOUT "Something went wrong\n" if $_[HEAP]->{status};
  undef;
}

sub _output {
  push @{ $_[HEAP]->{output} }, $_[ARG0];
  print $_[ARG0], "\n" if $verbose;
  undef;
}

sub _wheel_error {
  my ($heap,$wheel_id) = @_[HEAP,ARG3];
  delete $heap->{wheels}->{ $wheel_id };
  $poe_kernel->yield( 'process' );
  undef;
}

sub _wheel_close {
  my ($heap,$wheel_id) = @_[HEAP,ARG0];
  delete $heap->{wheels}->{ $wheel_id };
  undef;
}

sub _response {
  my ($kernel,$heap) = @_[KERNEL,HEAP];
  my ($request, $response, $entry) = @{$_[ARG1]};
  print STDOUT $response -> status_line;
  $kernel->alias_remove($_) for $kernel->alias_list();
  $kernel->post (useragent => 'shutdown');
  undef;
}

__END__

=head1 NAME

smoker.perl - a small POE script for 'smoke' testing.

=head1 SYNOPSIS

  smoker.perl --workdir /home/foo/svnpoe/ --result 'svn POE' \
  --name "Foo" --channel '#poe' --url "http://paste.scsys.co.uk" \
  --make /usr/bin/make --perl /usr/bin/perl

=head1 DESCRIPTION

smoker.perl is a POE based script ( naturally ) that was originally intended to 'smoke' test the POE svn trunk
and report the results using a pastebot.

It can be used to test any module distribution.

=head1 REQUIRED MODULES

This script requires:

  POE >= 0.35
  LWP::UserAgent

=head1 COMMAND LINE PARAMETERS

smoker.perl uses L<Getopt::Long>, the following command line parameters are supported:

=over

=item --workdir

The working directory to use where the distribution to be tested is located. The default is to use the current working directory.

=item --perl

The path to the perl executable to use. The default is /usr/bin/perl or perl.exe on MSWin32.

=item --make

The path to the make executable to use. The default is 'make' or 'nmake.exe' on MSWin32.

=item --result

This is string of descriptive text that is put in the pastebot comment. Default is the name of the current working directory.

=item --url

The pastebot url to use. The default is 'http://paste.scsys.co.uk'.

=item --name

The name who the paste will be from. The default is 'POlESmoker'.

=item --channel

The channel the paste will be sent to. The default is '#poe'. 

=item --verbose 

Enable C<verbose> output.

=back

=head1 AUTHOR

Chris 'BinGOs' Williams


