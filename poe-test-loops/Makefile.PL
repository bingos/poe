# $Id$

use ExtUtils::MakeMaker;

# Touch auto-generated files so we don't see warnings.
open(CHANGES, ">>CHANGES") and close CHANGES;
open(README, ">>README")   and close README;

WriteMakefile(
  NAME         => 'POE::Test::Loops',
  AUTHOR       => 'Rocco Caputo <rcaputo@cpan.org>',
  ABSTRACT     => 'POE::Loop test suite',
  LICENSE      => 'perl',
  VERSION_FROM => 'bin/poe-gen-tests',
  PREREQ_PM    => {
    'Test::More' => 0,
  },
  EXE_FILES    => [ 'bin/poe-gen-tests' ],
  dist         => {
    COMPRESS   => 'gzip -9f',
    SUFFIX     => 'gz',
    PREOP      => (
      'svn-log.perl --tags ^ptl- | ' .
      'tee ./$(DISTNAME)-$(VERSION)/CHANGES > ./CHANGES;' .
      'perldoc bin/poe-gen-tests > README'
    ),
  },
);
