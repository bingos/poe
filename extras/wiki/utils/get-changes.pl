#!/usr/bin/env perl

use warnings;
use strict;

foreach my $source (
	qw(
		/Users/troc/Sites/poeperlorg
		/var/www/poeperlorg
	)
) {
	next unless -d $source;

	copy_files(
		$source,
		qw(
			favicon.ico
			global.css
			robots.txt
			dot-htaccess
			data/templates/*.tt2
			index.cgi
		)
	);
}

exit;

sub copy_files {
	my ($source, @files) = @_;

	foreach my $file (@files) {

		my $source_file = $file;
		$source_file =~ s/^dot-/./;

		my $source_path = "$source/$source_file";

		my $target = "./$file";
		$target =~ s/\/[^\/]*$//;

		my $cmd = "/bin/cp $source_path $target";
		system $cmd and die $!;
	}
}
