#!/usr/bin/env perl

use warnings;
use strict;

use ConvertToJson qw(
	sanitize_data
	deep_check_deserialization
	utf8_decode_data
	deserialize_section
	replace_file_with_json
);

use File::Find;
use YAML::Syck;

find( \&process_kept, "./data/keep" );
exit;

sub process_kept {
	my $file_name = $_;

	return unless $file_name =~ /\.kp/;

	open(my $fh, "<", $file_name) or die $!;
	my $raw_data = do { local $/; scalar <$fh> };
	close $fh;

	return unless defined $raw_data;

	my @data = (
		grep { defined }
		map { deserialize_section($_) }
		split /\xb31/, $raw_data, -1
	);

	#@data = @{ sanitize_data(\@data) };
	@data = @{ utf8_decode_data(sanitize_data(\@data)) };

	eval { deep_check_deserialization(\@data) };
	warn "$file_name\n$@" if $@;

	replace_file_with_json($file_name, \@data);
}
