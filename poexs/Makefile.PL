#!perl
# $Id$

use ExtUtils::MakeMaker;
use warnings FATAL => 'all';
use strict;

use File::Find;
use File::Spec;
my @tests;

no warnings qw(once);
find(
	{
		wanted => sub {
			my $file = File::Spec->catfile($File::Find::dir, $_);
			return unless $file =~ /\.t$/;
			return if $file =~ /devel/;
			return if $file =~ /lib/;
			push @tests, $file;
		},
	},
	't/',
);

my $test_str = join " ", sort @tests;

WriteMakefile(
	NAME => 'poexs',
	VERSION_FROM => 'VERSION',
	ABSTRACT => 'C/XS version of POE',
	AUTHOR => 'The POE Community (poe@perl.org)',

	depend => {
		'$(FIRST_MAKEFILE)' => '$(VERSION_FROM)',
	}, # this forces the Makefile to be rebuilt when lib/POE/XS.pm's version changes

	PREREQ_PM => {
		'Test::More' => 0,
	},

	test => {
		TESTS => $test_str,
	},
);

# sungo // vim: ts=4 sw=4 noexpandtab
