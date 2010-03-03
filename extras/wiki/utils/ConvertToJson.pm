package ConvertToJson;

use warnings;
use strict;

use Encode qw(decode FB_DEFAULT);
use Carp qw(croak);
use File::AtomicWrite;
use JSON::XS;

use Exporter qw(import);
our @EXPORT_OK = qw(
	sanitize_data
	replace_file_with_json
	deep_check_deserialization
	utf8_decode_data
	deserialize_section
);

sub sanitize_data {
	my $insane = shift;

	return "" unless defined $insane;

	if (ref($insane) eq "") {
		return $insane;
	}

	if (ref($insane) eq "HASH") {
		my %sanitized;
		foreach my $key (keys %$insane) {
			$sanitized{$key} = sanitize_data($insane->{$key});
		}
		return \%sanitized;
	}

	if (ref($insane) eq "ARRAY") {
		return [ map { sanitize_data($_) } @$insane ];
	}

	croak "unknown data type: " . ref($insane);
}

sub utf8_decode_data {
	my $encoded = shift;

	if (ref($encoded) eq "") {
		my $decoded = decode("UTF-8", $encoded, FB_DEFAULT);
		$decoded =~ s/\x{FFFD}/\x{203D}/g;
		return $decoded;
	}

	if (ref($encoded) eq "HASH") {
		my %decoded;
		foreach my $key (keys %$encoded) {
			$decoded{$key} = utf8_decode_data($encoded->{$key});
		}
		return \%decoded;
	}

	if (ref($encoded) eq "ARRAY") {
		return [ map { utf8_decode_data($_) } @$encoded ];
	}

	croak "unknown data type: " . ref($encoded);
}

sub replace_file_with_json {
	my ($file, $data) = @_;
	my $json_version = encode_json($data);
	File::AtomicWrite->write_file(
		{
			file  => $file,
			input => \$json_version,
			mode  => 0644,
		}
	);
}

sub deep_check_deserialization {
	my $data = shift;

	croak "data member is undefined" unless defined $data;

	if (ref($data) eq "") {
		croak "data member contains serialization code ($data)" if $data =~ /\xb3/;
		return;
	}

	if (ref($data) eq "HASH") {
		foreach my $value (values %$data) {
			deep_check_deserialization($value);
		}
		return;
	}

	if (ref($data) eq "ARRAY") {
		foreach my $value (@$data) {
			deep_check_deserialization($value);
		}
		return;
	}

	croak "unknown data type: " . ref($data);
}

sub deserialize_section {
	my $serialized_section = shift;

	my %section = (split /\xb32/, $serialized_section, -1);
	if (defined $section{data}) {
		$section{data} = { split /\xb33/, $section{data}, -1 };
	}
	else {
		$section{data} = { };
	}

	return \%section;
}

1;
