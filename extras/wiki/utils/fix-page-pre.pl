#!/usr/bin/env perl

use warnings;
use strict;

use File::Find;
use YAML::Syck;
use JSON::XS;
use HTML::Entities;

use ConvertToJson qw(replace_file_with_json);
use Perl::Tidy;

find( \&process_page, "/var/www/poeperlorg/data/page" );
exit;

sub process_page {
	my $file_name = $_;

	return unless $file_name =~ /\.db/;

	open(my $fh, "<", $file_name) or die $!;
	my $raw_data = do { local $/; scalar <$fh> };
	close $fh;

	return unless defined $raw_data;

	my $data = decode_json($raw_data);
	return unless $data->{text_default}{data}{text} =~ /<(span|div)/;

	1 while (
		$data->{text_default}{data}{text} =~ s!<div\s*id="code">\s*<pre>!!g or
		$data->{text_default}{data}{text} =~ s!<div\s*id="eg">\s*<pre>!!g
	);
	1 while $data->{text_default}{data}{text} =~ s!</pre>\s*</div>!!g;
	1 while $data->{text_default}{data}{text} =~ s!<\/?span[^<>]*>!!g;
	1 while $data->{text_default}{data}{text} =~ s!<a name="[^"]*"></a>!!g;

	while (
		$data->{text_default}{data}{text} =~ m{
			(
				&lt;(pre|perl)&gt;
				(.*?)
				&lt;/\2&gt;
			)
		}gsx
	) {
		my $pos_after_match = pos($data->{text_default}{data}{text});
		my ($whole_match, $tag, $content) = ($1, $2, $3);

		my $orig_len = length($whole_match);
		my $orig_pos = $pos_after_match - $orig_len;

		$content = decode_entities($content);

		if ($tag eq "perl") {
			my $tidied = "";
			Perl::Tidy::perltidy(
				source      => \$content,
				destination => \$tidied,
				argv        => [
					'--quiet',
					'--add-semicolons',
					'--add-whitespace',
					'--block-brace-tightness=0',
					'--brace-tightness=2',
					'--closing-token-indentation=0',
					'--continuation-indentation=2',
					'--delete-old-whitespace',
					'--delete-semicolons',
					'--hanging-side-comments',
					'--indent-block-comments',
					'--indent-columns=2',
					'--indent-spaced-block-comments',
					'--maximum-line-length=80',
					'--minimum-space-to-comment=4',
					'--nocuddled-else',
					'--noline-up-parentheses',
					'--noopening-brace-on-new-line',
					'--noopening-sub-brace-on-new-line',
					'--nooutdent-labels',
					'--nooutdent-long-comments',
					'--nooutdent-long-comments',
					'--nooutdent-long-lines',
					'--nospace-for-semicolon',
					'--nospace-terminal-semicolon',
					'--opening-brace-always-on-right',
					'--output-line-ending=unix',
					'--paren-tightness=2',
					'--quiet',
					'--square-bracket-tightness=2',
					'--notabs',
				],
			);
			$content = $tidied;
		}

		$content = "<$tag>$content</$tag>";

		substr($data->{text_default}{data}{text}, $orig_pos, $orig_len) = $content;

		pos($data->{text_default}{data}{text}) = $pos_after_match - ($orig_len - length($content));
	}

	replace_file_with_json($file_name, $data);
}
