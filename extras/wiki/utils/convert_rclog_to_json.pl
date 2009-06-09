#!/usr/bin/env perl

use warnings;
use strict;

use ConvertToJson qw(
	sanitize_data
	deep_check_deserialization
	utf8_decode_data
);

use File::Find;
use File::AtomicWrite;
use JSON::XS;

find( \&process_kept, "./data" );
exit;

sub process_kept {
	my $file_name = $_;

	#return unless $file_name =~ /^rclog(.old)*$/;
	return unless $file_name =~ /^rclog$/;

	open(my $fh, "<", $file_name) or die $!;

	my @data;

	while (<$fh>) {
		chomp;

		my @change_data = split /\xb33/, $_, -1;

		my %change_data;

		my @field_names = qw(
			timestamp page_id summary minor_edit host kind
		);

		my $i = @field_names;
		while ($i--) {
			$change_data{$field_names[$i]} = $change_data[$i];
		}

		my %user_data = split /\xb32/, $change_data[-1], -1;
		$change_data{user_name} = $user_data{name};
		$change_data{user_id}   = $user_data{id};

		push @data, \%change_data;
	}

	#@data = @{ sanitize_data(\@data) };
	@data = @{ utf8_decode_data(sanitize_data(\@data)) };

	eval { deep_check_deserialization(\@data) };
	die "$file_name\n$@" if $@;

	# Now write the new file.

	my $new_file_data = "";
	foreach (@data) {
		$new_file_data .= encode_json($_) . "\n";
	}

	File::AtomicWrite->write_file(
		{
			file  => $file_name,
			input => \$new_file_data,
			mode  => 0644,
		}
	);
}
