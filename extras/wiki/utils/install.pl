#!/usr/bin/env perl

use warnings;
use strict;

use constant VERBOSE => 1;

foreach my $target (
	qw(
		/Users/troc/Sites/poeperlorg
		/var/www/poeperlorg
	)
) {
	next unless -d $target;

	copy_644(
		$target,
		qw(
			favicon.ico
			global.css
			robots.txt
			dot-htaccess
			data/templates/*.tt2
		)
	);

	copy_755(
		$target,
		qw(
			index.cgi
		)
	);
}

exit;

sub copy_files {
	my ($target, @files) = @_;

	foreach my $file (@files) {
		my $target_file = $file;

		my ($target_path) = ($file =~ /^(.*)\//);
		if (defined $target_path) {
			$target_path = "/$target_path";
		}
		else {
			$target_path = "";
		}

		if (-f $file) {
			$target_file =~ s/^dot-/./;
			$target_path .= "/$target_file";
		}

		my $cmd = "/bin/cp $file $target$target_path";
		VERBOSE and print "$cmd\n";
		system $cmd and die $!;
	}
}

sub chmod_files {
	my ($mode, $target, @files) = @_;

	foreach my $file (@files) {
		(-f $file) and ($file =~ s/^dot-/./);
		my $cmd = "/bin/chmod $mode $target/$file";
		VERBOSE and print "$cmd\n";
		system $cmd and die $!;
	}
}

sub copy_644 {
	my ($target, @files) = @_;

	copy_files($target, @files);
	chmod_files('0644', $target, @files);
}

sub copy_755 {
	my ($target, @files) = @_;

	copy_files($target, @files);
	chmod_files('0755', $target, @files);
}
