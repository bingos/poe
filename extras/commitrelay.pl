#!/usr/bin/env perl

use strict;
use warnings;
use POE qw(Component::IRC Component::IRC::Plugin::Connector
  Component::IRC::Plugin::CTCP);

our $NICK = "poecommits";

our $IN_SERVER = "irc.freenode.net";
our $IN_CHANNEL = "#commits";
our $OUT_SERVER = "irc.perl.org";
our $OUT_CHANNEL = "#poe";

POE::Session->create(
  package_states => [
    'My::Receiver' => [ qw(_start irc_001 irc_public shutdown flush_commit) ],
  ],
);

POE::Session->create(
  package_states => [
    'My::Transmitter' => [ qw(_start irc_001 irc_public a_commit) ],
  ],
);

{
  package My::Receiver;
  use POE;

  my %interesting_projects = (
    poe => 1,
  );

  sub _start {
    $_[KERNEL]->alias_set('receiver');
    my $irc = $_[HEAP]->{irc} = POE::Component::IRC->spawn(
      nick => $NICK,
      server => $IN_SERVER,
      ircname => "irc.perl.org #poe commit relay (IN)",
    ) or die $!;
    $irc->yield(register => qw(001 public));
    $irc->plugin_add(Connector => POE::Component::IRC::Plugin::Connector->new);
    $irc->plugin_add(CTCP => POE::Component::IRC::Plugin::CTCP->new);
    $irc->yield(connect => {});
  }
  sub irc_001 {
    $_[KERNEL]->post($_[SENDER] => join => $IN_CHANNEL);
  }
  sub irc_public {
    my ($kernel, $heap) = @_[KERNEL, HEAP];
    my ($irc, $who, $where, $what) = ($heap->{irc}, @_[ARG0..ARG2]);
    my $channel = $where->[0];
    return unless $channel eq $IN_CHANNEL;
    return unless $who =~ m/^CIA-\d+!.=cia@/i;
    $what =~ s/\cC\d+(,\d+)*//g;
    $what =~ tr/\x00-\x1f//d;
    my ($project) = $what =~ m/(\w+):/;
    print "<$channel> <$who> <$project> <$what>\n";
    return unless $project and exists($interesting_projects{$project});

    # Remove the project.
    $what =~ s/\w+:\s*//;

    # Find the start of a commit.
    my ($committer, $revision) = $what =~ m/(\S+)\s*\*\s*(r\d+)/;
    if ($revision) {

      # If there's a previous commit, flush it.
      if ($heap->{commit}{$project}) {
        $kernel->alarm_remove($heap->{delay}{$project});
        $kernel->post(transmitter => a_commit => $project, join(" ", $heap->{commit}));
        print "  signaled transmitter (previous commit)\n";
      }

      # Start the new commit.
      $heap->{commit}{$project} = [ $what ];
      $heap->{delay}{$project} = $kernel->delay_set(flush_commit => 5, $project);
      return;
    }

    # Don't push new lines onto projects that haven't started.
    return unless exists $heap->{commit}{$project};

    push @{$heap->{commit}{$project}}, $what;
  }

  sub flush_commit {
    my ($kernel, $heap, $project) = @_[KERNEL, HEAP, ARG0];
    $kernel->post(transmitter => a_commit => $project, join(" ", @{$heap->{commit}{$project}}));
    delete $heap->{commit}{$project};
    delete $heap->{delay}{$project};
    print "  signaled transmitter (flushed $project)\n";
  }

  sub shutdown {
    $_[HEAP]->{irc}->yield('shutdown');
  }
}

{
  package My::Transmitter;
  use POE;

  use Text::Wrap qw(wrap $columns $huge);
  $columns = 475;
  $huge    = "wrap";

  sub _start {
    $_[KERNEL]->alias_set('transmitter');
    my $irc = $_[HEAP]->{irc} = POE::Component::IRC->spawn(
      nick => $NICK,
      server => $OUT_SERVER,
      ircname => "irc.perl.org #poe commit relay (OUT)",
    ) or die $!;
    $irc->yield(register => qw(001 public));
    $irc->plugin_add(Connector => POE::Component::IRC::Plugin::Connector->new);
    $irc->plugin_add(CTCP => POE::Component::IRC::Plugin::CTCP->new);
    $irc->yield(connect => {});
  }
  sub irc_001 {
    $_[KERNEL]->post($_[SENDER] => join => $OUT_CHANNEL);
  } 
  sub irc_public { }
  sub a_commit {
    my ($project, $message) = @_[ARG0, ARG1];
    my @commit = wrap("","",$message);

    print "got commit: $project: $message\n";

    foreach (@commit) {
      chomp;
      print "a_commit <$project: $_>\n";
      $_[HEAP]->{irc}->yield(privmsg => $OUT_CHANNEL => "($project) $_");
    }
  }
}

$poe_kernel->run;
