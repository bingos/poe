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
#
# $Id$
#
# This wiki has no name.  It's based on:
# UseModWiki version 0.91 (February 12, 2001)
# By the time it's done, it should bear little resemblance.
#
# Copyright (C) 2003-2009 Rocco Caputo.
#
# Copyright (C) 2001-2002 Matt Cashner, Rocco Caputo, and Richard
# Soderberg The POE crew strikes again.
#
# Copyright (C) 2000-2001 Clifford A. Adams
#    <caadams@frontiernet.net> or <usemod@usemod.com>
#
# Based on the GPLed AtisWiki 0.3  (C) 1998 Markus Denker
#    <marcus@ira.uka.de>
#
# ...which was based on
#    the LGPLed CVWiki CVS-patches (C) 1997 Peter Merel
#    and The Original WikiWikiWeb  (C) Ward Cunningham
#        <ward@c2.com> (code reused with permission)
#
# ThinLine options by Jim Mahoney <mahoney@marlboro.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
#    Free Software Foundation, Inc.
#    59 Temple Place, Suite 330
#    Boston, MA 02111-1307 USA

#use lib qw(/home/troc/lib/local/share/perl);

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Template;
use POSIX qw(strftime);
use JSON::XS;
use Storable qw(dclone);

use constant UID_MINLEGAL     => 1001;
use constant UID_ENOCOOKIE    => 111;
use constant UID_ENOUSERFILE  => 112;
use constant UID_EBADCOOKIE   => 113;
use constant UID_MINPOSSIBLE  => 1;

use constant REDIR_CGIPM  => 1;
use constant REDIR_SCRIPT => 2;
use constant REDIR_NONE   => 3;

use constant ROBOTS_KEEP_OUT  => 1;
use constant ROBOTS_COME_IN   => 0;

use constant SKIP_RENDERING_IMAGES  => 0;
use constant RENDER_IMAGES          => 1;

use constant SKIP_LINE_ORIENTED_MARKUP  => 0;
use constant DO_LINE_ORIENTED_MARKUP    => 1;
use constant ONLY_LINE_ORIENTED_MARKUP  => 2;

$| = 1;      # Do not buffer output

# == Configuration ============================================================

# Development flag.  Dump the before and after versions of source code
# as it passes through Perl::Tidy.

use constant DUMP_TIDY => 0;

# Configuration/constant variables.  Must be C<use vars> because
# they're overridden with a do() function.

our (%config, $dir_data);

# Field separators are used in the URL-style patterns below.
my $FS = "\x{FFFD}";

my (
	$pattern_link, $pattern_inter_link, $pattern_inter_site,
	$pattern_free_link, $pattern_url_schemes, $pattern_url,
	$pattern_image_extensions, $pattern_rfc, $pattern_isbn,
);

use constant RS_CGI                 => 'cgi';
use constant RS_INDEX_HASH          => 'index_hash';
use constant RS_INDEX_LIST          => 'index_list';
use constant RS_KEPT_REVISION_HASH  => 'kept_revision_hash';
use constant RS_KEPT_REVISION_LIST  => 'kept_revision_list';
use constant RS_MAIN_PAGE           => 'main_page';
use constant RS_OPEN_PAGE_ID        => 'open_page_id';
use constant RS_PAGE                => 'page';
use constant RS_SAVED_HTML          => 'saved_html';
use constant RS_SAVED_URL_IDX       => 'saved_url_idx';
use constant RS_SECTION             => 'section';
use constant RS_SET_COOKIE          => 'set_cookie';
use constant RS_TEXT                => 'text';
use constant RS_TIME_ZONE_OFFSET    => 'time_zone_offset';
use constant RS_USER_COOKIE         => 'user_cookie';
use constant RS_USER_DATA           => 'user_data';
use constant RS_USER_ID             => 'user_id';

use constant SECT_DATA							=> 'data';
use constant SECT_KEEP_TS						=> 'keepts';
use constant SECT_PAGE_ID						=> 'name';
use constant SECT_REVISION					=> 'revision';
use constant SECT_TIMESTAMP_CHANGE  => 'ts';
use constant SECT_TIMESTAMP_CREATE	=> 'tscreate';
use constant SECT_USER_HOST					=> 'host';
use constant SECT_USER_ID						=> 'id';
use constant SECT_USER_IP						=> 'ip';
use constant SECT_USER_NAME					=> 'username';
use constant SECT_VERSION						=> 'version';

use constant PAGE_REVISION					=> 'revision';
use constant PAGE_TEXT_DEFAULT			=> 'text_default';
use constant PAGE_TIMESTAMP_CHANGE  => 'ts';
use constant PAGE_TIMESTAMP_CREATE	=> 'tscreate';
use constant PAGE_VERSION						=> 'version';

use constant TEXT_IS_MINOR_REV			=> 'minor';
use constant TEXT_IS_NEW_AUTHOR			=> 'newauthor';
use constant TEXT_SUMMARY						=> 'summary';
use constant TEXT_TEXT							=> 'text';

use constant SCOOK_ID								=> 'id';
use constant SCOOK_RANDKEY					=> 'randkey';
use constant SCOOK_REV							=> 'rev';

use constant UCOOK_ID								=> 'id';
use constant UCOOK_RANDKEY					=> 'randkey';

use constant USER_ADMIN_PASSWORD		=> 'adminpw';
use constant USER_CREATE_IP					=> 'createip';
use constant USER_CSS								=> 'css';
use constant USER_ID								=> 'id';
use constant USER_NAME							=> 'username';
use constant USER_PASSWORD					=> 'password';
use constant USER_RANDKEY						=> 'randkey';
use constant USER_TIMESTAMP_CREATE	=> 'createtime';
use constant USER_TIMEZONE_OFFSET		=> 'tzoffset';

use constant RC_TIMESTAMP     => 'timestamp';
use constant RC_PAGE_ID       => 'page_id';
use constant RC_SUMMARY       => 'summary';
use constant RC_IS_MINOR_REV  => 'minor_edit';
use constant RC_EDIT_HOST     => 'host';
use constant RC_KIND          => 'kind';
use constant RC_USER_ID       => 'user_id';
use constant RC_USER_NAME     => 'user_name';
use constant RC_LINK          => 'display_link';
use constant RC_TIME          => 'display_time';
use constant RC_COUNT         => 'display_count';
use constant RC_EDIT          => 'display_edit';
use constant RC_AUTHOR        => 'display_author';

use constant ACT_RC_EDIT_DELETE => 1;
use constant ACT_RC_EDIT_RENAME => 2;

my (
	%inter_site_map, %request_state,
);

# Automatically filled in by version control.
my $VERSION = (qw($Revision$))[1];

##############################
### INITIALIZATION SECTION ###

sub init_wiki {
	# Locate the main wiki directory.

	if (
		defined($ENV{SERVER_NAME}) and
		$ENV{SERVER_NAME} =~ /^(?:10\.0\.0\.|127\.)/
	) {
		$dir_data = "/home/troc/Sites/poeperlorg/data";
	}
	elsif (defined $ENV{DOCUMENT_ROOT}) {
		$dir_data = $ENV{DOCUMENT_ROOT};
		$dir_data .= '/' unless substr($dir_data, -1, 1) eq '/';
		$dir_data .= 'data';
	}

	# Load configuration.

	if (-f "$dir_data/config") {
		if (open(CONFIG, "<", "$dir_data/config")) {
			local $/;

			eval scalar <CONFIG>;
			confess "eval $dir_data/config failed: $@" if $@;
			close(CONFIG);
		}
		else {
			confess "couldn't open config: $!";
		}
	}
	else {
		confess "couldn't find $dir_data/config: $!";
	}

	# Validate configuration.

	confess "no document root; set \$dir_data manually" unless defined $dir_data;
	confess "document root $dir_data doesn't exist" unless -e $dir_data;
	unless (-d $dir_data || -l $dir_data) {
		confess "document root $dir_data isn't a directory";
	}

	# Initialize link patterns.

	my $pattern_upper_letter = "[A-Z";
	my $pattern_lower_letter = "[a-z";
	my $pattern_any_letter   = "[A-Za-z";

	if ($config{allow_non_english_links}) {
		$pattern_upper_letter .= "\xc0-\xde";
		$pattern_lower_letter .= "\xdf-\xff";
		$pattern_any_letter   .= "\xc0-\xff";
	}

	$pattern_any_letter .= "_:0-9" if $config{allow_complex_links};

	$pattern_upper_letter .= "]";
	$pattern_lower_letter .= "]";
	$pattern_any_letter   .= "]";

	# Main link pattern: lowercase between uppercase, then anything
	my $pattern_link_wiki = (
		$pattern_upper_letter . "+" .
		$pattern_lower_letter . "+" .
		$pattern_upper_letter . $pattern_any_letter . "*"
	);

	# Optional subpage link pattern: uppercase, lowercase, then anything
	my $pattern_link_subpage = (
		$pattern_upper_letter . "+" .
		$pattern_lower_letter . "+" .
		$pattern_any_letter . "*"
	);

	if ($config{use_subpages}) {

		# Loose pattern: If subpage is used, subpage may be simple name
		$pattern_link = (
			"(" .
			"(?:(?:$pattern_link_wiki)?\\/$pattern_link_subpage)" .
			"|$pattern_link_wiki" .
			")"
		);

		# Strict pattern: both sides must be the main pattern_link
		# $pattern_link = "((?:(?:$pattern_link_wiki)?\\/)?$pattern_link_wiki)";
	}
	else {
		$pattern_link = "($pattern_link_wiki)";
	}

	# Optional quote delimiter (not in output)
	my $pattern_quote_delimiter = '(?:"")?';
	$pattern_link .= $pattern_quote_delimiter;

	# Inter-site convention: sites must start with uppercase letter
	# (Uppercase letter avoids confusion with URLs)

	$pattern_inter_site = $pattern_upper_letter . $pattern_any_letter . "+";

	$pattern_inter_link = (
		"((?:$pattern_inter_site:[^\\]\\s\"<>$FS]+)$pattern_quote_delimiter)"
	);

	if ($config{allow_free_links}) {

		# Note: the - character must be first in $pattern_any_letter definition
		if ($config{allow_non_english_links}) {
			$pattern_any_letter = "[-,.:' _0-9A-Za-z\xc0-\xff]";
		}
		else {
			$pattern_any_letter = "[-,.:' _0-9A-Za-z]";
		}
	}

	$pattern_free_link = "($pattern_any_letter+)";

	if ($config{use_subpages}) {
		$pattern_free_link = (
			"((?:(?:$pattern_any_letter+)?\\/)?$pattern_any_letter+)"
		);
	}

	$pattern_free_link .= $pattern_quote_delimiter;

	# Url-style links are delimited by one of:
	#   1.  Whitespace                           (kept in output)
	#   2.  Left or right angle-bracket (< or >) (kept in output)
	#   3.  Right square-bracket (])             (kept in output)
	#   4.  A single double-quote (")            (kept in output)
	#   5.  A $FS (field separator) character    (kept in output)
	#   6.  A double double-quote ("")           (removed from output)

	$pattern_url_schemes = (
		"http|https|ftp|afs|news|nntp|mid|cid|mailto|wais|" .
		"prospero|telnet|gopher"
	);

	$pattern_url_schemes .= '|file' if $config{allow_file_scheme};

	$pattern_url = (
		"((?:(?:$pattern_url_schemes):[^\\]\\s\"<>$FS]+)$pattern_quote_delimiter)"
	);

	$pattern_image_extensions = "(gif|jpg|png|bmp|jpeg)";

	$pattern_rfc = "RFC\\s?(\\d+)";

	$pattern_isbn = "ISBN:?([0-9- xX]{10,})";
}

########################
### HELPER FUNCTIONS ###

sub replace_whitespace {
	my ($id) = @_;

	$id =~ s/ /_/g;
	return lc $id;
}

sub read_file {
	my ($fileName) = @_;

	if (open(IN, "<", $fileName)) {
		local $/;

		my $data = <IN>;
		close IN;
		return (1, $data);
	}

	return (0, "");
}

sub create_directory {
	my ($newdir) = @_;

	mkdir($newdir, 0775) unless -d $newdir;
	confess "Failed to mkdir $newdir: $!" unless -d $newdir;
}

sub write_string_to_file {
	my ($file, $string) = @_;

	confess "about to write raw html out to a file" if $string =~ /<span id="/;
	open(OUT, ">", $file) or confess "can't write $file: $!";
	print OUT $string;
	close(OUT) or confess "close failed (write_string_to_file) on $file: $!";
}

sub read_file_or_die {
	my ($fileName) = @_;

	my ($status, $data) = read_file($fileName);
	confess "Can't open $fileName: $!" unless $status;

	return $data;
}

sub is_valid_page_id {
	my ($id) = @_;

	if (length($id) > 120) {
		return "Page name is too long: $id";
	}

	if ($id =~ m!\s!) {
		return "Page name may not contain space characters: $id";
	}

	if ($config{use_subpages}) {
		if ($id =~ m!.*/.*/!) {
			return "Too many / characters in page $id";
		}

		if ($id =~ /^\//) {
			return "Invalid Page $id (subpage without main page)";
		}

		if ($id =~ /\/$/) {
			return "Invalid Page $id (missing subpage name)";
		}
	}

	if ($config{allow_free_links}) {
		$id =~ s/ /_/g;
		unless ($config{use_subpages}) {
			if ($id =~ /\//) {
				return "Invalid Page $id (/ not allowed)";
			}
		}

		unless ($id =~ m!$pattern_free_link!) {
			return "Invalid Page $id";
		}

		return "";
	}
	else {
		unless ($id =~ /^$pattern_link$/o) {
			return "Invalid Page $id";
		}
	}

	return "";
}

sub is_valid_page_id_or_error {
	my ($id) = @_;

	my $error = is_valid_page_id($id);
	if ($error ne "") {
		print render_error_page_as_html($error);
		return 0;
	}

	return 1;
}

# TODO - I suspect that timezone handling is broken, but it's not
# fatally so.

sub render_date_as_text { # TODO
	my ($ts) = @_;
	return strftime("%B %e, %y", gmtime($ts));
}

sub render_time_as_text { # TODO
	my $ts = shift;
	return strftime("%r GMT", gmtime($ts)) if $config{use_12_hour_times};
	return strftime("%T GMT", gmtime($ts));
}

sub render_date_time_as_text { # TODO
	my ($t) = @_;
	return render_date_as_text($t) . " " . render_time_as_text($t);
}

sub request_lock_dir {
	my ($name, $tries, $wait, $errorDie) = @_;

	create_directory($config{dir_temp});
	my $lockName = $config{dir_locks} . $name;
	my $n        = 0;

	while (mkdir($lockName, 0555) == 0) {

		# TODO - POSIX or Errno instead
		if ($! != 17) {
			confess("can't make $config{dir_locks}: $!\n") if $errorDie;
			return 0;
		}

		return 0 if $n++ >= $tries;
		sleep($wait);
	}

	return 1;
}

sub release_lock_dir {
	my ($name) = @_;
	rmdir($config{dir_locks} . $name);
}

sub request_main_lock {
	# 10 tries, 3 second wait, die on error
	return request_lock_dir("main", 10, 3, 1);
}

sub release_main_lock {
	release_lock_dir('main');
}

sub force_release_lock {
	my ($name) = @_;

	# First try to obtain lock (in case of normal edit lock).
	# 5 tries, 3 second wait, do not die on error
	my $forced = !request_lock_dir($name, 5, 3, 0);

	# Release the lock, even if we didn't get it.
	release_lock_dir($name);

	# Return whether lock was forced.
	return $forced;
}

sub quote_html {
	my ($html) = @_;

	$html =~ s/&/&amp;/g;
	$html =~ s/</&lt;/g;
	$html =~ s/>/&gt;/g;
	$html =~ s/\&lt;!--/<!--/g;
	$html =~ s/--&gt;/-->/g;

	# Allow character references?
	$html =~ s/&amp;([\#a-zA-Z0-9]+);/&$1;/g if $config{allow_char_refs};

	return $html;
}

sub unquote_html {
	my ($html) = @_;

	$html =~ s/&amp;/&/g;
	$html =~ s/&lt;/</g;
	$html =~ s/&gt;/>/g;

	# Allow character references?
	$html =~ s/&\#(\d+);/chr($1)/ge if $config{allow_char_refs};

	return $html;
}

sub get_interwiki_url {
	my ($site) = @_;

	unless (keys %inter_site_map) {
		my ($status, $data) = read_file($config{file_inter_wiki_map});

		return "" unless $status;

		# Later consider defensive code.
		%inter_site_map = split(/\s+/, $data);
	}

	return $inter_site_map{$site} if defined $inter_site_map{$site};
	return;
}

sub split_url_from_trailing_punctuation {
	my ($url) = @_;

	if ($url =~ s/\"\"$//) {
		return ($url, "");
	}

	my $punct = "";
	($punct) = ($url =~ /([^a-zA-Z0-9\/\xc0-\xff]+)$/);
	$url =~ s/([^a-zA-Z0-9\/\xc0-\xff]+)$//;

	return ($url, $punct);
}

sub strip_trailing_punct_from_url {
	my ($url) = @_;

	($url, my $junk) = split_url_from_trailing_punctuation($url);

	return $url;
}

#############################
### SITE SEARCH FUNCTIONS ###

sub search_title_and_body {
	my ($string) = @_;

	my @found;
	foreach my $name (get_all_pages_for_entire_site()) {
		open_or_create_page($name);
		open_default_text();

		if (
			($request_state{+RS_TEXT}{+TEXT_TEXT} =~ /\Q$string/i)
			||
			($name =~ /\Q$string/i)
		) {
			push(@found, $name);
			next;
		}

		if ($config{allow_free_links} and ($name =~ m/_/)) {
			my $freeName = $name;
			$freeName =~ s/_/ /g;
			push(@found, $name) if $freeName =~ /\Q$string/i;
			next;
		}

		# TODO - What happens here?
	}

	return @found;
}

sub search_body {
	my ($string) = @_;

	my @found;
	foreach my $name (get_all_pages_for_entire_site()) {
		open_or_create_page($name);
		open_default_text();
		if ($request_state{+RS_TEXT}{+TEXT_TEXT} =~ /$string/i) {
			push(@found, $name);
		}
	}

	return @found;
}

##################
### HTML CACHE ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub try_html_cache {

	return 0 unless $config{use_html_cache};

	my $query = $ENV{QUERY_STRING};

	if (($query eq "") and ($ENV{REQUEST_METHOD} eq "GET")) {
		$query = $config{home_page};    # Allow caching of home page.
	}

	unless ($query =~ /^$pattern_link$/o) {
		unless ($config{allow_free_links} and ($query =~ /^$pattern_free_link/o)) {
			return 0;            # Only use cache for simple links
		}
	}

	my $idFile = get_html_cache_filename_for_id($query);

	if (-f $idFile) {
		open(INFILE, "<", $idFile) or return 0;
		local $/;
		my $text = <INFILE>;
		close INFILE;
		print $text;
		return 1;
	}

	return 0;
}

sub get_html_cache_filename_for_id {
	my ($id) = @_;
	return normalize_filename(
		$config{dir_html_cache} . "/" . get_directory_for_page_id($id) . "/$id.htm"
	);
}

sub unlink_html_cache {
	my ($id) = @_;

	my $idFile = get_html_cache_filename_for_id($id);
	unlink $idFile if -f $idFile;
}

sub update_html_cache {
	my ($id, $html) = @_;

	my $idFile = get_html_cache_filename_for_id($id);
	create_page_directory($config{dir_html_cache}, $id);

	if (request_cache_lock()) {
		write_string_to_file($idFile, $html);
		release_cache_lock();
	}
}

#################
### PAGE DATA ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub get_filename_for_page_id {
	my ($id) = @_;
	return normalize_filename(
		$config{dir_page} . "/" . get_directory_for_page_id($id) . "/$id.db"
	);
}

sub open_or_create_page {
	my ($id) = @_;

	# No need to open, if it's already open.
	return if $request_state{+RS_OPEN_PAGE_ID} eq $id;

	# Reset the text and section.
	$request_state{+RS_TEXT}    = {};
	$request_state{+RS_SECTION} = {};

	my $fname = get_filename_for_page_id($id);

	if (-f $fname) {
		$request_state{+RS_PAGE} = decode_json(read_file_or_die($fname));
	}
	else {
		$request_state{+RS_PAGE} = {
			PAGE_VERSION,         3,    # Data format version
			PAGE_REVISION,        0,    # Number of edited times
			PAGE_TIMESTAMP_CREATE, $^T,  # Set once at creation
			PAGE_TIMESTAMP_CHANGE, $^T,  # Updated every edit
		};
	}

	if ($request_state{+RS_PAGE}{+PAGE_VERSION} != 3) {
		use YAML::Syck;
		print render_error_page_as_html(
			"<pre>" . YAML::Syck::Dump($request_state{+RS_PAGE}) . "</pre>"
		);
	}

	$request_state{+RS_OPEN_PAGE_ID} = $id;
}

sub save_page_to_file {

	# NB - Must always call save_page_to_file() within a lock.
	# TODO - Ensure it is so.

	my $file = get_filename_for_page_id($request_state{+RS_OPEN_PAGE_ID});

	$request_state{+RS_PAGE}{+PAGE_REVISION}++;
	$request_state{+RS_PAGE}{+PAGE_TIMESTAMP_CHANGE} = $^T;

	create_page_directory($config{dir_page}, $request_state{+RS_OPEN_PAGE_ID});
	write_string_to_file($file, encode_json($request_state{+RS_PAGE}));
}

sub create_page_directory {
	my ($dir, $id) = @_;

	# Make sure main page exists.
	create_directory($dir);

	my $subdir = $dir . "/" . get_directory_for_page_id($id);
	create_directory($subdir);
	if ($id =~ m!([^/]+)/!) {
		$subdir = $subdir . "/" . lc($1);
		create_directory($subdir);
	}
}

sub rename_page_and_links {
	my ($old, $new, $doRC, $doText) = @_;

	$old =~ s/ /_/g;
	$new =~ s/ /_/g;
	$new = ucfirst($new);

	my $status = is_valid_page_id($old);

	if ($status ne "") {
		print "Rename: old page $old is invalid, error is: $status<br>\n";
		return;
	}

	$status = is_valid_page_id($new);

	if ($status ne "") {
		print "Rename: new page $new is invalid, error is: $status<br>\n";
		return;
	}

	my $newfname = get_filename_for_page_id($new);
	if (-f $newfname) {
		print "Rename: new page $new already exists--not renamed.<br>\n";
		return;
	}

	my $oldfname = get_filename_for_page_id($old);
	unless (-f $oldfname) {
		print "Rename: old page $old does not exist--nothing done.<br>\n";
		return;
	}

	create_page_directory($config{dir_page}, $new);    # It might not exist yet
	rename($oldfname, $newfname) or confess "Failed to rename $oldfname to $newfname";
	create_page_directory($config{dir_kept_revisions}, $new);

	my $oldkeep = normalize_filename(
		$config{dir_kept_revisions} . "/" .
		get_directory_for_page_id($old) . "/" .
		"$old.kp"
	);
	my $newkeep = normalize_filename(
		$config{dir_kept_revisions} . "/" .
		get_directory_for_page_id($new) . "/" .
		"$new.kp"
	);

	unlink($newkeep) if (-f $newkeep);    # Clean up if needed.
	rename($oldkeep, $newkeep) or confess "Failed to rename $oldkeep to $newkeep";
	unlink($config{file_page_index}) if $config{use_page_index_file};

	edit_recent_changes(ACT_RC_EDIT_RENAME, $old, $new) if $doRC;
	rename_text_links($old, $new) if ($doText);
}

sub delete_page {
	my ($page, $doRC, $doText) = @_;

	$page =~ s/ /_/g;
	$page =~ s/\[+//;
	$page =~ s/\]+//;
	my $status = is_valid_page_id($page);

	if ($status ne "") {
		print "Delete-Page: page $page is invalid, error is: $status<br>\n";
		return;
	}

	my $fname = get_filename_for_page_id($page);
	unlink($fname) if -f $fname;

	$fname = normalize_filename(
		$config{dir_kept_revisions} . "/" .
		get_directory_for_page_id($page) . "/" .
		"$page.kp"
	);

	unlink($fname) if -f $fname;

	unlink($config{file_page_index}) if $config{use_page_index_file};

	edit_recent_changes(ACT_RC_EDIT_DELETE, $page, "") if $doRC;

	# Currently don't do anything with page text.
}

sub get_page_lock_filename {
	my ($id) = @_;

	return normalize_filename(
		$config{dir_page} . "/" . get_directory_for_page_id($id) . "/$id.lck"
	);
}

sub get_links_from_a_page {
	my ($name, $pagelink, $interlink, $urllink) = @_;

	open_or_create_page($name);
	open_default_text();

	my $text = $request_state{+RS_TEXT}{+TEXT_TEXT};

	$text =~ s/<perl>(.|\n)*?\<\/perl>/ /ig;
	$text =~ s/<html>((.|\n)*?)<\/html>/ /ig;
	$text =~ s/<nowiki>(.|\n)*?\<\/nowiki>/ /ig;
	$text =~ s/<pre>(.|\n)*?\<\/pre>/ /ig;
	$text =~ s/<code>(.|\n)*?\<\/code>/ /ig;
	$text =~ s/<boxes>(.|\n)*?\<\/boxes>/ /ig;

	my @links;
	if ($interlink) {
		$text =~ s/''+/ /g;    # Quotes can adjacent to inter-site links
		$text =~ s/$pattern_inter_link/push(@links, strip_trailing_punct_from_url($1)), ' '/geo;
	}
	else {
		$text =~ s/$pattern_inter_link/ /go;
	}

	if ($urllink) {
		$text =~ s/''+/ /g;    # Quotes can adjacent to URLs
		$text =~ s/$pattern_url/push(@links, strip_trailing_punct_from_url($1)), ' '/geo;
	}
	else {
		$text =~ s/$pattern_url/ /go;
	}

	if ($pagelink) {
		if ($config{allow_free_links}) {
			$text =~ s/\[\[$pattern_free_link\|[^\]]+\]\]/push(@links, replace_whitespace($1)),' '/geo;
			$text =~ s/\[\[$pattern_free_link\]\]/push(@links, replace_whitespace($1)), ' '/geo;
		}

		if ($config{allow_camelcase_links}) {
			$text =~ s/$pattern_link/push(@links, strip_trailing_punct_from_url($1)), ' '/geo;
		}
	}

	return @links;
}

sub rename_text_links {
	my ($old, $new) = @_;

	$old =~ s/ /_/g;
	$new =~ s/ /_/g;
	my $status = is_valid_page_id($old);

	if ($status ne "") {
		print "Rename-Text: old page $old is invalid, error is: $status<br>\n";
		return;
	}

	$status = is_valid_page_id($new);

	if ($status ne "") {
		print "Rename-Text: new page $new is invalid, error is: $status<br>\n";
		return;
	}

	$old =~ s/_/ /g;
	$new =~ s/_/ /g;

	foreach my $page (get_all_pages_for_entire_site()) {
		my $changed = 0;
		open_or_create_page($page);
		foreach my $section (keys %{$request_state{+RS_PAGE}}) {
			if ($section =~ /^text_/) {
				open_or_create_section($section);
				$request_state{+RS_TEXT} = dclone(
					$request_state{+RS_SECTION}{+SECT_DATA}
				);
				my $oldText = $request_state{+RS_TEXT}{+TEXT_TEXT};
				my $newText = substitute_text_links($old, $new, $oldText);
				if ($oldText ne $newText) {
					$request_state{+RS_TEXT}{+TEXT_TEXT} = $newText;
					$request_state{+RS_SECTION}{+SECT_DATA} = dclone(
						$request_state{+RS_TEXT}
					);
					$request_state{+RS_PAGE}{$section} = dclone(
						$request_state{+RS_SECTION}
					);
					$changed = 1;
				}
			}
			elsif ($section =~ /^cache_diff/) {
				my $oldText = $request_state{+RS_PAGE}{$section};
				my $newText = substitute_text_links($old, $new, $oldText);
				if ($oldText ne $newText) {
					$request_state{+RS_PAGE}{$section} = $newText;
					$changed = 1;
				}
			}

			# Later: add other text-sections (categories) here
		}

		if ($changed) {
			my $file = get_filename_for_page_id($page);
			write_string_to_file($file, encode_json($request_state{+RS_PAGE}));
		}

		rename_keep_text($page, $old, $new);
	}
}

sub substitute_text_links {
	my ($old, $new, $text) = @_;

	# Much of this is taken from the common markup

	$request_state{+RS_SAVED_HTML} = [];

	$text =~ s/$FS//g;    # Remove separators (paranoia)

	# These types of data are stored in the symbol table as raw html so
	# that they are omitted from the text substitution.

	$text =~ s/(<perl>((.|\n)*?)<\/perl>)/store_raw_html($1)/ige;
	$text =~ s/(<projects>((.|\n)*?)<\/projects>)/store_raw_html($1)/smige;
	$text =~ s/(<outline>((.|\n)*?)<\/outline>)/store_raw_html($1,"bullets")/smige;
	$text =~ s/(<outline-head>((.|\n)*?)<\/outline>)/store_raw_html($1,"headers")/smige;
	$text =~ s/(<outline-todo>((.|\n)*?)<\/outline>)/store_raw_html($1,"todo")/smige;
	$text =~ s/(<components>((.|\n)*?)<\/components>)/store_raw_html($1)/smige;

	if ($config{allow_raw_html}) {
		$text =~ s/(<html>((.|\n)*?)<\/html>)/store_raw_html($1)/ige;
	}

	$text =~ s/(<pre>((.|\n)*?)<\/pre>)/store_raw_html($1)/ige;
	$text =~ s/(<code>((.|\n)*?)<\/code>)/store_raw_html($1)/ige;
	$text =~ s/(<nowiki>((.|\n)*?)<\/nowiki>)/store_raw_html($1)/ige;

	# Rename free links.
	if ($config{allow_free_links}) {
		$text =~ s/\[\[$pattern_free_link\|([^\]]+)\]\]/render_sub_free_link_as_stored_html($1,$2,$old,$new)/geo;
		$text =~ s/\[\[$pattern_free_link\]\]/render_sub_free_link_as_stored_html($1,"",$old,$new)/geo;
	}

	# Links like [URL text of link] don't get renamed.
	if ($config{allow_link_descriptions}) {
		$text =~ s/(\[$pattern_url\s+([^\]]+?)\])/store_raw_html($1)/geo;
		$text =~ s/(\[$pattern_inter_link\s+([^\]]+?)\])/store_raw_html($1)/geo;
	}

	# URLs and inter-wiki links don't get renamed either.
	$text =~ s/(\[?$pattern_url\]?)/store_raw_html($1)/geo;
	$text =~ s/(\[?$pattern_inter_link\]?)/store_raw_html($1)/geo;

	# Rename CamelCase links.
	if ($config{allow_camelcase_links}) {
		$text =~ s/$pattern_link/render_sub_wiki_link_as_stored_html($1, $old, $new)/geo;
	}

	# Restore saved text.
	$text =~ s/$FS(\d+)$FS/$request_state{+RS_SAVED_HTML}[$1]/geo;

	return $text;
}

######################
### RECENT CHANGES ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub append_recent_changes_log {
	my ($id, $summary, $isEdit, $editTime, $name, $rhost) = @_;

	my $rc_line = encode_json(
		{
			RC_TIMESTAMP,     $editTime,
			RC_PAGE_ID,       $id,
			RC_SUMMARY,       $summary,
			RC_IS_MINOR_REV,  $isEdit,
			RC_EDIT_HOST,     $rhost,
			RC_KIND,          0,
			RC_USER_ID,       $request_state{+RS_USER_ID} || 0,
			RC_USER_NAME,     $name || "",
		}
	);

	open(OUT, ">>", $config{file_recent_changes_log}) or confess(
		"$config{rc_name} log error: $!"
	);
	print OUT "$rc_line\n";
	close(OUT);
}

sub edit_recent_changes {
	my ($action, $old, $new) = @_;

	edit_recent_changes_file(
		$config{file_recent_changes_log}, $action, $old, $new
	);
	edit_recent_changes_file(
		$config{file_old_recent_changes_log}, $action, $old, $new
	);
}

sub edit_recent_changes_file {
	my ($fname, $action, $old, $new) = @_;

	my ($status, $fileData) = read_file($fname);
	unless ($status) {
		print(
			"<p><strong>Could not open $config{rc_name} log file:" .
			"</strong> $fname<p>Error was:\n<pre>$!</pre>\n"
		);
		return;
	}

	my $outrc = "";
	my @rclist = map { decode_json($_) } split(/\n/, $fileData);

	RCLINE: foreach my $rcline (@rclist) {
		if ($rcline->{+RC_PAGE_ID} eq $old) {

			# Delete by not adding line to new RC.
			next RCLINE if $action == ACT_RC_EDIT_DELETE;

			if ($action == ACT_RC_EDIT_RENAME) {
				$rcline->{+RC_PAGE_ID} = $new;
			}
		}

		$outrc .= encode_json($rcline) . "\n";
	}

	# Backup copy.
	write_string_to_file("$fname.old", $fileData);

	# Updated current copy.
	write_string_to_file($fname, $outrc);
}

##################
### PAGE INDEX ###

sub request_index_lock {
	# 4 tries, 2 second wait, do not die on error
	return request_lock_dir('index', 4, 2, 0);
}

sub release_index_lock {
	release_lock_dir('index');
}

sub get_all_pages_from_filesystem {
	my @pages;

	my @dirs = qw(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z other);

	foreach my $dir (@dirs) {
		while (<$config{dir_page}/$dir/*.db $config{dir_page}/$dir/*/*.db>) {
			s!^$config{dir_page}/!!;
			m!^[^/]+/(\S*).db!;
			my $id = $1;
			push(@pages, $id);
		}
	}

	return sort(@pages);
}

sub get_all_pages_for_entire_site {
	return get_all_pages_from_filesystem() unless $config{use_page_index_file};

	my $refresh = get_request_param("refresh", 0);

	if (@{$request_state{+RS_INDEX_LIST}} and !$refresh) {

		# May need to change for mod_perl eventually (cache consistency)
		# Possibly check timestamp of file then?
		return @{$request_state{+RS_INDEX_LIST}};
	}

	if ((!$refresh) and (-f $config{file_page_index})) {
		my ($status, $rawIndex) = read_file($config{file_page_index});
		if ($status) {
			$request_state{+RS_INDEX_HASH} = {
				split(/\s+/, $rawIndex)
			};
			$request_state{+RS_INDEX_LIST} = [
				sort(keys %{$request_state{+RS_INDEX_HASH}})
			];
			return @{$request_state{+RS_INDEX_LIST}};
		}

		# If open fails just refresh the index.
	}

	$request_state{+RS_INDEX_LIST} = [];
	$request_state{+RS_INDEX_HASH} = {};

	# Maybe generate? (high load?)
	request_index_lock() or return @{$request_state{+RS_INDEX_LIST}};
	$request_state{+RS_INDEX_LIST} = [ get_all_pages_from_filesystem() ];

	foreach (@{$request_state{+RS_INDEX_LIST}}) {
		${$request_state{+RS_INDEX_HASH}}{$_} = 1;
	}

	write_string_to_file(
		$config{file_page_index},
		join(" ", %{$request_state{+RS_INDEX_HASH}})
	);

	release_index_lock();
	return @{$request_state{+RS_INDEX_LIST}};
}

sub get_all_links_for_entire_site {
	my $unique    = get_request_param("unique", 1);
	my $sort      = get_request_param("sort",   1);
	my $pagelink  = get_request_param("page",   1);
	my $interlink = get_request_param("inter",  0);
	my $urllink   = get_request_param("url",    0);
	my $exists    = get_request_param("exists", 2);
	my $empty     = get_request_param("empty",  0);
	my $search    = get_request_param("search", "");

	if (($interlink == 2) || ($urllink == 2)) {
		$pagelink = 0;
	}

	my %pgExists;
	my @pglist = get_all_pages_for_entire_site();

	foreach my $name (@pglist) {
		$pgExists{$name} = 1;
	}

	my %seen;
	my @found;

	foreach my $name (@pglist) {
		my @newlinks;

		if ($unique != 2) {
			%seen = ();
		}

		my @links = get_links_from_a_page($name, $pagelink, $interlink, $urllink);

		foreach my $link (@links) {
			$seen{$link}++;
			if (($unique > 0) and ($seen{$link} != 1)) {
				next;
			}

			if (($exists == 0) and ($pgExists{$link} == 1)) {
				next;
			}

			if (($exists == 1) and ($pgExists{$link} != 1)) {
				next;
			}

			if (($search ne "") and !($link =~ /$search/)) {
				next;
			}

			push(@newlinks, $link);
		}

		@links = @newlinks;

		if ($sort) {
			@links = sort(@links);
		}

		# Fix relative links.
		my $base_page = $name;
		$base_page =~ s/\s/_/g;
		$base_page =~ s/\/.*$//;

		foreach my $fixup (@links) {
			$fixup =~ s/^\//$base_page\//;
		}

		unshift(@links, $name);

		if ($empty || ($#links > 0)) {    # If only one item, list is empty.
			push(@found, join(' ', @links));
		}
	}

	return @found;
}

sub run_page_and_link_update_script {
	my ($commandList, $doRC, $doText) = @_;

	request_main_lock() or confess(
		"run_page_and_link_update_script could not get main lock"
	);
	unlink($config{file_page_index}) if $config{use_page_index_file};

	foreach (split(/\n/, $commandList)) {
		s/\s+$//g;
		next unless /^[=!|]/;    # Only valid commands.
		print "Processing $_<br>\n";

		if (/^\!(.+)/) {
			delete_page($1, $doRC, $doText);
		}
		elsif (/^\=(?:\[\[)?([^]=]+)(?:\]\])?\=(?:\[\[)?([^]=]+)(?:\]\])?/) {
			rename_page_and_links($1, $2, $doRC, $doText);
		}
		elsif (/^\|(?:\[\[)?([^]|]+)(?:\]\])?\|(?:\[\[)?([^]|]+)(?:\]\])?/) {
			rename_text_links($1, $2);
		}
	}

	clear_cached_pages_linking_to(".");    # Clear cache (needs testing?)
	unlink($config{file_page_index}) if $config{use_page_index_file};
	release_main_lock();
}

################
### SECTIONS ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub create_new_section {
	my ($name, $data) = @_;

	$request_state{+RS_SECTION} = {
		SECT_PAGE_ID,           $name,
		SECT_VERSION,           1,     # Data format version.
		SECT_REVISION,          0,     # Number of times edited.
		SECT_TIMESTAMP_CREATE,  $^T,   # Set once at creation.
		SECT_TIMESTAMP_CHANGE,  $^T,   # Updated every edit.
		SECT_USER_IP,           $ENV{REMOTE_ADDR},
		SECT_USER_HOST,         '',    # Updated for real edits (may be slow)
		SECT_USER_ID,           $request_state{+RS_USER_ID},
		SECT_USER_NAME,         get_request_param('username', ''),
		SECT_DATA,              dclone($data),
	};

	$request_state{+RS_PAGE}{$name} = dclone($request_state{+RS_SECTION});
}

sub open_or_create_section {
	my ($name) = @_;

	if (defined $request_state{+RS_PAGE}{$name}) {
		$request_state{+RS_SECTION} = dclone($request_state{+RS_PAGE}{$name});
	}
	else {
		create_new_section($name, "");
	}
}

sub save_section { # TODO
	my ($name, $data) = @_;

	$request_state{+RS_SECTION}{+SECT_REVISION}++;
	$request_state{+RS_SECTION}{+SECT_TIMESTAMP_CHANGE} = $^T;
	$request_state{+RS_SECTION}{+SECT_USER_IP} = $ENV{REMOTE_ADDR};
	$request_state{+RS_SECTION}{+SECT_USER_ID} = $request_state{+RS_USER_ID};
	$request_state{+RS_SECTION}{+SECT_USER_NAME} = get_request_param(
		"username", ""
	);
	$request_state{+RS_SECTION}{+SECT_DATA} = dclone($data);

	$request_state{+RS_PAGE}{$name} = dclone($request_state{+RS_SECTION});
}

############
### TEXT ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub open_or_create_text {
	my ($name) = @_;

	if (defined $request_state{+RS_PAGE}{"text_$name"}) {
		open_or_create_section("text_$name");
		$request_state{+RS_TEXT} = dclone($request_state{+RS_SECTION}{+SECT_DATA});
	}
	else {
		$request_state{+RS_TEXT} = {
			TEXT_TEXT, (
				"Empty page.\n\n" .
				"Edit this page (see the page footer for link), " .
				"or go back to [[$config{home_page}|the home page]].\n\n" .
				"<!--\n" .
				"\" vim: syntax=wiki\n" .
				"-->\n"
			),
			TEXT_IS_MINOR_REV,  1,   # Default as minor edit.
			TEXT_IS_NEW_AUTHOR, 1,   # Default as new author.
			TEXT_SUMMARY,       '',  # TODO - Can we default the summary?
		};

		create_new_section("text_$name", $request_state{+RS_TEXT});
	}
}

sub open_default_text {
	open_or_create_text('default');
}

sub save_text { # TODO
	my ($name) = @_;

	save_section("text_$name", $request_state{+RS_TEXT});
}

sub save_default_text { # TODO
	save_text('default');
}

#################################
### "KEPT" (whatever that is) ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub open_kept_list { # TODO
	my $fname = get_keep_path_for_open_page();

	unless (-f $fname) {
		$request_state{+RS_KEPT_REVISION_LIST} = [];
		return;
	}

	$request_state{+RS_KEPT_REVISION_LIST} = decode_json(
		read_file_or_die($fname)
	);
}

sub open_kept_revisions { # TODO
	my ($name) = @_;    # Name of section

	$request_state{+RS_KEPT_REVISION_HASH} = {};
	open_kept_list();

	foreach (@{$request_state{+RS_KEPT_REVISION_LIST}}) {
		next if $_->{+SECT_USER_NAME} ne $name;
		$request_state{+RS_KEPT_REVISION_HASH}{$_->{+SECT_REVISION}} = dclone($_);
	}
}

sub open_kept_revision { # TODO
	my ($revision) = @_;

	$request_state{+RS_SECTION} = dclone(
		$request_state{+RS_KEPT_REVISION_HASH}{$revision}
	);

	$request_state{+RS_TEXT} = dclone($request_state{+RS_SECTION}{+SECT_DATA});
}

sub get_keep_path_for_open_page {
	return normalize_filename(
		$config{dir_kept_revisions} . "/" .
		get_directory_for_page_id($request_state{+RS_OPEN_PAGE_ID}) . "/" .
		$request_state{+RS_OPEN_PAGE_ID} . ".kp"
	);
}

sub save_keep_section { # TODO
	my $file_name = get_keep_path_for_open_page();

	# Don't keep "empty" revision.
	return if $request_state{+RS_SECTION}{+SECT_REVISION} < 1;

	create_page_directory(
		$config{dir_kept_revisions},
		$request_state{+RS_OPEN_PAGE_ID}
	);

	$request_state{+RS_SECTION}{+SECT_KEEP_TS} = $^T;

	my $keep_list;
	if (-f $file_name) {
		$keep_list = decode_json(read_file_or_die($file_name));
	}
	else {
		$keep_list = [];
	}

	push @$keep_list, dclone($request_state{+RS_SECTION});
	write_string_to_file($file_name, encode_json($keep_list));
}

sub expire_keep_file { # TODO
	my $fname = get_keep_path_for_open_page();
	return unless -f $fname;

	my $data = read_file_or_die($fname);
	my @keep_list = @{ decode_json($data) };

	# Nothing to expire.
	return unless @keep_list;

	my $expire_ts = $^T - $config{keep_seconds};

	# Nothing old enough.
	return if $keep_list[0]{keepts} >= $expire_ts;

	my $old_major  = get_page_cache('oldmajor');
	my $old_author = get_page_cache('oldauthor');

	my $expire_count = 0;
	my $i = @keep_list;
	while ($i--) {

		my $kept_section = $keep_list[$i];

		if ($kept_section->{+SECT_USER_NAME} ne PAGE_TEXT_DEFAULT) {
			if ($kept_section->{+SECT_KEEP_TS} < $expire_ts) {
				$expire_count++;
				splice(@keep_list, $i, 1);
			}
			next;
		}

		my $section_revision = $kept_section->{+SECT_REVISION};

		if (
			($config{keep_major_revs}  and ($section_revision == $old_major)) or
			($config{keep_author_revs} and ($section_revision == $old_author))
		) {
			next;
		}

		if ($kept_section->{+SECT_KEEP_TS} < $expire_ts) {
			$expire_count++;
			splice(@keep_list, $i, 1);
			next;
		}
	}

	# All expired?  Remove the file!
	unless (@keep_list) {
		unlink $fname;
		return;
	}

	# Nothing expired?  No point in going on.
	return unless $expire_count;

	# Write the keep list back out.
	my $keep_list_string = encode_json(\@keep_list);
	confess "about to write raw html out to a file" if $keep_list_string =~ /<span id="/;

	open(OUT, ">", $fname) or confess("cant write $fname: $!");
	print OUT $keep_list_string;
	close(OUT) or confess "can't close (expire_keep_file) on $fname: $!";
}

sub rename_keep_text { # TODO
	my ($page, $old, $new) = @_;

	my $fname = normalize_filename(
		$config{dir_kept_revisions} . "/"
		. get_directory_for_page_id($page) . "/" .
		"$page.kp"
	);
	return unless -f $fname;

	my ($status, $data) = read_file($fname);
	return unless $status;

	my @keep_list = @{ decode_json($data) };
	return unless @keep_list;

	return unless defined $keep_list[0]{+SECT_KEEP_TS};

	# First pass: optimize for nothing changed
	my $changed = 0;
	foreach (@keep_list) {
		my $section_name = $_->{+SECT_USER_NAME};

		if ($section_name =~ /^(text_)/) {
			$request_state{+RS_TEXT} = dclone($_->{+SECT_DATA});

			my $new_text = substitute_text_links(
				$old, $new, $request_state{+RS_TEXT}{+TEXT_TEXT}
			);

			if ($request_state{+RS_TEXT}{+TEXT_TEXT} ne $new_text) {
				$changed++;
				$request_state{+RS_TEXT}{+TEXT_TEXT} = $new_text;
				$_->{+SECT_DATA} = dclone($request_state{+RS_TEXT});
			}
		}

		# Later add other section types? (maybe)
	}

	# No sections changed?
	return unless $changed;

	my $keep_list_string = encode_json(\@keep_list);
	confess "about to write raw html out to a file" if $keep_list_string =~ /<span id="/;

	open(OUT, ">", $fname) or return;
	print OUT $keep_list_string;
	close(OUT) or confess "cannot close $fname: $!";
}

##################
### PAGE CACHE ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub get_page_cache {
	my ($name) = @_;
	return $request_state{+RS_PAGE}{"cache_$name"};
}

sub set_page_cache {
	my ($name, $data) = @_;
	$request_state{+RS_PAGE}{"cache_$name"} = $data;
}

sub request_cache_lock {
	# 4 tries, 2 second wait, do not die on error
	return request_lock_dir('cache', 4, 2, 0);
}

sub release_cache_lock {
	release_lock_dir('cache');
}

sub clear_cached_pages_linking_to {
	my ($id) = @_;

	return unless $config{use_html_cache};

	# If subpage, search for just the subpage.
	$id =~ s!.+/!/!;

	foreach my $name (search_body($id)) {
		unlink_html_cache($name);
	}
}

#################
### USER DATA ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub load_user_data {
	$request_state{+RS_USER_DATA} = {};
	my ($status, $data) = read_file(
		get_user_data_filename($request_state{+RS_USER_ID})
	);

	unless ($status) {
		$request_state{+RS_USER_ID} = UID_ENOUSERFILE;
		return;
	}

	# -1 keeps trailing null fields.
	$request_state{+RS_USER_DATA} = decode_json($data);
}

sub get_user_data_filename {
	my ($id) = @_;

	return "" if ($id < 1);
	return normalize_filename(
		$config{dir_user_data} . "/" . ($id % 10) . "/$id.db"
	);
}

sub user_can_edit {
	my ($id, $deepCheck) = @_;

	# Optimized for the "everyone can edit" case (don't check passwords)
	if (($id ne "") and (-f get_page_lock_filename($id))) {

		# Admins can always edit.
		return 1 if user_is_admin();

		# Later option for editor-level to edit these pages?
		return 0;
	}

	unless ($config{allow_editing}) {
		return 1 if user_is_editor();
		return 0;
	}

	if (-f "$dir_data/noedit") {
		return 1 if user_is_editor();
		return 0;
	}

	# Deeper but slower checks (not every page).
	if ($deepCheck) {
		return 1 if user_is_editor();
		return 0 if user_is_banned();
	}

	return 1;
}

sub user_is_banned {

	my ($status, $data) = read_file("$dir_data/banlist");

	# No file exists, so no ban.
	return 0 unless $status;

	my $ip   = $ENV{REMOTE_ADDR};
	my $host = get_remote_host(0);

	foreach (split(/\n/, $data)) {

		# Skip empty, spaces, or comments
		next if /^\s*$/ || /^\s*#/;

		return 1 if $ip   =~ /$_/i;
		return 1 if $host =~ /$_/i;
	}

	return 0;
}

sub user_is_admin {

	# Nobody is admin if there's no admin password.
	return 0 if $config{admin_pass} eq "";

	my $userPassword = get_request_param("adminpw", "");
	return 0 if ($userPassword eq "");

	foreach (split(/\s+/, $config{admin_pass})) {
		next if ($_ eq "");
		return 1 if $userPassword eq $_;
	}

	return 0;
}

sub user_is_editor {
	# Administrators are also editors.
	return 1 if user_is_admin();

	# However, nobody else may be an editor if there's no password.
	return 0 if $config{edit_pass} eq "";

	my $userPassword = get_request_param("adminpw", "");
	return 0 if $userPassword eq "";

	foreach (split(/\s+/, $config{edit_pass})) {
		next if ($_ eq "");
		return 1 if $userPassword eq $_;
	}

	return 0;
}

sub do_new_login {

	# TODO - Consider warning if cookie already exists.  Maybe use
	# "replace=1" parameter?

	create_user_directories();
	$request_state{+RS_SET_COOKIE}{+SCOOK_ID}      = get_new_user_id();
	$request_state{+RS_SET_COOKIE}{+SCOOK_RANDKEY} = int(rand(1000000000));
	$request_state{+RS_SET_COOKIE}{+SCOOK_REV}     = 1;
	$request_state{+RS_USER_COOKIE} = {
		%{$request_state{+RS_SET_COOKIE}}
	};
	$request_state{+RS_USER_ID} = $request_state{+RS_SET_COOKIE}{+SCOOK_ID};

	# The cookie will be transmitted in the next header.

	$request_state{+RS_USER_DATA} = { %{$request_state{+RS_USER_COOKIE}} };
	$request_state{+RS_USER_DATA}{+USER_TIMESTAMP_CREATE} = $^T;
	$request_state{+RS_USER_DATA}{+USER_CREATE_IP}   = $ENV{REMOTE_ADDR};

	save_user_data();
}

sub do_login {
	my $success = 0;
	my $uid = get_request_param("p_userid", "");
	$uid =~ s/\D//g;
	my $password = get_request_param("p_password", "");

	if (($uid > 199) and ($password ne "") and ($password ne "*")) {
		$request_state{+RS_USER_ID} = $uid;
		load_user_data();
		if ($request_state{+RS_USER_ID} > 199) {
			if (
				defined($request_state{+RS_USER_DATA}{+USER_PASSWORD}) and
				($request_state{+RS_USER_DATA}{+USER_PASSWORD} eq $password)
			) {
				$request_state{+RS_SET_COOKIE}{+SCOOK_ID}      = $uid;
				$request_state{+RS_SET_COOKIE}{+SCOOK_RANDKEY} = $request_state{+RS_USER_DATA}{+USER_RANDKEY};
				$request_state{+RS_SET_COOKIE}{+SCOOK_REV}     = 1;
				$success = 1;
			}
		}
	}

	print render_page_header_as_html("", "Login Results", "", ROBOTS_KEEP_OUT);

	if ($success) {
		print "Login for user ID $uid complete.";
	}
	else {
		print "Login for user ID $uid failed.";
	}

	print render_common_footer_as_html();
}

sub get_new_user_id {
	my $id = UID_MINLEGAL;

	while (-f get_user_data_filename($id + 1000)) {
		$id += 1000;
	}

	while (-f get_user_data_filename($id + 100)) {
		$id += 100;
	}

	while (-f get_user_data_filename($id + 10)) {
		$id += 10;
	}

	request_main_lock() or confess "Could not get user-ID lock";

	while (-f get_user_data_filename($id)) {
		$id++;
	}

	write_string_to_file(get_user_data_filename($id), "lock");    # reserve the ID
	release_main_lock();
	return $id;
}

sub save_user_data {
	create_user_directories();
	my $userFile = get_user_data_filename($request_state{+RS_USER_ID});
	my $data = encode_json($request_state{+RS_USER_DATA});
	write_string_to_file($userFile, $data);
}

sub create_user_directories {
	unless (-d "$config{dir_user_data}/0") {
		create_directory($config{dir_user_data});

		foreach my $n (0 .. 9) {
			my $subdir = "$config{dir_user_data}/$n";
			create_directory($subdir);
		}
	}
}

sub user_is_editor_or_render_error { # TODO
	return 1 if user_is_editor();

	print "<p>This operation is restricted to site editors only...\n";
	print render_common_footer_as_html();
	return 0;
}

sub user_is_admin_or_render_error { # TODO
	return 1 if user_is_admin();

	print "<p>This operation is restricted to administrators only...\n";
	print render_common_footer_as_html();
	return 0;
}

sub set_user_pref_from_request_text {
	my ($param) = @_;

	my $temp = get_request_param("p_$param", "*");

	return if ($temp eq "*");
	$request_state{+RS_USER_DATA}{$param} = $temp;
}

sub set_user_pref_from_request_number {
	my ($param, $integer, $min, $max) = @_;

	my $temp = get_request_param("p_$param", "*");
	return if ($temp eq "*");

	$temp =~ s/[^-\d\.]//g;
	$temp =~ s/\..*// if ($integer);
	return if ($temp eq "");
	return if (($temp < $min) || ($temp > $max));

	$request_state{+RS_USER_DATA}{$param} = $temp;

	# Later consider returning status?
}

sub set_user_pref_from_request_bool {
	my ($param) = @_;

	my $temp = get_request_param("p_$param", "*");

	$request_state{+RS_USER_DATA}{$param} = 1 if ($temp eq "on");
	$request_state{+RS_USER_DATA}{$param} = 0 if ($temp eq "*");

	# It is possible to skip updating by using another value, like "2"
}

#################
### DIFF DATA ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub write_diff_log {
	my ($id, $editTime, $diffString) = @_;

	open(OUT, ">>", "$dir_data/diff_log") or confess "cant write diff_log";
	print OUT "------\n" . $id . "|" . $editTime . "\n", $diffString;
	close(OUT);
}

sub update_diffs {
	my ($id, $editTime, $old, $new, $isEdit, $newAuthor) = @_;

	# 0 = "already in lock".
	my $editDiff  = find_differences($old, $new, 0);
	my $oldMajor  = get_page_cache('oldmajor');
	my $oldAuthor = get_page_cache('oldauthor');

	write_diff_log($id, $editTime, $editDiff) if $config{use_diff_log};

	set_page_cache('diff_default_minor', $editDiff);

	if ($isEdit || !$newAuthor) {
		open_kept_revisions(PAGE_TEXT_DEFAULT);
	}

	if ($isEdit) {
		set_page_cache(
			'diff_default_major',
			find_kept_differences($new, $oldMajor, 0)
		);
	}
	else {
		set_page_cache('diff_default_major', "1");
	}

	if ($newAuthor) {
		set_page_cache('diff_default_author', "1");
	}
	elsif ($oldMajor == $oldAuthor) {
		set_page_cache('diff_default_author', "2");
	}
	else {
		set_page_cache(
			'diff_default_author',
			find_kept_differences($new, $oldAuthor, 0)
		);
	}
}

sub release_diff_lock {
	release_lock_dir('diff');
}

sub request_diff_lock {

	# 4 tries, 2 second wait, do not die on error
	return request_lock_dir('diff', 4, 2, 0);
}

sub get_cache_diff {
	my ($type) = @_;

	# TODO - How does this recursion terminate?

	my $diffText = get_page_cache("diff_default_$type");
	$diffText = get_cache_diff('minor') if $diffText eq "1";
	$diffText = get_cache_diff('major') if $diffText eq "2";

	return $diffText;
}

sub find_kept_differences {

	# Must be done after minor diff is set and open_kept_revisions
	# called.

	my ($newText, $oldRevision, $lock) = @_;

	my $oldText = "";
	if (defined($request_state{+RS_KEPT_REVISION_HASH}{$oldRevision})) {
		$oldText = $request_state{+RS_KEPT_REVISION_HASH}{$oldRevision}{+SECT_DATA}{text};
	}

	# Old revision not found, so no diff.
	return "" if $oldText eq "";

	return find_differences($oldText, $newText, $lock);
}

sub find_differences {
	my ($old, $new, $lock) = @_;

	create_directory($config{dir_temp});
	my $oldName = "$config{dir_temp}/old_diff";
	my $newName = "$config{dir_temp}/new_diff";

	if ($lock) {
		request_diff_lock() or return "";
		$oldName .= "_locked";
		$newName .= "_locked";
	}

	write_string_to_file($oldName, $old);
	write_string_to_file($newName, $new);

	my $diff_out = `$config{diff_util} $oldName $newName`;
	release_diff_lock() if ($lock);

	# Get rid of common complaints.
	$diff_out =~ s/\\ No newline.*\n//g;

	# No need to unlink temp files--next diff will just overwrite.
	return $diff_out;
}

##########################
### FILESYSTEM HELPERS ###

sub normalize_filename {
	# The wiki page space is case-insensitive, but the FS is sensitive.

	my $file_name = shift;

	return $file_name if -e $file_name;
	return $file_name unless $config{enable_case_insensitivity};

	# Lowercase subdirectories and everything.
	if ($file_name =~ s/\/([^\/\.]|other)\/(.*?)\.([^\/\.]+)$//) {
		return $file_name . "/$1/" . lc($2) . ".$3";
	}

	# No subdirectories?  Lowercase just the base name.
	if ($file_name =~ s/\/([^\/\.]+)\.([^\/\.]+)$//) {
		return $file_name . "/" . lc($1) . ".$2";
	}

	warn "Strange filename: $file_name";
	return $file_name;
}

sub get_directory_for_page_id {
	my ($id) = @_;

	if ($id =~ /^([a-zA-Z])/) {
		return uc($1);
	}

	return "other";
}

###################
### CGI HELPERS ###

sub init_request {
	$CGI::POST_MAX        = 1024 * 200;    # max post size
	$CGI::DISABLE_UPLOADS = 1;             # no uploads

	$request_state{+RS_CGI} = CGI->new();

	# Reset in case the script is persistent.
	# TODO: Maybe we should just use %request_state here.
	$^T = time;

	# Do we want to grab the script name and use it, or ignore it so that
	# things like http://domain/?Wiki_Link work?

	$request_state{+RS_INDEX_LIST} = [];

	# For subpages only, the name of the top-level page.
	$request_state{+RS_MAIN_PAGE}     = ".";
	$request_state{+RS_OPEN_PAGE_ID}  = "";   # The currently open page

	# Create the data directory if it doesn't exist.
	create_directory($dir_data);

	unless (-d $dir_data) {
		print render_error_page_as_html("Could not create $dir_data: $!");
		return 0;
	}

	# Reads in user data.
	init_request_cookie();

	return 1;
}

sub init_request_cookie {
	$request_state{+RS_SET_COOKIE} = {};
	$request_state{+RS_TIME_ZONE_OFFSET} = 0;
	$request_state{+RS_USER_COOKIE} = {
		$config{cookie_name}
		? $request_state{+RS_CGI}->cookie($config{cookie_name})
		: ()
	};

	$request_state{+RS_USER_ID} = $request_state{+RS_USER_COOKIE}{+UCOOK_ID} || 0;
	$request_state{+RS_USER_ID} =~ s/\D//g;    # Numeric only

	if ($request_state{+RS_USER_ID} < UID_MINPOSSIBLE) {
		$request_state{+RS_USER_ID} = UID_ENOCOOKIE;
	}
	else {
		load_user_data($request_state{+RS_USER_ID});
	}

	if ($request_state{+RS_USER_ID} > 199) {
		if (
			($request_state{+RS_USER_DATA}{+USER_ID} != $request_state{+RS_USER_COOKIE}{+UCOOK_ID})
			or
			($request_state{+RS_USER_DATA}{+USER_RANDKEY} != $request_state{+RS_USER_COOKIE}{+UCOOK_RANDKEY})
		) {
			# Invalid user data.  TODO - Consider a warning message?

			$request_state{+RS_USER_ID}   = UID_EBADCOOKIE;
			$request_state{+RS_USER_DATA} = {};
		}
	}

	$request_state{+RS_TIME_ZONE_OFFSET} = (
		$request_state{+RS_USER_DATA}{+USER_TIMEZONE_OFFSET} || 0
	) * (60 * 60);
}

sub get_remote_host {
	my ($doMask) = @_;

	my $rhost = $ENV{REMOTE_HOST};

	# No remote host.  Try looking up the remote address.  Assumes the
	# remote address exists.

	if ($rhost eq "") {

		# Catch errors (including bad input) without aborting the script.
		eval(
			'use Socket; $iaddr = inet_aton($ENV{REMOTE_ADDR});' .
			'$rhost = gethostbyaddr($iaddr, AF_INET)'
		);
	}

	# Still no remote host, so the remote address wouldn't resolve.  Use
	# the remote address, but semi-anonymize it by making it a class C.
	# TODO - Does this matter?  We show the full host name....

	if ($rhost eq "") {
		$rhost = $ENV{REMOTE_ADDR};
		$rhost =~ s/\d+$/xxx/ if ($doMask);    # Be somewhat anonymous
	}

	return $rhost;
}

sub get_request_param {
	my ($name, $default) = @_;

	my $result = $request_state{+RS_CGI}->param($name);
	return $result if defined $result;
	return $request_state{+RS_USER_DATA}{$name} if (
		defined $request_state{+RS_USER_DATA}{$name}
	);
	return $default;
}

#####################################
### TOP-LEVEL REQUEST DISPATCHERS ###

sub dispatch_browse_request {

	# No parameters.  Browse the home page.
	unless ($request_state{+RS_CGI}->param()) {
		action_browse_page($config{home_page});
		return 1;
	}

	# Just index.cgi?PageName.
	my $id = get_request_param("keywords", "");
	return unless $id and is_valid_page_id_or_error($id);

	action_browse_page($id);
	return 1;
}

sub dispatch_action_request {
	my $action = shift;

	my $id = get_request_param("id", "");

	# TODO - Make this a dispatch table.

	if ($action eq "browse") {
		action_browse_page($id) if is_valid_page_id_or_error($id);
		return 1;
	}

	if ($action eq "rc") {
		action_browse_page($config{rc_name});
		return 1;
	}

	if ($action eq "random") {
		action_browse_random_page();
		return 1;
	}

	if ($action eq "history") {
		print action_page_history($id) if is_valid_page_id_or_error($id);
		return 1;
	}

	if ($action eq "edit") {
		action_open_page_editor($id, 0, 0, "", 0) if is_valid_page_id_or_error($id);
		return;
	}

	if ($action eq "unlock") {
		action_remove_temporary_locks();
		return;
	}

	if ($action eq "index") {
		print render_page_index_as_html();
		return;
	}

	if ($action eq "links") {
		print render_links_page_as_html();
		return;
	}

	if ($action eq "maintain") {
		action_run_periodic_maintenance();
		return;
	}

	if ($action eq "pagelock") {
		action_lock_or_unlock_page_edits();
		return;
	}

	if ($action eq "editlock") {
		action_lock_or_unlock_entire_site_edits();
		return;
	}

	if ($action eq "editprefs") {
		action_open_preferences_editor();
		return;
	}

	if ($action eq "editbanned") {
		action_open_ban_list_editor();
		return;
	}

	if ($action eq "editlinks") {
		action_open_links_editor();
		return;
	}

	if ($action eq "login") {
		print render_login_page_as_html();
		return;
	}

	if ($action eq "enter_login") {
		do_login();
		return;
	}

	if ($action eq "newlogin") {
		$request_state{+RS_USER_ID} = 0;

		# Also creates a new ID, because $request_state{+RS_USER_ID} < 400.
		action_open_preferences_editor();
		return;
	}

	if ($action eq "search") {
		my $query = get_request_param("query", "");
		if ($query ne "" or get_request_param("dosearch", "") ne "") {
			# Searching for nothing.  Return everything.
			if ($query eq "") {
				print render_page_index_as_html();
				return;
			}

			my @search_results = search_title_and_body($query);
			print render_search_results_page_as_html($query, @search_results);
		}

		return;
	}

	if ($action eq "edit_ban") {
		action_write_updated_ban_list();
		return;
	}

	if ($action eq "edit_prefs") {
		action_write_updated_preferences();
		return;
	}

	if ($action eq "edit_links") {
		action_write_updated_links();
		return;
	}

	if ($action eq "save_page") {
		$id = get_request_param("title", "");
		action_write_updated_page() if is_valid_page_id_or_error($id);
		return;
	}

	print render_error_page_as_html("Invalid action parameter $action");
	return;
}

####################################
### TOP-LEVEL REQUESTS & ACTIONS ###

# TODO - Many of these combine action logic and response HTML.  They
# should be broken into action logic (with a return value), and
# response generators that render the return values of the actions
# into appropriate HTML.  This will let us templatize the responses.

# Miscellaneous.
# TODO - Categorize properly.

sub action_lock_or_unlock_entire_site_edits {
	print render_page_header_as_html(
		"", "Set or Remove global edit lock", "", ROBOTS_KEEP_OUT
	);

	return unless user_is_admin_or_render_error();

	my $fname = "$dir_data/noedit";

	if (get_request_param("set", 1)) {
		write_string_to_file($fname, "editing locked.");
	}
	else {
		unlink($fname);
	}

	if (-f $fname) {
		print "<p>Edit lock created.<br>";
	}
	else {
		print "<p>Edit lock removed.<br>";
	}

	print render_common_footer_as_html();
}

sub action_lock_or_unlock_page_edits {
	print render_page_header_as_html(
		"", "Set or Remove page edit lock", "", ROBOTS_KEEP_OUT
	);
	return unless user_is_admin_or_render_error();

	unless (user_is_admin()) {
		print "<p>This operation is restricted to administrators only...\n";
		print render_common_footer_as_html();
		return;
	}

	my $id = get_request_param("id", "");

	if ($id eq "") {
		print "<p>Missing page id to lock/unlock...\n";
		return;
	}

	return unless is_valid_page_id_or_error($id);    # Later consider nicer error?

	my $fname = get_page_lock_filename($id);
	if (get_request_param("set", 1)) {
		write_string_to_file($fname, "editing locked.");
	}
	else {
		unlink($fname);
	}

	if (-f $fname) {
		print "<p>Lock for $id created.<br>";
	}
	else {
		print "<p>Lock for $id removed.<br>";
	}

	print render_common_footer_as_html();
}

sub action_remove_temporary_locks {

	# XXX = All diff and recent-list operations should be done within
	# locks.

	my $LockMessage = "Normal Unlock.";

	print(
		render_page_header_as_html("", "Removing edit lock", "", ROBOTS_KEEP_OUT),
		"<p>This operation may take several seconds...\n"
	);

	if (force_release_lock('main')) {
		$LockMessage = "Forced Unlock.";
	}

	# Later display status of other locks?
	force_release_lock('cache');
	force_release_lock('diff');
	force_release_lock('index');

	print "<br><h2>$LockMessage</h2>", render_common_footer_as_html();
}

sub action_run_periodic_maintenance {
	print(
		render_page_header_as_html(
			"", "Maintenance on all pages", "", ROBOTS_KEEP_OUT
		),
		"<br>"
	);

	my $fname = "$dir_data/maintain";
	unless (user_is_admin()) {
		if ((-f $fname) and ((-M $fname) < 0.5)) {
			print(
				"Maintenance not done.  ",
				"(Maintenance can only be done once every 12 hours.)  ",
				"Remove the \"maintain\" file or wait.",
				render_common_footer_as_html()
			);
			return;
		}
	}

	request_main_lock() or confess "Could not get maintain-lock";

	foreach my $name (get_all_pages_for_entire_site()) {
		open_or_create_page($name);
		open_default_text();
		expire_keep_file();
		print ".... " if $name =~ m!/!;
		print render_unnamed_page_link_as_html($name), "<br>\n";
	}

	write_string_to_file(
		$fname, "Maintenance done at " . render_date_time_as_text($^T)
	);
	release_main_lock();

	# Do any rename/deletion commands.
	# (Must be outside lock because it will grab its own lock)

	$fname = "$dir_data/editlinks";
	if (-f $fname) {
		my $data = read_file_or_die($fname);
		print "<hr>Processing rename/delete commands:<br>\n";

		# Always update RC and links
		run_page_and_link_update_script($data, 1, 1);

		unlink("$fname.old");
		rename($fname, "$fname.old");
	}

	print render_common_footer_as_html();
}

# Browse pages.

sub redirect_browse_page {
	my ($id, $old_id, $isEdit) = @_;

	if ($old_id ne "") {
		print render_redirect_page_as_html(
			"action/browse?id=$id&amp;oldid=$old_id", $id, $isEdit
		);
	}
	else {
		print render_redirect_page_as_html("?$id", $id, $isEdit);
	}
}

sub action_browse_page {
	my ($id) = @_;

	open_or_create_page($id);
	open_default_text();

	my $newText  = $request_state{+RS_TEXT}{+TEXT_TEXT};  # For differences
	my $openKept = 0;

	my $revision = get_request_param("revision", "");
	$revision =~ s/\D//g;                       # Remove non-numeric chars

	my $goodRevision = $revision;               # Non-blank only if exists

	if ($revision ne "") {
		open_kept_revisions(PAGE_TEXT_DEFAULT);

		$openKept = 1;

		unless (defined $request_state{+RS_KEPT_REVISION_HASH}{$revision}) {
			$goodRevision = "";
		}
		else {
			open_kept_revision($revision);
		}
	}

	# Handle a single-level redirect
	my $old_id = get_request_param("oldid", "");
	if (
		($old_id eq "") and
		(substr($request_state{+RS_TEXT}{+TEXT_TEXT}, 0, 10) eq "#REDIRECT ")
	) {
		$old_id = $id;

		if (
			($config{allow_free_links}) and
			($request_state{+RS_TEXT}{+TEXT_TEXT} =~ /\#REDIRECT\s+\[\[.+\]\]/)
		) {
			($id) = (
				$request_state{+RS_TEXT}{+TEXT_TEXT} =~ /\#REDIRECT\s+\[\[(.+)\]\]/
			);
			$id =~ s/ /_/g;    # Convert from typed form to internal form
		}
		else {
			($id) = ($request_state{+RS_TEXT}{+TEXT_TEXT} =~ /\#REDIRECT\s+(\S+)/);
		}

		if (is_valid_page_id($id) eq "") {

			# Later consider revision in rebrowse?
			redirect_browse_page($id, $old_id, 0);
			return;
		}
		else {               # Not a valid target, so continue as normal page
			$id    = $old_id;
			$old_id = "";
		}
	}

	$request_state{+RS_MAIN_PAGE} = $id;
	$request_state{+RS_MAIN_PAGE} =~ s!/.*!!; # Remove subpage name.

	# Need to know if this is a diff (also looking at older revision)
	# so we can stop search robots from indexing it.
	my $allDiff = get_request_param("alldiff", 0);
	if ($allDiff != 0) {
		$allDiff = get_request_param("defaultdiff", 1);
	}

	if (($id eq $config{rc_name}) and get_request_param("norcdiff", 1)) {
		$allDiff = 0;          # Only show if specifically requested
	}

	my $header_revision = $revision;

	my $showDiff = get_request_param("diff", $allDiff);
	my $diffRevision;
	if ($config{allow_diff} and $showDiff) {
		$diffRevision = $goodRevision;
		$diffRevision = get_request_param("diffrevision", $diffRevision);

		# Later try to avoid the following keep-loading if possible?
		open_kept_revisions(PAGE_TEXT_DEFAULT) unless $openKept;
		$header_revision ||= 1;
	}

	# TODO - Put render_page_header_as_html() into each page renderer, so we can
	# them template-ize them.

	my $fullHtml = render_page_header_as_html(
		$id, quote_html($id), $old_id, (
			$header_revision
			? ROBOTS_KEEP_OUT
			: ROBOTS_COME_IN
		)
	);

	if ($config{allow_diff} and $showDiff) {
		$fullHtml .= render_diff_as_html($showDiff, $id, $diffRevision, $newText);
	}

	if ($revision ne "") {

		# Later maybe add edit time?
		if ($goodRevision ne "") {
			$fullHtml .= "<b>Showing revision $revision</b><br>";
		}
		else {
			$fullHtml .= (
				"<b>Revision $revision not available " .
				"(showing current revision instead)</b><br>"
			);
		}
	}

	$fullHtml .= render_wiki_data_as_html(
		$request_state{+RS_TEXT}{+TEXT_TEXT}
	) . "\n";  # . "<hr>\n";

	if ($id eq $config{rc_name}) {
		#print $fullHtml;
		print render_recent_changes_page_as_html();
		#print render_complex_page_footer_as_html($id, $goodRevision);
		return;
	}

	$fullHtml .= render_complex_page_footer_as_html($id, $goodRevision);
	print $fullHtml;

	# Don't cache special versions.
	return if ($showDiff || ($revision ne ""));

	update_html_cache($id, $fullHtml) if $config{use_html_cache};
}

sub action_browse_random_page {
	my @pageList = get_all_pages_for_entire_site();
	my $id       = $pageList[rand @pageList];
	redirect_browse_page($id, "", 0);
}

sub action_page_history {
	my $page_id = shift;

	print render_page_header_as_html(
		"", quote_html("History of $page_id"), "", ROBOTS_KEEP_OUT
	) . "<br>";

	open_or_create_page($page_id);
	open_default_text();

	# Turn off direct "Edit" links.
	my $canEdit = user_can_edit($page_id);
	$canEdit = 0;

	my $html = render_history_line_as_html(
		$page_id, $request_state{+RS_PAGE}{+PAGE_TEXT_DEFAULT}, $canEdit, 1
	);

	open_kept_revisions(PAGE_TEXT_DEFAULT);

	foreach (
		reverse sort { $a <=> $b } keys %{$request_state{+RS_KEPT_REVISION_HASH}}
	) {
		# (needed?)
		next if ($_ eq "");

		$html .= render_history_line_as_html(
			$page_id, $request_state{+RS_KEPT_REVISION_HASH}{$_}, $canEdit, 0
		);
	}

	return $html . render_common_footer_as_html();
}

# Edit ban list.

sub action_open_ban_list_editor {
	print render_page_header_as_html(
		"", "Editing Banned list", "", ROBOTS_KEEP_OUT
	);
	return unless user_is_admin_or_render_error();

	my ($status, $banList) = read_file("$dir_data/banlist");
	$banList = "" unless $status;
	print(
		render_form_start_as_html("edit_ban"),
		"\n",
		"<b>Banned IP/network/host list:</b><br>\n",
		"<p>Each entry is either a commented line (starting with #), ",
		"or a Perl regular expression (matching either an IP address or ",
		"a hostname).  <b>Note:</b> To test the ban on yourself, you must ",
		"give up your admin access (remove password in Preferences).",
		"<p>Examples:<br>",
		"\\.foocorp.com\$  (blocks hosts ending with .foocorp.com)<br>",
		"^123.21.3.9\$  (blocks exact IP address)<br>",
		"^123.21.3.  (blocks whole 123.21.3.* IP network)<p>",
		render_form_text_area_as_html('banlist', $banList, 12, 50),
		"<br>",
		q{<input type="submit" name="Save" value="Save">},
		"<hr>\n",
		render_goto_bar_as_html(""),
		$request_state{+RS_CGI}->endform,
		render_common_footer_as_html()
	);
}

sub action_write_updated_ban_list {
	print render_page_header_as_html(
		"", "Updating Banned list", "", ROBOTS_KEEP_OUT
	);

	return unless user_is_admin_or_render_error();

	my $fname = "$dir_data/banlist";
	my $newList = get_request_param("banlist", "#Empty file");

	if ($newList eq "") {
		print "<p>Empty banned list or error.";
		print "<p>Resubmit with at least one space character to remove.";
	}
	elsif ($newList =~ /^\s*$/s) {
		unlink($fname);
		print "<p>Removed banned list";
	}
	else {
		write_string_to_file($fname, $newList);
		print "<p>Updated banned list";
	}

	print render_common_footer_as_html();
}

# Edit preferences.

sub action_open_preferences_editor {

	my $recentName = $config{rc_name};
	$recentName =~ s/_/ /g;

	do_new_login() if $request_state{+RS_USER_ID} < 400;

	print(
		render_page_header_as_html(
			"", "Editing Preferences", "", ROBOTS_KEEP_OUT
		),
		render_form_start_as_html("edit_prefs"),
		"\n",
		"<b>User Information:</b>\n",
		"<br>Your User ID number: $request_state{+RS_USER_ID} " .
		"<b>(Needed to log back in.)</b>\n",
		"<br>UserName: ",
		render_form_text_input_as_html('username', "", 20, 50),
		" (blank to remove, or valid page name)",
		"<br>Set Password: ",
		q{<input type="password" name="p_password" value="*" size=15 maxlength=50>},
		" (blank to remove password)",
		"<br>(Passwords are only used for sharing user IDs",
		" and preferences between multiple systems.",
		" Passwords are completely optional.)"
	);

	if ($config{admin_pass} ne "") {
		print(
			"<br>Administrator Password: ",
			'<input type="password" name="p_adminpw" value="*" size=15 maxlength=50>',
			" (blank to remove password)",
			"<br>(Administrator passwords are used for special maintenance.)"
		);
	}

	print(
		"<hr><b>$recentName:</b>\n",
		"<br>Default days to display: ",
		render_form_text_input_as_html('rcdays', $config{rc_default_days}, 4, 9),
		"<br>",
		render_form_checkbox_as_html(
			'rcnewtop', $config{recent_on_top}, 'Most recent changes on top'
		),
		"<br>",
		render_form_checkbox_as_html(
			'rcall', 0, 'Show all changes (not just most recent)'
		)
	);

	my %labels = (
		0 => 'Hide minor edits',
		1 => 'Show minor edits',
		2 => 'Show only minor edits'
	);

	print(
		"<br>Minor edit display: ",
		$request_state{+RS_CGI}->popup_menu(
			-name   => 'p_rcshowedit',
			-values => [0, 1, 2],
			-labels => \%labels,
			-default => get_request_param("rcshowedit", $config{show_minor_edits})
		),
		"<br>",
		render_form_checkbox_as_html(
			'rcchangehist', 1, 'Use "changes" as link to history'
		),
	);

	if ($config{allow_diff}) {
		print(
			"<hr><b>Differences:</b>\n",
			"<br>",
			render_form_checkbox_as_html(
				'diffrclink', 1, "Show (diff) links on $recentName"
			),
			"<br>",
			render_form_checkbox_as_html(
				'alldiff',  0, 'Show differences on all pages'
			),
			"  (",
			render_form_checkbox_as_html(
				'norcdiff', 1, "No differences on $recentName"
			),
			")"
		);

		%labels = (1 => 'Major', 2 => 'Minor', 3 => 'Author');
		print(
			"<br>Default difference type: ",
			$request_state{+RS_CGI}->popup_menu(
				-name   => 'p_defaultdiff',
				-values => [1, 2, 3],
				-labels => \%labels,
				-default => get_request_param("defaultdiff", 1)
			)
		);
	}

	print(
		"<hr><b>Misc:</b>\n",
		"<br>Server time: ",
		render_date_time_as_text($^T - $request_state{+RS_TIME_ZONE_OFFSET}),
		"<br>Time Zone offset (hours): ",
		render_form_text_input_as_html('tzoffset', 0, 4, 9),
		"<br>",
		render_form_checkbox_as_html(
			'editwide', 1, 'Use 100% wide edit area (if supported)'
		),
		"<br>Edit area rows: ",
		render_form_text_input_as_html('editrows', 20, 4, 4),
		" columns: ",
		render_form_text_input_as_html('editcols', 65, 4, 4),
		"<br>",
		render_form_checkbox_as_html('toplinkbar', 1, 'Show link bar on top'),
		"<br>",
		render_form_checkbox_as_html(
			'linkrandom', 0, 'Add "Random Page" link to link bar'
		),
	);

	if ($config{allow_user_css}) {
		print(
			"<br>Site-wide custom CSS (don't put &lt;style&gt; tags in here)<br>",
			q{<textarea name="p_css" rows="4" cols="65">},
			($request_state{+RS_USER_DATA}{+USER_CSS} || ''),
			q{</textarea>},
		);
	}

	my %data;
	$data{footer} = (
		"<br>" .
		q{<input type="submit" name="Save" value="Save">} .
		"<hr>\n" .
		render_goto_bar_as_html("") .
		$request_state{+RS_CGI}->endform
	);

	print render_template_as_html("snip-footer.tt2", \%data);
}

sub action_write_updated_preferences {
	# All link bar settings should be updated before printing the header.
	set_user_pref_from_request_bool("toplinkbar");
	set_user_pref_from_request_bool("linkrandom");

	print(
		render_page_header_as_html(
			"", "Saving Preferences", "", ROBOTS_KEEP_OUT
		),
		"<br>"
	);

	if ($request_state{+RS_USER_ID} < UID_MINLEGAL) {
		print "<b>Invalid user ID $request_state{+RS_USER_ID}, preferences not saved.</b>";

		if ($request_state{+RS_USER_ID} == UID_ENOCOOKIE) {
			print "<br>(Preferences require cookies, but no cookie was sent.)";
		}

		print render_common_footer_as_html();
		return;
	}

	my $username = get_request_param("p_username", "");

	if ($config{allow_free_links}) {
		$username =~ s/^\[\[(.+)\]\]/$1/;    # Remove [[ and ]] if added
		$username = ucfirst($username);
	}

	if ($username eq "") {
		print "UserName removed.<br>";
		$request_state{+RS_USER_DATA}{+USER_NAME} = undef;
	}
	elsif ((!$config{allow_free_links}) and (!($username =~ /^$pattern_link$/o))) {
		print "Invalid UserName $username: not saved.<br>\n";
	}
	elsif (
		$config{allow_free_links} and (!($username =~ /^$pattern_free_link$/o))
	) {
		print "Invalid UserName $username: not saved.<br>\n";
	}
	elsif (length($username) > 50) {    # Too long
		print "UserName must be 50 characters or less. (not saved)<br>\n";
	}
	else {
		print "UserName $username saved.<br>";
		$request_state{+RS_USER_DATA}{+USER_NAME} = $username;
	}

	my $password = get_request_param("p_password", "");

	if ($password eq "") {
		print "Password removed.<br>";
		$request_state{+RS_USER_DATA}{+USER_PASSWORD} = undef;
	}
	elsif ($password ne "*") {
		print "Password changed.<br>";
		$request_state{+RS_USER_DATA}{+USER_PASSWORD} = $password;
	}

	if ($config{admin_pass} ne "") {
		$password = get_request_param("p_adminpw", "");
		if ($password eq "") {
			print "Administrator password removed.<br>";
			$request_state{+RS_USER_DATA}{+USER_ADMIN_PASSWORD} = undef;
		}
		elsif ($password ne "*") {
			print "Administrator password changed.<br>";
			$request_state{+RS_USER_DATA}{+USER_ADMIN_PASSWORD} = $password;
			if (user_is_admin()) {
				print "User has administrative abilities.<br>";
			}
			else {
				print(
					"User <b>does not</b> have administrative abilities. ",
					"(Password does not match administrative password(s).)<br>"
				);
			}
		}
	}

	set_user_pref_from_request_number("rcdays", 0, 0, 999999);
	set_user_pref_from_request_bool("rcnewtop");
	set_user_pref_from_request_bool("rcall");
	set_user_pref_from_request_bool("rcchangehist");
	set_user_pref_from_request_bool("editwide");

	if ($config{allow_diff}) {
		set_user_pref_from_request_bool("norcdiff");
		set_user_pref_from_request_bool("diffrclink");
		set_user_pref_from_request_bool("alldiff");
		set_user_pref_from_request_number("defaultdiff", 1, 1, 3);
	}

	set_user_pref_from_request_number("rcshowedit", 1, 0,    2);
	set_user_pref_from_request_number("tzoffset",   0, -999, 999);
	set_user_pref_from_request_number("editrows",   1, 1,    999);
	set_user_pref_from_request_number("editcols",   1, 1,    999);
	set_user_pref_from_request_text("css") if $config{allow_user_css};

	print(
		"Server time: ",
		render_date_time_as_text($^T - $request_state{+RS_TIME_ZONE_OFFSET}),
		"<br>"
	);

	$request_state{+RS_TIME_ZONE_OFFSET} = (
		get_request_param("tzoffset", 0) * (60 * 60)
	);
	print "Local time: ", render_date_time_as_text($^T), "<br>";

	save_user_data();
	print "<b>Preferences saved.</b>", render_common_footer_as_html();
}

# Edit links.

sub action_open_links_editor {
	print render_page_header_as_html(
		"", "Editing Links", "", ROBOTS_KEEP_OUT
	);

	if ($config{allow_editors_to_delete}) {
		return unless user_is_editor_or_render_error();
	}
	else {
		return unless user_is_admin_or_render_error();
	}

	print(
		render_form_start_as_html("edit_links"),
		"\n",
		"<b>Editing/Deleting page titles:</b><br>\n",
		"<p>Enter one command on each line.  Commands are:<br>",
		"<tt>!PageName</tt> -- deletes the page called PageName<br>\n",
		"<tt>=OldPageName=NewPageName</tt> -- Renames OldPageName ",
		"to NewPageName and updates links to OldPageName.<br>\n",
		"<tt>|OldPageName|NewPageName</tt> -- Changes links to OldPageName ",
		"to NewPageName.",
		" (Used to rename links to non-existing pages.)<br>\n",
		render_form_text_area_as_html('commandlist', "", 12, 50),
		$request_state{+RS_CGI}->checkbox(
			-name     => "p_changerc",
			-override => 1,
			-checked  => 1,
			-label    => "Edit $config{rc_name}"
		),
		"<br>\n",
		$request_state{+RS_CGI}->checkbox(
			-name     => "p_changetext",
			-override => 1,
			-checked  => 1,
			-label    => "Substitute text for rename"
		),
		"<br>", q{<input type="submit" name="Edit" value="Edit">},
		"<hr>\n",
		$request_state{+RS_CGI}->endform,
		render_common_footer_as_html()
	);
}

sub action_write_updated_links {
	print render_page_header_as_html(
		"", "Updating Links", "", ROBOTS_KEEP_OUT
	);

	if ($config{allow_editors_to_delete}) {
		return unless user_is_editor_or_render_error();
	}
	else {
		return unless user_is_admin_or_render_error();
	}

	my $commandList = get_request_param("commandlist", "");

	my $doRC = get_request_param("p_changerc",  "0");
	$doRC = 1 if ($doRC eq "on");

	my $doText = get_request_param("p_changetext", "0");
	$doText = 1 if ($doText eq "on");

	if ($commandList eq "") {
		print "<p>Empty command list or error.";
	}
	else {
		run_page_and_link_update_script($commandList, $doRC, $doText);
		print "<p>Finished command list.";
	}

	print render_common_footer_as_html();
}

# Edit pages.

sub action_open_page_editor {
	my ($id, $isConflict, $oldTime, $newText, $preview) = @_;

	unless (user_can_edit($id, 1)) {
		print render_page_header_as_html(
			"", "Editing Denied", "", ROBOTS_KEEP_OUT
		);

		if (user_is_banned()) {
			print(
				"Editing not allowed: user, ip, or network is blocked.",
				"<p>Contact the system administrator for more information."
			);
		}
		else {
			print "Editing not allowed: $config{site_name} is read-only.";
		}

		print render_common_footer_as_html();
		return;
	}

	open_or_create_page($id);
	open_default_text();

	my $pageTime = $request_state{+RS_SECTION}{+SECT_TIMESTAMP_CHANGE};
	my $header   = "Editing $id";

	# Old revision handling
	my $revision = get_request_param("revision", "");
	$revision =~ s/\D//g;    # Remove non-numeric chars
	if ($revision ne "") {
		open_kept_revisions(PAGE_TEXT_DEFAULT);
		if (defined $request_state{+RS_KEPT_REVISION_HASH}{$revision}) {
			open_kept_revision($revision);
			$header = "Editing Revision $revision of $id";
		}
		else {
			$revision = "";

			# Later look for better solution, like error message?
		}
	}

	my $oldText = $request_state{+RS_TEXT}{+TEXT_TEXT};

	if ($preview and !$isConflict) {
		$oldText = $newText;
	}

	my $editRows = get_request_param("editrows", 20);
	my $editCols = get_request_param("editcols", 65);

	print render_page_header_as_html(
		"", quote_html($header), "", ROBOTS_KEEP_OUT
	);

	if ($revision ne "") {
		print(
			"\n<b>Editing old revision $revision.  Saving this page will" .
			" replace the latest revision with this text.</b><br>"
		);
	}

	if ($isConflict) {
		$editRows -= 10 if ($editRows > 19);
		print "\n<H1>Edit Conflict!</H1>\n";
		if ($isConflict > 1) {

			# The main purpose of a new warning is to display more text
			# and move the save button down from its old location.
			print "\n<H2>(This is a new conflict)</H2>\n";
		}

		print(
			"<p><strong>Someone saved this page after you started editing.",
			" The top textbox contains the saved text.",
			" Only the text in the top textbox will be saved.</strong><br>\n",
			" Scroll down to see your edited text.<br>\n",
			"Last save time: ",
			render_date_time_as_text($oldTime),
			" (Current time is: ",
			render_date_time_as_text($^T),
			")<br>\n"
		);
	}

	print(
		render_form_start_as_html("save_page"),
		render_hidden_input_as_html("title",       $id),         "\n",
		render_hidden_input_as_html("oldtime",     $pageTime),   "\n",
		render_hidden_input_as_html("oldconflict", $isConflict), "\n"
	);

	if ($revision ne "") {
		print render_hidden_input_as_html("revision", $revision), "\n";
	}

	print render_form_text_area_as_html('text', $oldText, $editRows, $editCols);

	my $summary = get_request_param("summary", "*");
	print(
		"<p>Summary:",
		$request_state{+RS_CGI}->textfield(
			-name      => 'summary',
			-default   => $summary,
			-override  => 1,
			-size      => 60,
			-maxlength => 200
		)
	);

	print "<br>";
	if (get_request_param("recent_edit") eq "on") {
		print(
			$request_state{+RS_CGI}->checkbox(
				-name    => 'recent_edit',
				-checked => 1,
				-label   => 'This change is a minor edit.'
			)
		);
	}
	else {
		print(
			$request_state{+RS_CGI}->checkbox(
				-name    => 'recent_edit',
				-label   => 'This change is a minor edit.'
			)
		);
	}

	print(
		"<br>(Minor edits are structural or typographical changes.)",
		"<br>(Major edits include new pages and substantial content changes.)",
	);

	print q{<br><input type="submit" name="Save" value="Save">};

	my $userName = get_request_param("username", "");
	if ($userName ne "") {
		print(
			" (Your user name is " .
			render_unnamed_page_link_as_html($userName) .
			") "
		);
	}
	else {
		print(
			" (Visit " .
			render_prefs_link_as_html() .
			" to set your user name, or " .
			render_login_link_as_html() .
			" to log in.) "
		);
	}

	print q{<input type="submit" name="Preview" value="Preview">};

	if ($isConflict) {
		print(
			"\n<br><hr><p><strong>This is the text you submitted:</strong><p>",
			render_form_text_area_as_html('newtext', $newText, $editRows, $editCols),
			"<p>\n"
		);
	}

	print "<hr>\n";

	if ($preview) {
		print "<h2>Preview:</h2>\n";
		if ($isConflict) {
			print(
				"<b>NOTE: This preview shows the other author's revision.",
				"</b><hr>\n"
			);
		}

		$request_state{+RS_MAIN_PAGE} = $id;
		$request_state{+RS_MAIN_PAGE} =~ s!/.*!!;  # Remove subpage

		print(
			render_wiki_data_as_html($oldText) .
			"<hr>\n",
			"<h2>Preview only, not yet saved</h2>\n"
		);
	}

	my %data;
	$data{footer} = (
		render_history_link_as_html($id, "View other revisions") .
		"<br>\n" .
		render_goto_bar_as_html($id) .
		$request_state{+RS_CGI}->endform
	);

	print render_template_as_html("snip-footer.tt2", \%data);
}

sub action_write_updated_page {
	my $string      = get_request_param("text",        undef);
	my $id          = get_request_param("title",       "");
	my $summary     = get_request_param("summary",     "");
	my $oldtime     = get_request_param("oldtime",     "");
	my $oldconflict = get_request_param("oldconflict", "");
	my $isEdit      = 0;
	my $editTime    = $^T;
	my $authorAddr  = $ENV{REMOTE_ADDR};

	unless (user_can_edit($id, 1)) {

		# This is an internal interface--we don't need to explain
		print render_error_page_as_html("Editing not allowed for $id.");
		return;
	}

	if ($id eq "SampleUndefinedPage") {
		print render_error_page_as_html("SampleUndefinedPage cannot be defined.");
		return;
	}

	if ($id eq "Sample_Undefined_Page") {
		print render_error_page_as_html(
			"[[Sample Undefined Page]] cannot be defined."
		);
		return;
	}

	$summary =~ s/\s+/ /g;
	$summary =~ s/^\s+//;
	$summary =~ s/\s+$//;

	# Add a newline to the end of the string (if it doesn't have one)
	$string .= "\n" unless $string =~ /\n$/;

	# Fucking spammers.
	if (
		$string =~ m!
			( hakdata | 82\.165\.4\.19 | suchmaschinenoptimierung
			| emmss\.com | chongqing | 211\.158\.6\.107
			| 0020\.net | 61\.135\.129\.95
			| kykdz\.com | 211\.154\.211\.\d+
			| freewebpage\.org | 65\.208\.179\.220
			| svs\.cn
			| crestron\.cn
			| ganzaoji | 218\.244\.47\.24
			| huola\.com | sexyongpin | mianfei | midiwu | nanting
			| news123\.org | guilinhotel
			| shop263.com | 218\.244\.47\.217
			| www\.wjmgy\.com | 61\.135\.136\.130
			| www\.etoo\.cn | 210\.192\.124\.153
			| www\.timead\.net
			| www\.paite\.net
			| www\.rr365\.net
			| www\.ronren\.com
			| csnec\.net | \d+\.com | bjzyy\.com | lifuchao\.com
			| pfxb\.com | qzkfw\.com | rxbkfw\.com | xyxy\.com | zhqzw\.com
			| 210\.51\.188\.148 | 218\.30\.96\.\d+ | 61\.152\.94\.121
			| \.\d+dragon\.com
			| u-tokyo\.ac\.jp | mycv\.com | cvdiy\.com | mycv\.cn
			| hpvsos\.(?:com|net) | aakk\.org | xbcn\.org
			| bead-diy\.com | royalty-crystal\.com | adlernunu\.blogcn\.com
			| asiaec\.com | windowstime\.com | pggreen\.com
			| buy-?(carisoprodol|cialis|floricet|levitra|propecia|soma|tramadol|viagra|adipex|ambien)
			| mujweb\.cz
			| phentermine | comunalia\.com | gayhomes\.net
			| chenado\.info
			| freeforen\.com | hrentut\.org
			| i\s(?:do\snot|don\'t)\shave\smoney\s\S+\s\S+\s\S+\s\S+\smy\schildren
			)
		!ix
		or $string =~ m!
			( Ss+Ss+
			)
		!x
	) {
		print render_error_page_as_html(
			"Error submitting your data.",
			"Please contact the web master if this persists."
		);
		return;
	}

	# Lock before getting old page to prevent races
	request_main_lock() or confess "Could not get editing lock";

	# Consider extracting lock section into sub, and eval-wrap it?
	# (A few called routines can die, leaving locks.)
	open_or_create_page($id);
	open_default_text();

	my $old    = $request_state{+RS_TEXT}{+TEXT_TEXT};
	my $oldrev = $request_state{+RS_SECTION}{+SECT_REVISION};
	my $pgtime = $request_state{+RS_SECTION}{+SECT_TIMESTAMP_CHANGE};

	my $preview = 0;
	$preview = 1 if (get_request_param("Preview", "") ne "");

	if (!$preview and ($old eq $string)) {    # No changes (ok for preview)
		release_main_lock();
		redirect_browse_page($id, "", 1);
		return;
	}

	# Later extract comparison?
	my $newAuthor;
	if (
		($request_state{+RS_USER_ID} > 399)
		||
		($request_state{+RS_SECTION}{+SECT_USER_ID} > 399)
	) {
		# Known user(s).
		$newAuthor = (
			$request_state{+RS_USER_ID} ne $request_state{+RS_SECTION}{+SECT_USER_ID}
		);
	}
	else {
		# Hostname fallback.
		$newAuthor = ($request_state{+RS_SECTION}{+SECT_USER_IP} ne $authorAddr);
		release_main_lock();
		print render_error_page_as_html(
			"Error submitting your data.",
			"Please be sure to log in first."
		);
		return;
	}

	$newAuthor = 1 if $oldrev == 0;   # New page
	$newAuthor = 0 unless $newAuthor; # Standard flag form, not empty
																		# Detect editing conflicts and resubmit edit
	if (($oldrev > 0) and ($newAuthor and ($oldtime != $pgtime))) {
		release_main_lock();

		if ($oldconflict > 0) {         # Conflict again...
			action_open_page_editor($id, 2, $pgtime, $string, $preview);
		}
		else {
			action_open_page_editor($id, 1, $pgtime, $string, $preview);
		}

		return;
	}

	if ($preview) {
		release_main_lock();
		action_open_page_editor($id, 0, $pgtime, $string, 1);
		return;
	}

	my $user = get_request_param("username", "");

	if (get_request_param("recent_edit", "") eq 'on') {
		$isEdit = 1;
	}

	unless ($isEdit) {
		set_page_cache('oldmajor', $request_state{+RS_SECTION}{+SECT_REVISION});
	}

	if ($newAuthor) {
		set_page_cache('oldauthor', $request_state{+RS_SECTION}{+SECT_REVISION});
	}

	save_keep_section();
	expire_keep_file();

	if ($config{allow_diff}) {
		update_diffs($id, $editTime, $old, $string, $isEdit, $newAuthor);
	}

	$request_state{+RS_TEXT}{+TEXT_TEXT}      = $string;
	$request_state{+RS_TEXT}{+TEXT_IS_MINOR_REV}     = $isEdit;
	$request_state{+RS_TEXT}{+TEXT_IS_NEW_AUTHOR} = $newAuthor;
	$request_state{+RS_TEXT}{+TEXT_SUMMARY}   = $summary;
	$request_state{+RS_SECTION}{+SECT_USER_HOST}   = get_remote_host(1);

	save_default_text();
	save_page_to_file();
	append_recent_changes_log(
		$id,
		$summary,
		$isEdit,
		$editTime,
		$user,
		$request_state{+RS_SECTION}{+SECT_USER_HOST}
	);

	if ($config{use_html_cache}) {
		# Old cache copy is invalid.
		unlink_html_cache($id);

		# If this is a new page, uncache pages linked to it.
		if (
			$request_state{+RS_PAGE}{+PAGE_REVISION} == 1
		) {
			clear_cached_pages_linking_to($id);
		}
	}

	# Regenerate index on next request.
	if (
		$config{use_page_index_file} and
		($request_state{+RS_PAGE}{+PAGE_REVISION} == 1)
	) {
		unlink($config{file_page_index});
	}

	release_main_lock();
	redirect_browse_page($id, "", 1);
}

######################
### PAGE RENDERERS ###

sub render_template_as_html {
	my ($template_file, $template_data) = @_;

	my $template = Template->new(
		{
			INCLUDE_PATH  => $config{dir_templates},
			TRIM          => 1,
			PRE_CHOMP     => 1,
			POST_CHOMP    => 1,
		}
	);

	$template->context->define_vmethod( 'scalar', 'ucfirst', sub { ucfirst($_[0]) } );

	$template_data->{base_url} = $config{full_url};
	my $output = "";
	$template->process(
		$template_file,
		$template_data,
		\$output
	) or confess $template->error;

	return $output;
}

# TODO - These are prime candidates for templates.

sub render_login_page_as_html {
	my $title = "Log In";

	my %template_data;
	template_set_common_header_data(\%template_data, $title);
	template_set_title_data(\%template_data, "", $title);
	template_set_meta_robot_data(\%template_data, ROBOTS_KEEP_OUT);
	template_set_common_footer_html(\%template_data);

	return render_template_as_html("page-login.tt2", \%template_data);
}

sub render_wiki_data_as_html { # TODO
	my ($pageText) = @_;

	$request_state{+RS_SAVED_HTML} = [];
	$request_state{+RS_SAVED_URL_IDX} = {};

	# TODO - Perl rendering must come first.
	if ($config{allow_raw_html}) {
		$pageText =~ s/<html>((.|\n)*?)<\/html>/store_raw_html($1)/ige;
	}

	$pageText = quote_html($pageText);

	# Join lines with backslash at end.
	$pageText =~ s/\\ *\r?\n/ /g;

	# Multi-line markup.
	$pageText = render_common_markup_as_html($pageText, RENDER_IMAGES, 0);

	# Line-oriented markup.
	$pageText = render_line_based_markup_as_html($pageText);

	# Restore saved text.
	$pageText =~ s/$FS(\d+)$FS/$request_state{+RS_SAVED_HTML}[$1]/geo;

	# Restore nested saved text.
	$pageText =~ s/$FS(\d+)$FS/$request_state{+RS_SAVED_HTML}[$1]/geo;

	return $pageText;
}

sub render_page_index_as_html {
	my $title = "Index of All Pages";

	my %template_data;
	template_set_common_header_data(\%template_data, $title);
	template_set_title_data(\%template_data, "", $title);
	template_set_meta_robot_data(\%template_data, ROBOTS_KEEP_OUT);
	template_set_common_footer_html(\%template_data);

	my @page_list = get_all_pages_for_entire_site();
	$template_data{page_list} = render_list_of_page_names_as_html(@page_list);

	return render_template_as_html("page-list.tt2", \%template_data);
}

sub render_error_page_as_html {
	my @errors = @_;

	my $title = "An Error Has Occurred";

	my %template_data = ( errors => \@_ );

	template_set_common_header_data(\%template_data, $title);
	template_set_title_data(\%template_data, "", $title);
	template_set_meta_robot_data(\%template_data, ROBOTS_KEEP_OUT);
	template_set_common_footer_html(\%template_data);

	return render_template_as_html("page-error.tt2", \%template_data);
}

sub render_recent_changes_page_as_html {

	my %template_data;

	my $request_start_time = get_request_param("from", 0);
	if ($request_start_time > 0) {
		$template_data{start_header} = (
			"since " . render_date_time_as_text($request_start_time)
		);
	}
	elsif (
		my $daysago = (
			get_request_param("days", 0)
			|| get_request_param("rcdays", 0)
			|| $config{rc_default_days}
			|| 7
		)
	) {
		$request_start_time = $^T - ((24 * 60 * 60) * $daysago);
		$template_data{start_header} = (
			"in the last $daysago day" .
			(($daysago == 1) ? "" : "s")
		);
	}

	unless (-f $config{file_recent_changes_log}) {
		return render_error_page_as_html(
			"<p>" .
			"<strong>No $config{rc_name} log file " .
			"at $config{file_recent_changes_log}.</strong>" .
			"<p>"
		);
	}

	# Read the recent changes log.

	my ($rc_log_status, $rc_log_data) = read_file($config{file_recent_changes_log});

	unless ($rc_log_status) {
		return render_error_page_as_html(
			"<p>" .
			"<strong>Could not open $config{rc_name} log file " .
			"($config{file_recent_changes_log}):</strong> " .
			"Error was: <pre>$!</pre>" .
			"</p>" .
			"<p>This error is normal if no changes have been made.</p>"
		);
	}

	my @rc_log_items = map { decode_json($_) } split(/\n/, $rc_log_data);

	my $first_ts = 0;
	$first_ts = $rc_log_items[0]{+RC_TIMESTAMP} if @rc_log_items;

	# Read the old recent changes log, if needed.
	# Empty log, or the earliest timestamp is later than the start time.

	if ($first_ts == 0 or $request_start_time <= $first_ts) {
		($rc_log_status, my $old_rc_log_data) = read_file(
			$config{file_old_recent_changes_log}
		);

		unless ($rc_log_status) {
			return render_error_page_as_html(
				"<p>" .
				"<strong>Could not open old $config{rc_name} log file " .
				"($config{file_recent_changes_log}):</strong> " .
				"Error was: <pre>$!</pre>" .
				"</p>"
			);
		}

		unshift(
			@rc_log_items,
			map { decode_json($_) }
			split(/\n/, $old_rc_log_data)
		);
	}

	my $last_ts = 0;
	$last_ts = $rc_log_items[-1]{+RC_TIMESTAMP} if @rc_log_items;

	my $id_only = get_request_param("rcidonly", "");
	if ($id_only ne "") {
		$template_data{id_only} = render_script_link_as_html($id_only, $id_only);
	}

	$template_data{display_options} = join(
		" | ",
		map {
			render_script_link_as_html(
				"action/rc?days=$_", "$_ day" . (($_ == 1) ? "" : "s")
			)
		}
		@{$config{rc_days_options}}
	);

	$template_data{next_page} = render_script_link_as_html(
		"action/rc?from=$last_ts",
		"List new changes starting from " . render_date_time_as_text($last_ts)
	);

	# Log fiter parameters.

	my $show_minor_edits = get_request_param(
		"showedit",
		get_request_param(
			"rcshowedit",
			$config{show_minor_edits}
		)
	);

	my $show_all = get_request_param("all", get_request_param("rcall", 0));

	my $show_recent_on_top = get_request_param(
		"newtop",
		get_request_param("rcnewtop", $config{recent_on_top})
	);

	# Filter the log.

	my %last_change_time;
	my %changes_per_page;
	my %displayable_changes;

	my $rc_index = @rc_log_items;
	while ($rc_index--) {
		my %rc_line = %{ $rc_log_items[$rc_index] };

		# We've gone too far back.  Bye!
		last if $rc_line{+RC_TIMESTAMP} < $request_start_time;

		# 0 = No minor edits.
		next if $show_minor_edits == 0 and $rc_line{+RC_IS_MINOR_REV};

		# 2 = Only minor edits.
		next if $show_minor_edits == 2 and !$rc_line{+RC_IS_MINOR_REV};

		# Not showing all changes for the page (just the last one).
		next if !$show_all and $rc_line{+RC_TIMESTAMP} < $last_change_time{timestamp};

		# Not the ID we're looking for.
		next if $id_only ne "" and $rc_line{+RC_PAGE_ID} ne $id_only;

		# This one's displayable.  Format the fields and save the line.

		if ($config{allow_diff} and get_request_param("diffrclink", 1)) {
			$rc_line{+RC_LINK} = render_diff_link_as_html(
				4,
				$rc_line{+RC_PAGE_ID},
				"(diff)",
				""
			) . " ";
		}

		$rc_line{+RC_LINK} .= render_unnamed_page_link_as_html($rc_line{+RC_PAGE_ID});

		$rc_line{+RC_TIME} = render_time_as_text($rc_line{+RC_TIMESTAMP});

		if (!$show_all and $changes_per_page{$rc_line{+RC_PAGE_ID}} > 1) {
			$rc_line{+RC_COUNT} = "($changes_per_page{$rc_line{+RC_PAGE_ID}} ";
			if (get_request_param("rcchangehist", 1)) {
				$rc_line{+RC_COUNT} .= render_history_link_as_html(
					$rc_line{+RC_PAGE_ID},
					"changes"
				);
			}
			else {
				$rc_line{+RC_COUNT} .= "changes";
			}
			$rc_line{+RC_COUNT} .= ")";
		}

		$rc_line{+RC_EDIT} = "<em>(edit)</em>" if $rc_line{+RC_IS_MINOR_REV};

		unless (
			defined($rc_line{+RC_SUMMARY}) and
			length($rc_line{+RC_SUMMARY}) and
			$rc_line{+RC_SUMMARY} ne "*"
		) {
			$rc_line{+RC_SUMMARY} = "(no summary, tch tch tch)";
		}

		if (defined($rc_line{+RC_USER_NAME}) and defined($rc_line{+RC_USER_ID})) {
			$rc_line{+RC_AUTHOR} = render_author_link_as_html(
				$rc_line{+RC_EDIT_HOST}, $rc_line{+RC_USER_NAME}, $rc_line{+RC_USER_ID}
			);
		}
		else {
			$rc_line{+RC_AUTHOR} = render_author_link_as_html($rc_line{+RC_EDIT_HOST}, "", 0);
		}

		my $sort_date = strftime("%F", gmtime($rc_line{+RC_TIMESTAMP}));
		if ($show_recent_on_top) {
			push @{$displayable_changes{$sort_date}}, \%rc_line;
		}
		else {
			unshift @{$displayable_changes{$sort_date}}, \%rc_line;
		}

		$last_change_time{$rc_line{+RC_PAGE_ID}} ||= $rc_line{+RC_TIMESTAMP};
		$changes_per_page{$rc_line{+RC_PAGE_ID}}++;
	}

	if ($show_recent_on_top) {
		$template_data{change_dates} = [
			sort { $b cmp $a } keys %displayable_changes
		];
	}
	else {
		$template_data{change_dates} = [ sort keys %displayable_changes ];
	}

	$template_data{changes} = \%displayable_changes;

	$template_data{page_render_time} = render_date_time_as_text($^T);

	template_set_common_header_data(
		\%template_data,
		"Changes $template_data{start_header}"
	);

	template_set_common_footer_html(\%template_data);

	return render_template_as_html("page-recent-changes.tt2", \%template_data);
}

sub render_redirect_page_as_html { # TODO
	my ($newid, $name, $isEdit) = @_;

	# Normally get URL from script, but allow override.
	my $url = (
		($config{full_url} || $request_state{+RS_CGI}->url(-full => 1)) .
		$newid
	);

	my $html;
	if ($config{redir_type} < REDIR_NONE) {
		# Use CGI.pm
		if ($config{redir_type} == REDIR_CGIPM) {
			# NOTE: do NOT use -method (does not work with old CGI.pm versions)
			# Thanks to Daniel Neri for fixing this problem.
			$html = $request_state{+RS_CGI}->redirect(-uri => $url);
		}
		elsif ($config{redir_type} == REDIR_SCRIPT) {
			# Minimal header.
			$html = "Status: 302 Moved\n";
			$html .= "Location: $url\n";
			$html .= "Content-Type: text/html; charset=UTF-8\n";    # Needed for browser failure
			$html .= "\n";
		}
		else {
			confess "unknown redirection type: $config{redir_type}";
		}

		$html .= "\nYour browser should go to the $newid page.";
		$html .= "  If it does not, click <a href=\"$url\">$name</a>";
		$html .= " to continue.";
	}
	else {
		if ($isEdit) {
			$html = render_page_header_as_html(
				"", "Thanks for editing...", "", "norobots"
			);
			$html .= "Thank you for editing <a href=\"$url\">$name</a>.";
		}
		else {
			$html = render_page_header_as_html(
				"", "Link to another page...", "", "norobots"
			);
		}

		$html .= "\n<p>Follow the <a href=\"$url\">$name</a> link to continue.";
	}

	return $html;
}

sub render_search_results_page_as_html {
	my $search_string = shift;
	my @search_results = @_;

	my $title = "Search results for: $search_string";

	my %template_data;
	template_set_common_header_data(\%template_data, $title);
	template_set_title_data(\%template_data, "", $title);
	template_set_meta_robot_data(\%template_data, ROBOTS_KEEP_OUT);
	template_set_common_footer_html(\%template_data);

	$template_data{page_list} = render_list_of_page_names_as_html(@search_results);

	return render_template_as_html("page-list.tt2", \%template_data);
}

sub render_links_page_as_html {

	my $title = "Full Link List";

	my %template_data;
	template_set_common_header_data(\%template_data, $title);
	template_set_title_data(\%template_data, $title);
	template_set_meta_robot_data(\%template_data, ROBOTS_KEEP_OUT);
	template_set_common_footer_html(\%template_data);

	# A list of pages that exist.
	my %page_exists;
	$page_exists{$_} = 1 foreach get_all_pages_for_entire_site();

	my $include_container_page = get_request_param("names",    1);
	my $edit_unknown_pages     = get_request_param("editlink", 1);

	my %link_tree;
	my %linked_to;

	# Each $page_links = page_name page_links, separated by spaces.
	foreach my $page_links (get_all_links_for_entire_site()) {
		my @links_in_page;

		foreach my $page_link (split(' ', $page_links)) {
			my $link;

			# Determine & format the link.
			if ($page_link =~ /\:/) {
				# URL or inter-wiki form.
				if ($page_link =~ /$pattern_url/) {
					($link, my $extra) = render_url_link_as_html_and_punct($page_link);
				}
				else {
					($link, my $extra) = render_inter_page_link_as_html_and_punct($page_link);
				}
			}
			else {
				# Intra-wiki form.
				if ($page_exists{$page_link}) {
					$link = render_unnamed_page_link_as_html($page_link);
				}
				else {
					$link = $page_link;
					if ($edit_unknown_pages) {
						$link .= render_edit_link_as_html($page_link, "?");
					}
				}
			}

			push @links_in_page, $link;
		}

		my $page_link = shift(@links_in_page);
		if ($include_container_page) {
			$link_tree{$page_link}{$_} = 1 foreach @links_in_page;
		}
		else {
			$linked_to{$_} = 1 foreach @links_in_page;
		}
	}

	$template_data{linked_to} = \%linked_to;
	$template_data{link_tree} = \%link_tree;

	return render_template_as_html("page-links.tt2", \%template_data);
}

######################
### HTML RENDERERS ###

sub render_diff_text_as_html { # TODO
	my ($html) = @_;

	$html =~ s/\n--+//g;

	# Note: Need spaces before <br> to be different from diff section.
	$html =~ s/(^|\n)(\d+.*c.*)/$1 <br><strong>Changed: $2<\/strong><br>/g;
	$html =~ s/(^|\n)(\d+.*d.*)/$1 <br><strong>Removed: $2<\/strong><br>/g;
	$html =~ s/(^|\n)(\d+.*a.*)/$1 <br><strong>Added: $2<\/strong><br>/g;
	$html =~ s/\n((<.*\n)+)/render_diff_color_as_html($1,"ffffaf")/ge;
	$html =~ s/\n((>.*\n)+)/render_diff_color_as_html($1,"cfffcf")/ge;

	return $html;
}

sub render_diff_as_html { # TODO
	my ($diffType, $id, $rev, $newText) = @_;

	my $links     = "(";
	my $usecomma  = 0;
	my $major     = render_diff_link_as_html(1, $id, "major diff", "");
	my $minor     = render_diff_link_as_html(2, $id, "minor diff", "");
	my $author    = render_diff_link_as_html(3, $id, "author diff", "");

	my $useMajor  = 1;
	my $useMinor  = 1;
	my $useAuthor = 1;

	my $priorName;
	if ($diffType == 1) {
		$priorName = "major";
		$useMajor  = 0;
	}
	elsif ($diffType == 2) {
		$priorName = "minor";
		$useMinor  = 0;
	}
	elsif ($diffType == 3) {
		$priorName = "author";
		$useAuthor = 0;
	}

	my $diffText;
	if ($rev ne "") {

		# Note: open_kept_revisions must have been done by caller.
		# Later optimize if same as cached revision
		$diffText = find_kept_differences($newText, $rev, 1);    # 1 = get lock

		if ($diffText eq "") {
			$diffText = "(The revisions are identical or unavilable.)";
		}
	}
	else {
		$diffText = get_cache_diff($priorName);
	}

	$useMajor  = 0 if ($useMajor  and ($diffText eq get_cache_diff("major")));
	$useMinor  = 0 if ($useMinor  and ($diffText eq get_cache_diff("minor")));
	$useAuthor = 0 if ($useAuthor and ($diffText eq get_cache_diff("author")));
	$useMajor  = 0 if (
		(!defined(get_page_cache('oldmajor'))) or
		(get_page_cache('oldmajor') < 1)
	);

	$useAuthor = 0 if (
		(!defined(get_page_cache('oldauthor'))) or
		(get_page_cache('oldauthor') < 1)
	);

	if ($useMajor) {
		$links .= $major;
		$usecomma = 1;
	}

	if ($useMinor) {
		$links .= ", " if ($usecomma);
		$links .= $minor;
		$usecomma = 1;
	}

	if ($useAuthor) {
		$links .= ", " if ($usecomma);
		$links .= $author;
	}

	unless ($useMajor || $useMinor || $useAuthor) {
		$links .= "no other diffs";
	}

	$links .= ")";

	if ((!defined($diffText)) || ($diffText eq "")) {
		$diffText = "No diff available.";
	}

	if ($rev ne "") {
		return(
			"<b>Difference (from revision $rev to current revision)</b>\n" .
			"$links<br>" .
			render_diff_text_as_html($diffText) .
			"<hr>\n"
		);
	}

	if (
		($diffType != 2) and
		(
			(!defined(get_page_cache("old$priorName")))
			|| (get_page_cache("old$priorName") < 1)
		)
	) {
		return(
			"<b>No diff available--this is the first $priorName" .
			" revision.</b>\n$links<hr>"
		);
	}

	return(
		"<b>Difference (from prior $priorName revision)</b>\n" .
		"$links<br>" .
		render_diff_text_as_html($diffText) .
		"<hr>\n"
	);
}

sub render_diff_color_as_html { # TODO
	my ($diff, $color) = @_;

	$diff =~ s/(^|\n)[<>]/$1/g;
	$diff = quote_html($diff);

	# Do some of the Wiki markup rules:
	$request_state{+RS_SAVED_HTML} = [];
	$request_state{+RS_SAVED_URL_IDX} = {};

	# No images, all patterns
	$diff = render_common_markup_as_html($diff, SKIP_RENDERING_IMAGES, 1);

	# Restore saved text.
	$diff =~ s/$FS(\d+)$FS/$request_state{+RS_SAVED_HTML}[$1]/geo;

	# Restore nested saved text.
	$diff =~ s/$FS(\d+)$FS/$request_state{+RS_SAVED_HTML}[$1]/geo;

	$diff =~ s/\r?\n/<br>/g;

	return(
		"<table width=\"95\%\" bgcolor=#$color><tr><td>\n" .
		$diff .
		"</td></tr></table>\n"
	);
}

sub render_form_text_area_as_html { # TODO
	my ($name, $text, $rows, $cols) = @_;

	if (get_request_param("editwide", 1)) {
		return $request_state{+RS_CGI}->textarea(
			-name     => $name,
			-default  => $text,
			-rows     => $rows,
			-columns  => $cols,
			-override => 1,
			-style    => 'width:100%',
			-wrap     => 'virtual'
		);
	}

	return $request_state{+RS_CGI}->textarea(
		-name     => $name,
		-default  => $text,
		-rows     => $rows,
		-columns  => $cols,
		-override => 1,
		-wrap     => 'virtual'
	);
}

sub render_form_text_input_as_html { # TODO
	my ($name, $default, $size, $max) = @_;

	my $text = get_request_param($name, $default);

	return $request_state{+RS_CGI}->textfield(
		-name      => "p_$name",
		-default   => $text,
		-override  => 1,
		-size      => $size,
		-maxlength => $max
	);
}

sub render_form_checkbox_as_html { # TODO
	my ($name, $default, $label) = @_;

	my $checked = (get_request_param($name, $default) > 0);

	return $request_state{+RS_CGI}->checkbox(
		-name     => "p_$name",
		-override => 1,
		-checked  => $checked,
		-label    => $label
	);
}

sub render_common_markup_as_html { # TODO
	my ($text, $useImage, $doLines) = @_;
	local $_ = $text;

	# Do block markup, if not doing only line-oriented markup.
	if ($doLines < ONLY_LINE_ORIENTED_MARKUP) {
		# The <nowiki> tag stores text with no markup (except quoting HTML)
		s/\&lt;nowiki\&gt;((.|\n)*?)\&lt;\/nowiki\&gt;/store_raw_html($1)/ige;

		# The <pre> tag wraps the stored text with the HTML <pre> tag
		s/\&lt;pre\&gt;((.|\n)*?)\&lt;\/pre\&gt;/render_pre_as_stored_html($1)/ige;
		s/\&lt;code\&gt;((.|\n)*?)\&lt;\/code\&gt;/render_code_as_stored_html($1)/ige;
		s/\&lt;perl\&gt;\s*\n?((.|\n)*?)\&lt;\/perl\&gt;/render_perl_as_stored_html($1)/ige;
		s/\&lt;projects\&gt;\s*\n?((.|\n)*?)\&lt;\/projects\&gt;/render_projects_as_html($1)/ige;
		s/\&lt;outline\&gt;\s*\n?((.|\n)*?)\&lt;\/outline\&gt;/render_outline_as_html($1,"bullets")/ige;
		s/\&lt;outline-head\&gt;\s*\n?((.|\n)*?)\&lt;\/outline\&gt;/render_outline_as_html($1,"headers")/ige;
		s/\&lt;outline-todo\&gt;\s*\n?((.|\n)*?)\&lt;\/outline\&gt;/render_outline_as_html($1,"todo")/ige;
		s/\&lt;components\&gt;\s*\n?((.|\n)*?)\&lt;\/components\&gt;/render_components_as_html($1)/ige;

		if ($config{allow_unsafe_html}) {
			foreach my $t (@{$config{allowed_html_tag_pairs}}) {
				s/\&lt;$t(\s[^<>]+?)?\&gt;(.*?)\&lt;\/$t\&gt;/<$t$1>$2<\/$t>/gis;
			}

			foreach my $t (@{$config{allowed_html_tag_singletons}}) {
				s/\&lt;$t(\s[^<>]+?)?\&gt;/<$t$1>/gi;
			}
		}
		else {

			# Note that these tags are restricted to a single line

			# Bold
			s#\&lt;b\&gt;(.*?)\&lt;/b\&gt;#<b>$1</b>#gi;
			s{(?:(?<=\s)|(?<=^))\*([^\n*]+)\*(?=($|\s|[,.;:]))}{<b>$1</b>}g;

			# Italics
			s#\&lt;i\&gt;(.*?)\&lt;/i\&gt;#<i>$1</i>#gi;

			# Underline
			s#\&lt;u\&gt;(.*?)\&lt;/i\&gt;#<u>$1</u>#gi;
			s{(?:(?<=\s)|(?<=^))_([^\n_]+)_(?=($|\s|[,.;:]))}{<u>$1</u>}g;

			s#\&lt;s\&gt;(.*?)\&lt;/s\&gt;#<s>$1</s>#gi;
			s#\&lt;strong\&gt;(.*?)\&lt;/strong\&gt;#<strong>$1</strong>#gi;
			s#\&lt;em\&gt;(.*?)\&lt;/em\&gt;#<em>$1</em>#gi;
		}

		s/\&lt;tt\&gt;(.*?)\&lt;\/tt\&gt;/<tt>$1<\/tt>/gis;    # <tt> (MeatBall)

		if ($config{allow_html_links}) {
			s/\&lt;A(\s[^<>]+?)\&gt;(.*?)\&lt;\/a\&gt;/render_href_as_stored_html($1, $2)/gise;
		}

		if ($config{allow_free_links}) {

			# Consider: should local free-link descriptions be conditional?
			# Also, consider that one could write [[Bad Page|Good Page]]?
			s/\[\[$pattern_free_link\|([^\]]+)\]\]/render_page_or_edit_link_as_stored_html($1, $2)/geo;
			s/\[\[$pattern_free_link\]\]/render_page_or_edit_link_as_stored_html($1, "")/geo;
		}

		# Links like [URL text of link]
		if ($config{allow_link_descriptions}) {
			s/\[$pattern_url\s+([^\]]+?)\]/render_bracketed_url_as_stored_html($1, $2)/geos;
			s/\[$pattern_inter_link\s+([^\]]+?)\]/render_bracketed_inter_page_link_as_stored_html($1, $2)/geos;

			# Local bracket-links
			if ($config{allow_camelcase_links} and $config{allow_bracketed_wiki_links}) {
				s/\[$pattern_link\s+([^\]]+?)\]/render_bracketed_link_as_stored_html($1, $2)/geos;
			}
		}

		s/\[$pattern_url\]/render_bracketed_url_as_stored_html($1, "")/geo;
		s/\[$pattern_inter_link\]/render_bracketed_inter_page_link_as_stored_html($1, "")/geo;
		s/$pattern_url/render_url_as_stored_html($1, $useImage)/geo;
		s/$pattern_inter_link/render_and_store_inter_page_link($1)/geo;

		if ($config{allow_camelcase_links}) {
			s/$pattern_link/render_page_or_edit_link_as_html($1, "")/geo;
		}

		s/$pattern_rfc/render_rfc_link_as_stored_html($1)/geo;
		s/$pattern_isbn/render_isbn_link_as_stored_html($1)/geo;

		if ($config{allow_thin_hr_lines}) {
			s/----+/<hr noshade size=1>/g;
			s/====+/<hr noshade size=2>/g;
		}
		else {
			s/----+/<hr>/g;
		}
	}

	if ($doLines > SKIP_LINE_ORIENTED_MARKUP) {
		# The quote markup patterns avoid overlapping tags (with 5 quotes)
		# by matching the inner quotes for the strong pattern.
		s/(\'*)\'\'\'(.*?)\'\'\'/$1<strong>$2<\/strong>/g;
		s/\'\'(.*?)\'\'/<em>$1<\/em>/g;

		if ($config{allow_headings}) {
			s/(^|\n)\s*(\=+)\s+([^\n]+)\s+\=+/render_wiki_heading_as_html($1, $2, $3)/geo;
		}
	}

	return $_;
}

sub render_line_based_markup_as_html { # TODO
	my ($pageText) = @_;

	my @htmlStack = ();
	my $depth     = 0;
	my $pageHtml  = "";
	my $id        = "";

	foreach (split(/\n/, $pageText)) {    # Process lines one-at-a-time
		$_ .= "\n";

		my ($code, $depth);
		if (s/^(\;+)([^:]+\:?)\:?/<dt>$2<dd>/) {
			$code  = "DL";
			$depth = length $1;
			$id    = "";
		}
		elsif (s/^(\:+)/<dt><dd>/) {
			$code  = "DL";
			$depth = length $1;
			$id    = "";
		}
		elsif (s/^(\*+)/<li>/) {
			$code  = "UL";
			$depth = length $1;
			$id    = "";
		}
		elsif (s/^(\#+)/<li>/) {
			$code  = "OL";
			$depth = length $1;
			$id    = "";
		}
		elsif (/^[ \t].*\S/) {
			$code  = "PRE";
			$depth = 1;
			$id    = "eg";
		}
		else {
			$depth = 0;
			$id    = "";
		}

    # Close tags as needed
		while (@htmlStack > $depth) {
			my ($old_code,$old_id) = @{pop(@htmlStack)};
			$pageHtml .= "</$old_code>";
			$pageHtml .= "</div>" if $old_id;
		}

		if ($depth > 0) {
			$depth = $config{indent_limit} if ($depth > $config{indent_limit});

			# Non-empty stack
			if (@htmlStack) {
				my ($old_code,$old_id) = @{pop(@htmlStack)};

				if ($old_code ne $code) {
					$pageHtml .= "</$old_code>";
					$pageHtml .= "</div>" if $old_id;

					$pageHtml .= qq(<div id="$id">) if $id;
					$pageHtml .= qq(<$code>);
				}

				push(@htmlStack, [$code, $id]);
			}

			while (@htmlStack < $depth) {
				push(@htmlStack, [$code,$id]);

				$pageHtml .= qq(<div id="$id">) if $id;
				$pageHtml .= qq(<$code>\n);
			}
		}

		# Blank lines become <p> tags.
		# TODO - Paragraphs should be wrapped instead.
		s/^\s*$/<p>\n/;

		# Line-oriented markup.
		$pageHtml .= render_common_markup_as_html($_, RENDER_IMAGES, 2);
	}

	# Clear the stack.
	while (@htmlStack > 0) {
		my ($old_code,$old_id) = @{pop(@htmlStack)};
		$pageHtml .= "</$old_code>";
		$pageHtml .= "</div>" if $old_id;
	}

	return $pageHtml;
}

sub render_history_line_as_html { # TODO
	my ($id, $section, $canEdit, $isCurrent) = @_;

	my %sect    = %{ dclone($section) };
	my %revtext = %{ dclone($sect{+SECT_DATA}) };
	my $rev     = $sect{+SECT_REVISION};
	my $summary = $revtext{summary};

	my $host;
	if (defined($sect{host}) and $sect{host} ne "") {
		$host = $sect{host};
	}
	else {
		$host = $sect{+SECT_USER_IP};

    # Be somewhat anonymous if using IP address.
		$host =~ s/\d+$/xxx/;
	}

	my $user     = $sect{username};
	my $uid      = $sect{+SECT_USER_ID};
	my $ts       = $sect{+SECT_TIMESTAMP_CHANGE};
	my $minor    = $revtext{minor} ? "<i>(edit)</i> " : "";
	my $expirets = $^T - $config{keep_seconds};

	my $html = "Revision $rev: ";
	if ($isCurrent) {
		$html .= render_named_page_link_as_html($id, 'View') . " ";

		if ($canEdit) {
			$html .= render_edit_link_as_html($id, 'Edit') . " ";
		}

		if ($config{allow_diff}) {
			$html .= "Diff ";
		}
	}
	else {
		$html .= render_old_page_link_as_html('browse', $id, $rev, 'View') . " ";

		if ($canEdit) {
			$html .= render_old_page_link_as_html('edit', $id, $rev, 'Edit') . " ";
		}

		if ($config{allow_diff}) {
			$html .= render_diff_link_with_revision_as_html(1, $id, $rev, 'Diff') . " ";
		}
	}

	$html .= "... " . $minor . render_date_time_as_text($ts) . " ";
	$html .= "by " . render_author_link_as_html($host, $user, $uid) . " ";

	if (defined($summary) and ($summary ne "") and ($summary ne "*")) {
		$summary = quote_html($summary);    # Thanks Sunir! :-)
		$html .= "<b>[$summary]</b> ";
	}

	$html .= "<br>\n";

	return $html;
}

sub render_script_link_as_html {
	my ($action, $text, $title) = @_;
	return render_template_as_html(
		"snip-link-script.tt2",
		{
			base_url      => $config{full_url} || "",
			script_action => $action,
			anchor_text   => $text,
			title         => ($title || ""),
		}
	);
}

sub render_unnamed_page_link_as_html {
	my $page_id = shift;
	return render_named_page_link_as_html($page_id, $page_id);
}

sub render_named_page_link_as_html {
	my ($page_id, $page_name) = @_;

	$page_id =~ s!^/!$request_state{+RS_MAIN_PAGE}/!;

	if ($config{allow_free_links}) {
		$page_id =~ s/ /_/g;
		$page_id = ucfirst($page_id);
		$page_name =~ s/_/ /g;
	}

	return render_script_link_as_html("?$page_id", $page_name);
}

sub render_edit_link_as_html {
	my ($page_id, $page_name) = @_;

	if ($config{allow_free_links}) {
		$page_id =~ s/ /_/g;
		$page_id = ucfirst($page_id);
		$page_name =~ s/_/ /g;
	}

	return render_script_link_as_html("action/edit?id=$page_id", $page_name);
}

sub render_old_page_link_as_html {
	my ($kind, $page_id, $revision, $page_name) = @_;

	if ($config{allow_free_links}) {
		$page_id =~ s/ /_/g;
		$page_id = ucfirst($page_id);
		$page_name =~ s/_/ /g;
	}

	return render_script_link_as_html(
		"action/$kind?id=$page_id&amp;revision=$revision", $page_name
	);
}

sub render_page_or_edit_link_as_html {
	my ($page_id, $page_name) = @_;

	if ($page_name eq "") {
		$page_name = $page_id;
		if ($config{allow_free_links}) {
			$page_name =~ s/_/ /g;
		}
	}

	$page_id =~ s!^/!$request_state{+RS_MAIN_PAGE}/!;

	if ($config{allow_free_links}) {
		$page_id =~ s/ /_/g;
		$page_id = ucfirst($page_id);
	}

	my $exists = 0;

	if ($config{use_page_index_file}) {
		unless (@{$request_state{+RS_INDEX_LIST}}) {
			# Also initializes hash.
			my @temp = get_all_pages_for_entire_site();
		}
		$exists = 1 if ($request_state{+RS_INDEX_HASH}{$page_id});
	}
	elsif (-f get_filename_for_page_id($page_id)) {
		# Page file exists!
		$exists = 1;
	}

	if ($exists) {
		return render_named_page_link_as_html($page_id, $page_name);
	}

	if ($config{allow_free_links}) {
		if ($page_name =~ m!\s!) {     # Not a single word
			$page_name = "[$page_name]"; # Add brackets so boundaries are obvious
		}
	}

	return $page_name . render_edit_link_as_html($page_id, "?");
}

sub render_page_or_edit_link_as_stored_html {
	my ($page, $name) = @_;

	if ($config{allow_free_links}) {
		$page =~ s/^\s+//;        # Trim extra spaces
		$page =~ s/\s+$//;
		$page =~ s!\s*/\s*!/!;    # ...also before/after subpages
	}

	$name =~ s/^\s+//;
	$name =~ s/\s+$//;

	return store_raw_html(render_page_or_edit_link_as_html($page, $name));
}

sub render_search_link_as_html {
	my ($id) = @_;
	my $name = $id;

	$id =~ s!.+/!/!;                  # Subpage match: search for just /SubName

	if ($config{allow_free_links}) {
		$name =~ s/_/ /g;               # Display with spaces
		$id   =~ s/_/+/g;               # Search for url-escaped spaces
	}

	return render_script_link_as_html("action/search?query=$id", $name);
}

sub render_prefs_link_as_html {
	return render_template_as_html(
		"snip-link-preferences.tt2",
		{ },
	);
}

sub render_login_link_as_html {
	return render_template_as_html(
		"snip-link-login.tt2",
		{ },
	);
}

sub render_random_link_as_html {
	return render_template_as_html(
		"snip-link-random.tt2",
		{ },
	);
}

sub render_diff_link_as_html {
	my ($diff, $id, $text, $rev) = @_;

	$rev = "&amp;revision=$rev" if ($rev ne "");
	$diff = get_request_param("defaultdiff", 1) if ($diff == 4);

	return render_script_link_as_html(
		"action/browse?diff=$diff&amp;id=$id$rev", $text
	);
}

sub render_diff_link_with_revision_as_html {
	my ($diff, $id, $rev, $text) = @_;

	$rev = "&amp;diffrevision=$rev" if ($rev ne "");
	$diff = get_request_param("defaultdiff", 1) if ($diff == 4);

	return render_script_link_as_html(
		"action/browse?diff=$diff&amp;id=$id$rev", $text
	);
}

sub render_author_link_as_html {
	my ($host, $userName, $uid) = @_;

	my $userNameShow = $userName;

	if ($config{allow_free_links}) {
		$userName     =~ s/ /_/g;
		$userNameShow =~ s/_/ /g;
	}

	if (is_valid_page_id($userName) ne "") {    # Invalid under current rules
		$userName = "";                   # Just pretend it isn't there.
	}

	# Later have user preference for link titles and/or host text?
	my $html;
	if (($uid > 0) and ($userName ne "")) {
		# XXX - Probably renders the wrong link.
		$html = render_script_link_as_html(
			$userName, $userNameShow, "ID $uid from $host"
		);
	}
	else {
		$html = $host;
	}

	return $html;
}

sub render_history_link_as_html {
	my ($id, $text) = @_;
	$id =~ s/ /_/g if $config{allow_free_links};
	return render_script_link_as_html("action/history?id=$id", $text);
}

sub render_list_of_page_names_as_html {
	my $html = "<h2>" . @_ . " pages found:</h2>\n";
	foreach my $pagename (@_) {
		$html .= ".... " if $pagename =~ m!/!;
		$html .= render_unnamed_page_link_as_html($pagename) . "<br>\n";
	}
	return $html;
}

sub render_hidden_input_as_html {
	my ($name, $value) = @_;
	$request_state{+RS_CGI}->param($name, $value);
	return $request_state{+RS_CGI}->hidden($name);
}

# If $revision is true, it means we're viewing an old revision of a page.
# Notify search engine robots not to index the old versions.
#
# Search engine spammers rely on old versions of a page being indexed---
# fixing spam doesn't correct it in the past, so it's also assimilated.
# Turning off indexing for old pages thwarts their evil schemes.
#
# We also pass in "norobots" from maintenance forms and things to prevent
# their non-content from being indexed.

sub template_set_common_header_data {
	my ($template_data, $title) = @_;

	if (defined($request_state{+RS_SET_COOKIE}{+SCOOK_ID})) {
		# TODO - Proper cache-management headers.

		my $cookie = $request_state{+RS_CGI}->cookie(
			-name => $config{cookie_name},
			-value => $request_state{+RS_SET_COOKIE},
			-path => '/',
			-expires => '+1y',
		);

		$template_data->{html_headers} = $request_state{+RS_CGI}->header(
			-cookie => $cookie,
			-charset => 'UTF-8',
		);
	}
	else {
		$template_data->{html_headers} = $request_state{+RS_CGI}->header(
			-charset => 'UTF-8',
		);
	}

	$template_data->{global_css} = $config{global_css} || "";
	$template_data->{base_url}   = $config{full_url}   || "";

	# Display as spaces.
	$title =~ s/_/ /g if $config{allow_free_links};

	if (lc $title eq lc $config{site_name}) {
		$template_data->{doctitle} = $config{site_name};
	}
	elsif ($config{page_title_before_site_name}) {
		$template_data->{doctitle} = "$title - $config{site_name}";
	}
	else {
		$title =~ s/(^|\s)([a-z])([^A-Z\s]*)/$1\U$2\E$3/g;
		$title =~ s/^\s*($config{site_name}(?:'s)?)?\s*/$config{site_name}: /i;
		$title =~ s!/! - !g;
		$template_data->{doctitle} = $title;
	}

	if ($config{allow_user_css} and $request_state{+RS_USER_DATA}{+USER_CSS}) {
		$template_data->{CSS} = $request_state{+RS_USER_DATA}{+USER_CSS};
	}
}

sub template_set_redirect_data {
	my ($template_data, $old_id) = @_;
	return if $old_id eq "";

	$template_data->{redirect} .= (
		q{<h3>} .
		"(redirected from " .
		render_edit_link_as_html($old_id, $old_id) .
		")" .
		q{</h3>}
	);
}

sub template_set_title_data {
	my ($template_data, $page_id, $title) = @_;

	my $logo_image;
	my $header;
	if ($config{logo_url} ne "") {
		$logo_image = "img src=\"$config{logo_url}\" alt=\"[Home]\" border=0";

		unless ($config{logo_on_left}) {
			$logo_image .= " align=\"right\"";
		}

		$header = render_script_link_as_html($config{home_page}, "<$logo_image>");
	}
	else {
		$logo_image = $header = "";
	}

	if ($config{enable_inline_page_title}) {
		if ($config{allow_self_links} and $page_id ne "") {
			$template_data->{header} .= (
				q{<h1>} .
				$header .
				render_search_link_as_html($page_id) .
				q{</h1>}
			);
		}
		else {
			$template_data->{header} .= q{<h1>} . ($header . $title) . q{</h1>};
		}
	}

	if ($config{enable_top_link_bar} and get_request_param("toplinkbar", 1)) {

		# Later consider smaller size?
		$template_data->{header} .= render_goto_bar_as_html($page_id) . "<hr>";
	}
}

sub template_set_meta_robot_data {
	my ($template_data, $robots_keep_out) = @_;

	if ($robots_keep_out) {
		$template_data->{meta_robot} = "NOINDEX,NOFOLLOW";
	}
	else {
		$template_data->{meta_robot} = "INDEX,FOLLOW";
	}
}

sub render_page_header_as_html { # TODO
	my ($page_id, $title, $old_id, $robots_keep_out) = @_;

	my %template_data;
	template_set_common_header_data(\%template_data, $title);
	template_set_title_data(\%template_data, $page_id, $title);
	template_set_redirect_data(\%template_data, $old_id);
	template_set_meta_robot_data(\%template_data, $robots_keep_out);

	return render_template_as_html("snip-header.tt2", \%template_data);
}

sub template_set_complex_page_footer {
	my ($template_data, $id, $rev) = @_;

	$template_data->{footer} = render_goto_bar_as_html($id);

	if (user_can_edit($id, 0)) {
		my $userName = get_request_param("username", "");
		if ($userName eq "") {
			$template_data->{footer} .= "Must Login to Edit";
		}
		else {
			if ($rev ne "") {
				$template_data->{footer} .= (
					render_old_page_link_as_html(
						'edit', $id, $rev, "Edit r$rev of This Page"
					)
				);
			}
			else {
				$template_data->{footer} .= render_edit_link_as_html(
					$id, "Edit This Page"
				);
			}
		}

		$template_data->{footer} .= (
			" | " .
			render_history_link_as_html($id, "View Page History")
		);
	}
	else {
		$template_data->{footer} .= (
			"This Page is Read-Only" .
			" | " .
			render_history_link_as_html($id, "View Page History")
		);
	}

	if ($rev ne "") {
		$template_data->{footer} .= (
			" | " .
			render_named_page_link_as_html($id, "View Current Revision")
		);
	}

	$template_data->{footer} .= (
		" | Find Links to <b>" .
		render_search_link_as_html($id) .
		"</b>"
	);

	$template_data->{footer} .= "<br>";

	if ($request_state{+RS_SECTION}{+SECT_REVISION}) {
		if ($rev eq "") {    # Only for most current rev
			$template_data->{footer} .= "Last edited: ";
		}
		else {
			$template_data->{footer} .= "Edited: ";
		}

		$template_data->{footer} .= render_date_time_as_text(
			$request_state{+RS_SECTION}{+SECT_TIMESTAMP_CHANGE}
		);
	}

	if ($config{allow_diff}) {
		$template_data->{footer} .= " " . render_diff_link_as_html(4, $id, "(diff)", $rev);
	}

	#$template_data->{footer} .= "<br>" . render_search_form_as_html();
	if ($dir_data =~ m!/te?mp/!) {
		$template_data->{footer} .= (
			"<br><b>Warning:</b> Database is stored in temporary" .
			" directory $dir_data<br>"
		);
	}

	if (length $config{additional_footer_html}) {
		$template_data->{footer} .= $config{additional_footer_html};
	}

	#$template_data->{footer} .= $request_state{+RS_CGI}->endform;
}

sub render_complex_page_footer_as_html { # TODO
	my ($id, $rev) = @_;

	my %template_data;
	template_set_complex_page_footer(\%template_data, $id, $rev);

	return render_template_as_html("snip-footer.tt2", \%template_data);
}

sub template_set_common_footer_html {
	my $template_data = shift;
	$template_data->{footer} = render_goto_bar_as_html("");
}

sub render_common_footer_as_html { # TODO
	my %template_data;
	template_set_common_footer_html(\%template_data);

	return render_template_as_html("snip-footer.tt2", \%template_data);
}

sub render_form_start_as_html { # TODO
	my $action = shift();

	return $request_state{+RS_CGI}->startform(
		"POST",
		"$config{full_url}action/$action",
		"application/x-www-form-urlencoded"
	);
}

sub render_goto_bar_as_html { # TODO
	my ($id) = @_;

	my $bartext = render_unnamed_page_link_as_html($config{home_page});

	if ($id =~ m!/!) {
		my $main = $id;
		$main =~ s!/.*!!;    # Only the main page name (remove subpage)
		$bartext .= " | " . render_unnamed_page_link_as_html($main);
	}

	$bartext .= " | " . render_unnamed_page_link_as_html($config{rc_name});

	my $userName = get_request_param("username", "");
	$bartext .= " | " . render_prefs_link_as_html();
	$bartext .= " | " . render_login_link_as_html();

	if ($userName ne "") {
		$bartext .= (
			" (You are " .
			render_unnamed_page_link_as_html($userName) .
			") "
		);
	}
	else {
		$bartext .= " (Not logged in) ";
	}

	if (get_request_param("linkrandom", 0)) {
		$bartext .= " | " . render_random_link_as_html();
	}

	$bartext .= "<br>\n";
	return $bartext;
}

sub render_search_form_as_html { # TODO
	return unless $config{enable_search_box};

	return(
		"Search: " .
		$request_state{+RS_CGI}->textfield(-name => 'search', -size => 20) .
		render_hidden_input_as_html("dosearch", 1)
	);
}

sub render_projects_as_html { # TODO
	my $source = shift;
	my @projects;

	# The Wiki has munged $/, so we munge it back.  By the time we get
	# here, the Wiki page has already been HTML quoted.  We need to
	# unquote the HTML for the source code, or it may not look like
	# source!
	local $/ = "\n";
	$source = unquote_html($source);

	while ($source =~ m/<project>\s*(.*?)\s*<\/project>/sig) {
		local $_ = $1;

		my $name = "(unknown)";
		$name = $1 if /^\s*name\s*[:=]\s*(.*?)\s*$/mi;

		my $url = "";
		$url = $1 if /^\s*url\s*[:=]\s*(.*?)\s*$/mi;

		my $desc = "No description.";
		$desc = $1 if /^\s*<desc>\s*(.*?)\s*<\/desc>/sim;
		$desc =~ s/\s+/ /g;

		my $project = (
			"<p>" .
			"<table border=0 cellpadding=0 cellspacing=0 width='100%'>" .
			"<tr bgcolor=#000000>" .
			"<td>" .
			"<table border=0 cellpadding=1 cellspacing=1 width='100%'>" .
			"<tr bgcolor=#DDDDDD>" .
			"<td>"
		);

		my $url_name;
		if (length $url) {
			$url_name = "[$url $name]";
		}
		else {
			$url_name = $name;
		}

		$project .= "<font face='verdana'><b>$url_name</b></font>";

		if (length $url) {
			$project .= "</a>";
		}

		$project .= (
			"</td>" .
			"</tr>" .
			"<tr bgcolor=#C5C5C5>" .
			"<td>" .
			"<font face=verdana size=2>" .
			$desc .
			"</font>" .
			"</td>" .
			"</tr>" .
			"</table>" .
			"</td>" .
			"</tr>" .
			"</table>" .
			"</p>"
		);

		push @projects, $project;
	}

	my $html;
	if (@projects) {
		$html = join "", @projects;
	}
	else {
		$html = "<p>No projects listed.</p>";
	}

	return $html;
}

sub render_perl_as_stored_html { # TODO
	my $source = shift;

	# Defer compiling the module until it's needed.
	require Perl::Tidy;

	# By the time we get here, the Wiki page has already been HTML
	# quoted.  We need to unquote the HTML for the source code, or it
	# may not look like source!
	$source = unquote_html($source);

	# Something introduces strange newlines.  Remove them.
	$source =~ s/^(.*?)\s+?$/$1/mg;

	DUMP_TIDY and do {
		open(WHEE, ">", "/home/troc/tmp/messy");
		print WHEE $source;
		close WHEE;
	};

	# The Wiki has munged $/, so we munge it back.
	local $/ = "\n";

	# Tidy up the source.  Grok Perl::Tidy's options so this comes out
	# nicer.

	my $tidied = "";
	Perl::Tidy::perltidy(
		source      => \$source,
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

	# Convert it to HTML.  TODO: Make a clickable option to toggle line
	# numbers (-nnn option in the argv listref).

	my $html = "";
	Perl::Tidy::perltidy(
		source      => \$tidied,
		destination => \$html,
		argv        => [
			'-html',
			'-pre',
		],
	);

	$html = '<div id="code">' . $html . '</div>';

	DUMP_TIDY and do {
		open(WHEE, ">", "/home/troc/tmp/tidied");
		print WHEE $html;
		close WHEE;
	};

	return store_raw_html($html);
}

# TODO - Turn into a style sheet or something?
my %otl_colors = (
	"?" => "707070",
	"-" => "008000",
	"=" => "00C000",
	"+" => "004000",
	"*" => "000000",
	"#" => "800000",
);

# TODO - I don't really like the way they render anymore.
sub render_outline_as_html { # TODO
	my ($source, $type) = @_;
	$type = "headers" unless defined $type;

	# The Wiki has munged $/, so we munge it back.  By the time we get
	# here, the Wiki page has already been HTML quoted.  We need to
	# unquote the HTML for the source code, or it may not look like
	# source!
	local $/ = "\n";
	$source = unquote_html($source);

	my @outline;
	my $level = 0;

	my $last_color = "000000";

	while ($source =~ m/^(.*)$/mig) {
		my $line = $1;
		chomp $line;

		# Headings.
		if ($line =~ s/^(\t+)//) {
			$level = length $1;
		}
		else {
			$level = 0;
		}

		# Pipe denotes text.
		if ($line =~ s/^\| ?//) {

			if ($type eq "todo") {

				# Can't use : in todo lists, because it's a special wiki character.
				$line =~ s/:/&#58;/g;

				# This line is preformatted.  Just add it, but fixed-width, etc.
				if ($line =~ /^\s/) {
					my $stuff = ":" x ($level + 1);
					$line =~ s/\s/&#160;/g;
					push @outline, "$stuff<font color='#$last_color'><tt>$line</tt>";
					next;
				}

				# This line continues a pipe...
				if (@outline and $outline[-1] =~ /^:/) {

					# Previous line was empty...
					my $temp = $outline[-1];
					$temp =~ s/<.*?>//g;
					unless ($temp =~ /^(:|&#160;|\s+)*$/) {
						$outline[-1] =~ s/\s+$//;
						$outline[-1] .= " $line";
						next;
					}
				}

				# This line starts a pipe?
				my $stuff = ":" x ($level + 1);
				push @outline, "$stuff<font color='#$last_color'>$line";
				next;
			}

			# Some other outline.  Just add it.
			push @outline, $line;
			next;
		}

		if ($type eq "headers") {
			my $stuff = "=" x ($level + 1);
			push @outline, "$stuff $line $stuff";
			next;
		}

		if ($type eq "bullets") {
			my $stuff = "*" x ($level + 1);
			push @outline, "$stuff $line";
			next;
		}

		if ($type eq "todo") {
			$line =~ s/\s+$//;

			my $stuff = ";" x ($level + 1);

			$line =~ s/^([\!-\/\:-\@\[-\`\{-\~])\s+/<tt>$1 <\/tt>/;

			my $bullet = $1;

			$line =~ s/\:/&#58;/g;

			# TODO - Make this use style sheets?
			my $color;
			if (exists $otl_colors{$bullet}) {
				$color = $otl_colors{$bullet};
			}
			else {
				$color = "F08080";
			}

			$last_color = $color;
			push @outline, "$stuff<font color='\#$color'>$line</font>";
			next;
		}

		push @outline, "?($type,$level) $line";
	}

	if (@outline) {
		for (1 .. $#outline - 1) {
			next if $outline[$_] =~ /\S/;
			if ($outline[$_ - 1] =~ /^(\s+)/) {
				my $match = $1;
				if ($outline[$_ + 1] =~ /^$match/) {
					$outline[$_] = $match;
				}
			}
		}

		# Close <font> tags in text notes.
		foreach (@outline) {
			s/\s*$/<\/font>/ if /^:/;
		}

		if ($type eq "todo") {
			unshift(@outline,
				"  \? = Maybe.  An idea without a plan.",
				"  \- = Planned.",
				"  \= = Started.  Actively being worked on.",
				"  \+ = Almost done.",
				"  \* = Done.  Hooray!",
				"  X = Canceled.",
				"  \# = Blocked.  Someone or something is in the way.",
			);
		}

		return render_line_based_markup_as_html(join "\n", @outline);
	}
	return "<p>No outline.</p>";
}

sub render_components_as_html { # TODO
	my $source = shift;
	my @components;

	# The Wiki has munged $/, so we munge it back.  By the time we get
	# here, the Wiki page has already been HTML quoted.  We need to
	# unquote the HTML for the source code, or it may not look like
	# source!
	local $/ = "\n";
	$source = unquote_html($source);

	while ($source =~ m/<component>\s*(.*?)\s*<\/component>/sig) {
		local $_ = $1;

		my $name = "(unknown)";
		$name = $1 if /^\s*name\s*[:=]\s*(.*?)\s*$/mi;

		my $url = "";
		$url = $1 if /^\s*url\s*[:=]\s*(.*?)\s*$/mi;

		my $auth = "";
		$auth = $1 if /^\s*author\s*[:=]\s*(.*?)\s*$/mi;

		my $mail = "";
		$mail = $1 if /^\s*email\s*[:=]\s*(.*?)\s*$/mi;

		my $ver = "";
		$ver = $1 if /^\s*version\s*[:=]\s*(.*?)\s*$/mi;

		my $cpan = 0;
		$cpan = 1 if /^\s*<cpan\s*\/>\s*$/mi;

		my $desc = "No description.";
		$desc = $1 if /^\s*<desc>\s*(.*?)\s*<\/desc>/sim;
		$desc =~ s/\s+/ /g;

		my $component = (
			"<p>" .
			"<table border=0 cellpadding=0 cellspacing=0 width='100%'>" .
			"<tr bgcolor=#000000>" .
			"<td>" .
			"<table border=0 cellpadding=1 cellspacing=1 width='100%'>" .
			"<tr bgcolor=#DDDDDD>" .
			"<td><font face='verdana' color=#005599><b>$name</b></font></td>" .
			"</tr>" .
			"<tr bgcolor=#C5C5C5>" .
			"<td><font face='verdana' color=#000000>$desc</font></td>" .
			"</tr>"
		);

		if (length($url) or length($auth) or length($mail) or length($ver)) {
			$component .= (
				"<tr bgcolor=#DDDDDD>" .
				"<td>" .
				"<table border=0 cellpadding=0 cellspacing=0 width='100%'>"
			);

			### Author.

			if (length($auth) or length($mail)) {
				$component .= (
					"<tr>" .
					"<td width='1%'>" .
					"<font face='verdana' color=#000000 size=2><b>Author</b></font>" .
					"</td>" .
					"<td width='1%' nowrap>" .
					"<font face='verdana' color=#000000 size=2> <b>:</b> </font>" .
					"</td>" .
					"<td width='98%'>"
				);

				$component .= "<font face='verdana' color=#000000 size=2>$auth</font>"
					if length $auth;

				$component .= " mailto:$mail" if length $mail;

				$component .= ("</td>" . "</tr>");
			}

			### URL.

			if (length $url) {
				$component .= (
					"<tr bgcolor=#DDDDDD>" .
					"<td width='1%'>" .
					"<font face='verdana' color=#000000 size=2><b>Download</b></font>" .
					"</td>" .
					"<td width='1%' nowrap>" .
					"<font face='verdana' color=#000000 size=2> <b>:</b> </font>" .
					"</td>" .
					"<td width='98%'>" .
					"[$url Get it now!]" .
					"</td>" .
					"</tr>"
				);
			}

			if (length $ver) {
				$component .= (
					"<tr bgcolor=#DDDDDD>" .
					"<td width='1%'>" .
					"<font face='verdana' color=#000000 size=2>" .
					"<b>Version</b>" .
					"</font>" .
					"</td>" .
					"<td width='1%' nowrap>" .
					"<font face='verdana' color=#000000 size=2> <b>:</b> </font>" .
					"</td>" .
					"<td width='98%'>" .
					"<font face='verdana' color=#000000 size=2>" .
					$ver .
					"</font>" .
					"</td>" .
					"</tr>"
				);
			}

			$component .= (
				"<tr bgcolor=#DDDDDD>" .
				"<td nowrap>" .
				"<font face='verdana' color=#000000 size=2>" .
				"<b>On CPAN</b>" .
				"</font>" .
				"</td>" .
				"<td width='1%' nowrap>" .
				"<font face='verdana' color=#000000 size=2> <b>:</b> </font>" .
				"</td>" .
				"<td width='98%'>" .
				"<font face='verdana' color=#000000 size=2>"
			);

			if ($cpan) {
				$component .= "Yes!";
			}
			else {
				$component .= "Unfortunately not.";
			}

			$component .= ("</font>" . "</td>" . "</tr>");

			$component .= ("</table>" . "</td>" . "</tr>");
		}

		$component .= ("</table>" . "</td>" . "</tr>" . "</table>" . "</p>");

		push @components, $component;
	}

	my $html;
	if (@components) {
		$html = join "", @components;
	}
	else {
		$html = "<p>No components listed.</p>";
	}

	return $html;
}

sub render_pre_as_stored_html { # TODO
	my $html = shift;
	my $pre = (
		'<div id="eg"><pre>' .
		$html .
		'</pre></div>'
	);

	return store_raw_html($pre);
}

sub render_code_as_stored_html { # TODO
	my $html = shift;
	my $code = (
		"<code>" .
		$html .
		"</code>"
	);

	return store_raw_html($code);
}

sub render_rfc_link_as_stored_html { # TODO
	my ($num) = @_;
	return store_raw_html(
		"RFC <a href=\"http://www.faqs.org/rfcs/rfc${num}.html\">$num</a>"
	);
}

sub render_isbn_link_as_stored_html { # TODO
	my ($rawnum) = @_;

	my $num = $rawnum;
	$num =~ s/[- ]//g;

	my $rawprint = $rawnum;
	$rawprint =~ s/ +$//;

	if (length($num) != 10) {
		return "ISBN $rawnum";
	}

	my $first  = qq{ISBN <a href="http://isbn.nu/$num">$rawnum</a> };
	my $second = "<a href=\"http://www.amazon.com/exec/obidos/ISBN=$num\">Amazon</a>";
	my $third  = "<a href=\"http://www.pricescan.com/books/BookDetail.asp?isbn=$num\">Pricescan</a>";

	my $html .= "$first";
	$html .= " ($second, $third)" if $config{enable_extra_isbn_links};

	# preserve ISBN space.
	$html .= " " if (substr($rawnum, -1, 1) eq ' ');

	return store_raw_html($html);
}

sub render_inter_page_link_as_html_and_punct { # TODO
	my ($id) = @_;

	($id, my $punct) = split_url_from_trailing_punctuation($id);

	my $name = $id;
	my ($site, $remotePage) = split(/:/, $id, 2);
	my $url = get_interwiki_url($site);

	# The next line is an evil hack to prevent warnings
	# in the error logs.  Do something better later. -><-
	$url   = "" unless defined $url;
	$id    = "" unless defined $id;
	$punct = "" unless defined $punct;

	return ("", $id . $punct) if ($url eq "");

	$remotePage =~ s/&amp;/&/g;    # Unquote common URL HTML
	$url .= $remotePage;

	return ("<a href=\"$url\">$name</a>", $punct);
}

sub render_bracketed_inter_page_link_as_stored_html { # TODO
	my ($id, $text) = @_;

	my ($site, $remotePage) = split(/:/, $id, 2);
	$remotePage =~ s/&amp;/&/g;    # Unquote common URL HTML
	my $url = get_interwiki_url($site);

	if ($text ne "") {
		return "[$id $text]" if ($url eq "");
	}
	else {
		return "[$id]" if ($url eq "");
		$text = get_bracketed_url_index($id);
	}

	$url .= $remotePage;

	return store_raw_html("<a href=\"$url\">[$text]</a>");
}

sub render_url_link_as_html_and_punct { # TODO
	my ($rawname, $useImage) = @_;

	my ($name, $punct) = split_url_from_trailing_punctuation($rawname);

	if ($config{allow_file_scheme} and $name =~ m!^file:!) {

		# Only do remote file:// links. No file:///c|/windows.
		if ($name =~ m!^file://[^/]!) {
			return ("<a href=\"$name\">$name</a>", $punct);
		}

		return $rawname;
	}

	# Restricted image URLs so that mailto:foo@bar.gif is not an image
	if (
		$useImage and
		($name =~ /^(http:|https:|ftp:).+\.$pattern_image_extensions$/)
	) {
		return ("<img src=\"$name\">", $punct);
	}

	# we don't display mailto: on mailto: links.
	if ($name =~ /^mailto:/) {
		my $email = $name;

		# trim the mailto from what we display
		substr($email, 0, 7) = '';

		# change the @ to ' at '; makes humans feel a little better.
		$email =~ s/\@/&nbsp;at&nbsp;/;
		return (qq(&lt;<a href="$name">$email</a>&gt;), $punct);
	}

	return ("<a href=\"$name\">$name</a>", $punct);
}

sub render_wiki_heading_as_html { # TODO
	my ($pre, $depth, $text) = @_;

	$depth = length($depth);
	$depth = 6 if ($depth > 6);

	return $pre . "<H$depth>$text</H$depth>\n";
}

sub render_href_as_stored_html { # TODO
	my ($anchor, $text) = @_;
	return store_raw_html("<a $anchor>$text</a>");
}

sub render_and_store_inter_page_link { # TODO
	my ($id) = @_;

	my ($link, $extra) = render_inter_page_link_as_html_and_punct($id);

	# Next line ensures no empty links are stored.
	$link = store_raw_html($link) if $link ne "";
	return $link . $extra;
}

sub store_raw_html {
	# Given an HTML snippet, save it in a symbol table.  Return the
	# symbol representing the snippet.  This prevents rendered snippets
	# from being reconsidered by other renderers.

	my ($html) = @_;
	push @{$request_state{+RS_SAVED_HTML}}, $html;
	return $FS . $#{$request_state{+RS_SAVED_HTML}} . $FS;
}

sub render_url_as_stored_html { # TODO
	my ($name, $useImage) = @_;

	my ($link, $extra) = render_url_link_as_html_and_punct($name, $useImage);

	# Next line ensures no empty links are stored
	$link  = "" unless defined $link;
	$extra = "" unless defined $extra;
	$link = store_raw_html($link) if $link ne "";
	return $link . $extra;
}

sub render_bracketed_url_as_stored_html { # TODO
	my ($url, $text) = @_;

	# we want to translate 'http:/?' into something more meaningful.
	$url =~ s{^http:/{0,2}(?=\?)}{}g;

	if ($text eq "") {
		$text = get_bracketed_url_index($url);
	}

	return store_raw_html("<a href=\"$url\">[$text]</a>");
}

sub get_bracketed_url_index {
	my ($id) = @_;

	# Consider plain array?
	if ($request_state{+RS_SAVED_URL_IDX}{$id} > 0) {
		return $request_state{+RS_SAVED_URL_IDX}{$id};
	}

	$request_state{+RS_SAVED_URL_IDX}{$id} = keys(
		%{$request_state{+RS_SAVED_URL_IDX}}
	) + 1;

	return $request_state{+RS_SAVED_URL_IDX}{$id};
}

sub render_bracketed_link_as_stored_html { # TODO
	my ($name, $text) = @_;

	return store_raw_html(render_named_page_link_as_html($name, "[$text]"));
}

sub render_sub_wiki_link_as_stored_html { # TODO
	my ($link, $old, $new) = @_;

	my $newBracket = 0;
	if ($link eq $old) {
		$link = $new;
		unless ($new =~ /^$pattern_link$/o) {
			$link = "[[$link]]";
		}
	}

	return store_raw_html($link);
}

sub render_sub_free_link_as_stored_html { # TODO
	my ($link, $name, $old, $new) = @_;

	my $oldlink = $link;
	$link =~ s/^\s+//;
	$link =~ s/\s+$//;

	if ($link eq $old) {
		$link = $new;
	}
	else {
		$link = $oldlink;    # Preserve spaces if no match
	}

	$link = "[[$link";

	if ($name ne "") {
		$link .= "|$name";
	}

	$link .= "]]";
	return store_raw_html($link);
}

### MAIN: Handle the wiki request.
# It is called at the end of the program.
# This allows execution of various initializers throughout the code.
# It calls the dispatchers, which call the actions, which in turn call
# various helpers and renderers.

sub main_wiki_request {

	# Call the one-time initialization here.
	# More important with mod_perl than CGI.
	if (!$dir_data || $config{load_config_each_request}) {
		init_wiki();
	}

	# Cached page! Awright!
	return if try_html_cache();

	# Initialize request, or bail if it fails.
	init_request() or return;

	my $path_info = $request_state{+RS_CGI}->path_info() || "";
	if ($path_info =~ /^\/action\/?(.*?)\/*$/) {
		dispatch_action_request(lc($1));
		return;
	}
	else {
		dispatch_browse_request();
		return;
	}

	print render_error_page_as_html("Invalid URL.");
}

main_wiki_request();
exit;
