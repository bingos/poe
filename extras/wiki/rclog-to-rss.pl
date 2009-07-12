#!/bin/sh
# vim: filetype=perl
# The following bit of shell script chooses the right version of Perl.
if [ -x /sw/perl/5a0/bin/perl ];
	then exec /sw/perl/5a0/bin/perl -x $0;
fi
if [ -x /usr/bin/perl ];
	then exec /usr/bin/perl -x $0;
fi
exec /usr/local/bin/perl -x $0
#!perl
#line 13

use warnings;
use strict;

use XML::RSS;
use POSIX qw(strftime);
use JSON::XS;

### Common calculated data.

my %common_feed_info = (
	link            => 'http://poe.perl.org/',
	language        => 'en',
	copyright       => 'Copyright 1998-2009, Rocco Caputo, et al',
	lastBuildDate   => strftime("%a, %d %b %Y %T GMT", gmtime($^T)),
	managingEditor  => 'rcaputo@cpan.org',
	webMaster       => 'rcaputo@cpan.org',
);

my %common_text_input_info = (
	title       => "Search POE's Wiki",
	description => "Enter a search string.",
	name        => "query",
	link        => "http://poe.perl.org/action/search",
);

### Create and globally configure the major-changes feed.

my $rss_major = XML::RSS->new(version => '2.0');

$rss_major->channel(
	%common_feed_info,
	title           => 'POE Wiki Major Changes',
	description     => 'Major POE wiki changes, excluding minor edits.',
);

$rss_major->textinput(%common_text_input_info);

### Create and globally configure the all-changes feed.

my $rss_all = XML::RSS->new(version => '2.0');

$rss_all->channel(
	%common_feed_info,
	title           => 'POE Wiki - All Changes',
	description     => 'All POE wiki changes, including minor edits.',
);

$rss_all->textinput(%common_text_input_info);

### Add changes that happened within the last fortnight.

my @candidates = qw(
	/var/www/poeperlorg/data/rclog
	/home/troc/Sites/poeperlorg/data/rclog
);

my ($rclog, $rss_dir);
foreach (@candidates) {
	if (open($rclog, "<", $_)) {
		$rss_dir = $_;
		$rss_dir =~ s!/data/rclog!!;
		last;
	}
}
die "couldn't open rclog: $!" unless $rclog;

my $earliest = $^T - 14 * 86400;
while (<$rclog>) {
	chomp;
	my $rc_info = decode_json($_);

	# Too old, or, surprisingly, too new.
	next if $rc_info->{timestamp} < $earliest or $rc_info->{timestamp} > $^T;

	# Translate it to an RSS item.
	my %rss_item = (
		title       => "$rc_info->{page_id} (wiki change)",
		permaLink   => "http://poe.perl.org/?" . $rc_info->{page_id},
		description => $rc_info->{summary},
		pubDate     => strftime("%a, %d %b %Y %T GMT", gmtime($^T)),
		dc => {
			creator => "$rc_info->{user_name} ($rc_info->{user_id})",
		},
	);

	# Minor edits go into the full feed.

	$rss_major->add_item(%rss_item) unless $rc_info->{minor_edit};
	$rss_all->add_item(%rss_item);
}

# Save the files.

{
	my $rss_file = "$rss_dir/wiki-major.rss";
	$rss_major->save($rss_file);
	chmod 0644, $rss_file;
}

{
	my $rss_file = "$rss_dir/wiki-all.rss";
	$rss_all->save($rss_file);
	chmod 0644, $rss_file;
}

exit;
