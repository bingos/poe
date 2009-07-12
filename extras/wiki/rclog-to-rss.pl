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
use URI::Escape;

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

### Create and globally configure the notable-changes feed.

my $rss_notable = XML::RSS->new(version => '2.0');

$rss_notable->channel(
	%common_feed_info,
	title           => 'POE Wiki Notable Changes',
	description     => 'Notable POE wiki changes, excluding minor edits.',
);

$rss_notable->textinput(%common_text_input_info);

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

my $file_rss_notable  = "$rss_dir/wiki-notable.rss";
my $file_rss_all      = "$rss_dir/wiki-all.rss";

# We don't need to do anything if all our RSS files are up to date.

if (
	(stat $rclog)[9] < ((stat $file_rss_notable)[9] || time()) and
	(stat $rclog)[9] < ((stat $file_rss_all)[9] || time())
) {
	exit;
}

my $earliest = $^T - 14 * 86400;
while (<$rclog>) {
	chomp;
	my $rc_info = decode_json($_);

	# Too old, or, surprisingly, too new.
	next if $rc_info->{timestamp} < $earliest or $rc_info->{timestamp} > $^T;

	my $title = $rc_info->{page_id};
	$title =~ s/_+/ /g;
	$title =~ s!\s*/\s*! - !g;

	my $creator = "$rc_info->{user_name} ($rc_info->{user_id})";
	my $link    = "http://poe.perl.org/?" .  uri_escape($rc_info->{page_id});

	# Translate it to an RSS item.
	my %rss_item = (
		title       => $title,
		permaLink   => $link,
		description => $rc_info->{summary},
		pubDate     => strftime(
			"%a, %d %b %Y %T GMT", gmtime($rc_info->{timestamp})),
		author      => $creator,
	);

	# Minor edits go into the full feed.

	$rss_notable->add_item(%rss_item) unless $rc_info->{minor_edit};
	$rss_all->add_item(%rss_item);
}

# Save the files.
# TODO - Only save the files that have changed.

$rss_notable->save($file_rss_notable);
chmod 0644, $file_rss_notable;

$rss_all->save($file_rss_all);
chmod 0644, $file_rss_all;

exit;
