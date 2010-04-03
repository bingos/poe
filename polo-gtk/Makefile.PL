#!/usr/bin/perl
# rocco // vim: ts=2 sw=2 expandtab

use warnings;
use strict;
use ExtUtils::MakeMaker;
use POE::Test::Loops;

# Switch to default behavior if STDIN isn't a tty.

unless (-t STDIN) {
  warn(
    "\n",
    "=============================================\n\n",
    "STDIN is not a terminal.  Assuming --default.\n\n",
    "=============================================\n\n",
  );
  push @ARGV, "--default";
}

# Remind the user she can use --default.

unless (grep /^--default$/, @ARGV) {
  warn(
    "\n",
    "=============================================\n\n",
    "Prompts may be bypassed by running:\n",
    "   $^X $0 --default\n\n",
    "=============================================\n\n",
  );
}

# Should we skip the network tests?

my $prompt = (
  "Some of POE::Loop::Gtk's tests require a\n" .
  "functional network.  You can skip these network\n" .
  "tests if you'd like.\n\n" .
  "Would you like to skip the network tests?"
);

my $ret = "n";
if (grep /^--default$/, @ARGV) {
  print $prompt, " [$ret] $ret\n\n";
}
else {
  $ret = prompt($prompt, "n");
}

my $marker = 'run_network_tests';
unlink $marker;
unless ($ret =~ /^Y$/i) {
  open(TOUCH,"+>$marker") and close TOUCH;
}

print "\n";

### Touch files that will be generated at "make dist" time.
### ExtUtils::MakeMaker and Module::Build will complain about them if
### they aren't present now.

open(TOUCH, ">>CHANGES")  and close TOUCH;
open(TOUCH, ">>META.yml") and close TOUCH;

POE::Test::Loops::generate( 't', [ 'POE::Loop::Gtk' ], 0 );

WriteMakefile(
  NAME            => 'POE::Loop::Gtk',
  AUTHOR          => 'Rocco Caputo <rcaputo@cpan.org>',
  ABSTRACT        => 'Gtk event loop support for POE.',
  VERSION_FROM    => 'lib/POE/Loop/Gtk.pm',
  META_ADD        => {
    resources     => {
      license     => 'http://dev.perl.org/licenses/',
      repository  => (
        'https://poe.svn.sourceforge.net/svnroot/poe/trunk/polo-gtk'
      ),
    },
  },
  dist            => {
    COMPRESS      => 'gzip -9f',
    SUFFIX        => 'gz',
    PREOP         => (
      'svn-log.perl --tags ^plg- | ' .
      '/usr/bin/tee ./$(DISTNAME)-$(VERSION)/CHANGES > ./CHANGES'
    ),
  },
  clean           => { FILES => 't/poe_loop_gtk/*.t t/poe_loop_gtk ' . $marker },
  test            => { TESTS => 't/*.t t/poe_loop_gtk/*.t' },

  CONFIGURE_REQUIRES => {
    'ExtUtils::MakeMaker' => 0,
    'POE::Test::Loops'    => 1.035,
  },

  META_MERGE      => {
    build_requires => {
      'POE::Test::Loops'    => 1.035,
    },
  },

  PREREQ_PM       => {
    'POE'               => 1.289,
    'Gtk'               => 0.7009,
  },
);

1;
