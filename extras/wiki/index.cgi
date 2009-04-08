#!/sw/perl/5a0/bin/perl
#!/usr/bin/perl
# UseModWiki version 0.91 (February 12, 2001)
# Copyright (C) 2001-2002 Matt Cashner, Rocco Caputo, and Richard
# Soderberg The POE crew strikes again.
#
# $Id$
#
# Copyright (C) 2000-2001 Clifford A. Adams
#    <caadams@frontiernet.net> or <usemod@usemod.com>
# Based on the GPLed AtisWiki 0.3  (C) 1998 Markus Denker
#    <marcus@ira.uka.de>
# ...which was based on
#    the LGPLed CVWiki CVS-patches (C) 1997 Peter Merel
#    and The Original WikiWikiWeb  (C) Ward Cunningham
#        <ward@c2.com> (code reused with permission)
# ThinLine options by Jim Mahoney <mahoney@marlboro.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
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
use Text::Template;
use POSIX qw(strftime);

use constant UID_MINLEGAL     => 1001;
use constant UID_ENOCOOKIE    => 111;
use constant UID_ENOUSERFILE  => 112;
use constant UID_EBADCOOKIE   => 113;
use constant UID_MINPOSSIBLE  => 1;

$| = 1;      # Do not buffer output

# == Configuration ============================================================

# Development flag.  Dump the before and after versions of source code
# as it passes through Perl::Tidy.

use constant DUMP_TIDY => 0;

# Configuration/constant variables.  Must be C<use vars> because
# they're overridden with a do() function.

use vars qw( @RcDays @HtmlPairs @HtmlSingle $TempDir $LockDir
	$DataDir $HtmlDir $UserDir $KeepDir $PageDir
	$InterFile $RcFile $RcOldFile $IndexFile $FullUrl
	$SiteName $HomePage $LogoUrl $RcDefault $IndentLimit
	$RecentTop $EditAllowed $UseDiff $UseSubpage
	$UseCache $RawHtml $SimpleLinks $NonEnglish
	$LogoLeft $KeepDays $HtmlTags $HtmlLinks $UseDiffLog
	$KeepMajor $KeepAuthor
	$NotifyDefault $ScriptTZ $BracketText
	$UseAmPm $UseConfig $UseIndex $RedirType $AdminPass
	$EditPass $UseHeadings $NetworkFile $BracketWiki
	$FreeLinks $WikiLinks $AdminDelete $FreeLinkPattern
	$RCName $ShowEdits $ThinLine $LinkPattern
	$InterLinkPattern $InterSitePattern $UrlProtocols
	$UrlPattern $ImageExtensions $RFCPattern $ISBNPattern
	$FS $FS1 $FS2 $FS3 $CookieName $SiteBase $GlobalCSS
	$WantSearch $WantTopLinkBar $ExtraISBNLinks
	$UseScriptName $AllowCharRefs $UserCSS $ReverseTitle
	$EnableSelfLinks $Footer $ForceLcaseFiles
	$LoadEveryTime $Templates $EnableInlineTitle
	$VERSION
);

# Other global variables.  Must be C<use vars> because they're
# overridden with a do() function.

use vars qw( %Page %Section %Text %InterSite %SaveUrl %SaveNumUrl
	%KeptRevisions %UserCookie %SetCookie %UserData
	%IndexHash $InterSiteInit $SaveUrlIndex $SaveNumUrlIndex
	$MainPage $OpenPageName @KeptList @IndexList $IndexInit
	$q $UserID $TimeZoneOffset $ScriptName $BrowseCode
	$OtherCode $ShowNotify
);

$VERSION = (qw($Revision$))[1];    # CVS Version. NO TOUCHIE

##############################
### INITIALIZATION SECTION ###

sub init_config {

	# Main wiki directory depends on where the wiki is installed.

	if (
		defined($ENV{SERVER_NAME}) and
		$ENV{SERVER_NAME} =~ /^(?:10\.0\.0\.|127\.)/
	) {
		$DataDir = "/home/troc/Sites/poeperlorg/data";
	}
	elsif (defined $ENV{DOCUMENT_ROOT}) {
		$DataDir = $ENV{DOCUMENT_ROOT};
		$DataDir .= '/' unless substr($DataDir, -1, 1) eq '/';
		$DataDir .= 'data';
	}

	# 1 = use config file,    0 = do not look for config
	$UseConfig = 1;

	# Default configuration (used if UseConfig is 0)
	$GlobalCSS  = "";    # path to global css style sheet
	$WantSearch = 1;     # 1 = Show search box; 0 = Dont show search box;
	$WantTopLinkBar = 1; # 1 = show top link bar; 0 = never show top link bar
	$CookieName = "Wiki";             # Name for this wiki (for multi-wiki sites)
	$SiteName   = "Wiki";             # Name of site (used for titles)
	$HomePage   = "HomePage";         # Home page (change space to _)
	$RCName     = "RecentChanges";    # Name of changes page (change space to _)
	$LogoUrl    = "";                 # URL for site logo ("" for no logo)
	$ENV{PATH}  = "/usr/bin/";        # Path used to find "diff"
	$ScriptTZ   = "";                 # Local time zone ("" means do not print)
	$RcDefault  = 30;                 # Default number of RecentChanges days
	@RcDays     = qw(1 3 7 30 90);    # Days for links on RecentChanges
	$KeepDays   = 14;                 # Days to keep old revisions
	$SiteBase   = "";                 # Full URL for <BASE> header
	$FullUrl    = "";                 # Set if the auto-detected URL is wrong
	$RedirType  = 1;                  # 1 = CGI.pm, 2 = script, 3 = no redirect
	$AdminPass  = "";                 # Set to non-blank to enable password(s)
	$EditPass   = "";                 # Like AdminPass, but for editing only

	# Major options:
	$UseSubpage    = 1;    # 1 = use subpages,       0 = do not use subpages
	$UseCache      = 0;    # 1 = cache HTML pages,   0 = generate every page
	$EditAllowed   = 1;    # 1 = editing allowed,    0 = read-only
	$RawHtml       = 0;    # 1 = allow <HTML> tag,   0 = no raw HTML in pages
	$HtmlTags      = 0;    # 1 = "unsafe" HTML tags, 0 = only minimal tags
	$UseDiff       = 1;    # 1 = use diff features,  0 = do not use diff
	$FreeLinks     = 1;    # 1 = use [[word]] links, 0 = LinkPattern only
	$WikiLinks     = 1;    # 1 = use LinkPattern,    0 = use [[word]] only
	$AdminDelete   = 1;    # 1 = Admin only page,    0 = Editor can delete pages
	$UseScriptName = 0;    # 1 = use SCRIPT_NAME     0 = don't (supports http://wiki/?Link)

	# Minor options:
	$LogoLeft    = 0;    # 1 = logo on left,       0 = logo on right
	$RecentTop   = 1;    # 1 = recent on top,      0 = recent on bottom
	$UseDiffLog  = 1;    # 1 = save diffs to log,  0 = do not save diffs
	$KeepMajor   = 1;    # 1 = keep major rev,     0 = expire all revisions
	$KeepAuthor  = 1;    # 1 = keep author rev,    0 = expire all revisions
	$ShowEdits   = 0;    # 1 = show minor edits,   0 = hide edits by default
	$HtmlLinks   = 0;    # 1 = allow A HREF links, 0 = no raw HTML links
	$SimpleLinks = 0;    # 1 = only letters,       0 = allow _ and numbers
	$NonEnglish  = 0;    # 1 = extra link chars,   0 = only A-Za-z chars
	$ThinLine    = 0;    # 1 = fancy <hr> tags,    0 = classic wiki <hr>
	$BracketText = 1;    # 1 = allow [URL text],   0 = no link descriptions
	$UseAmPm     = 1;    # 1 = use am/pm in times, 0 = use 24-hour times
	$UseIndex    = 0;    # 1 = use index file,     0 = slow/reliable method
	$UseHeadings = 1;    # 1 = allow = h1 text =,  0 = no header formatting
	$NetworkFile = 1;    # 1 = allow remote file:, 0 = no file:// links
	$BracketWiki = 0;    # 1 = [WikiLnk txt] link, 0 = no local descriptions

	$ShowNotify     = 1;         # 1 = show notify option            0 = don't

	$ExtraISBNLinks = 1;    # 1 = display extra ISBN links.     0 = don't
	$AllowCharRefs  = 1;    # 1 = allow character references    0 = don't
	$UserCSS        = 1;    # 1 = allow per-user CSS prefs      0 = don't
	$ReverseTitle   = 0;    # 1 = page title before SiteName    0 = after

	$EnableSelfLinks   = 1; # 1 = create ?search heading links  0 = don't
	$EnableInlineTitle = 1; # 1 = use title in page             0 = don't

	$Footer          = "";  # HTML that goes at the end of the footer.
	$ForceLcaseFiles = 0;   # 1 = filename case always lower    0 = not
	$LoadEveryTime   = 0;   # 1 = force config load every run   0 = not

	# HTML tag lists, enabled if $HtmlTags is set.  Scripting is
	# currently possible with these tags, so they are *not* particularly
	# "safe".

	# Single tags (that do not require a closing /tag)
	@HtmlSingle = qw(br p hr li dt dd tr td th);

	# Tags that must be in <tag> ... </tag> pairs.  All single tags can
	# also be pairs.
	@HtmlPairs = (
		qw(
			b big blockquote boxes
			caption center cite code
			div dl
			em
			font
			h1 h2 h3 h4 h5 h6
			i
			ol
			perl
			s small span strike strong sub sup
			table tt
			u ul
			var
		),
		@HtmlSingle
	);

	# == You should not have to change anything below this line. ================

	$IndentLimit = 20;                      # Maximum depth of nested lists
	$PageDir     = "$DataDir/page";         # Stores page data
	$HtmlDir     = "$DataDir/html";         # Stores HTML versions
	$UserDir     = "$DataDir/user";         # Stores user data
	$KeepDir     = "$DataDir/keep";         # Stores kept (old) page data
	$TempDir     = "$DataDir/temp";         # Temporary files and locks
	$LockDir     = "$TempDir/lock";         # DB is locked if this exists
	$InterFile   = "$DataDir/intermap";     # Interwiki site->url map
	$RcFile      = "$DataDir/rclog";        # New RecentChanges logfile
	$RcOldFile   = "$DataDir/oldrclog";     # Old RecentChanges logfile
	$IndexFile   = "$DataDir/pageidx";      # List of all pages
	$Templates   = "$DataDir/templates/";
}

sub init_wiki {
	init_config();

	if ($UseConfig) {
		if (-f "$DataDir/config") {
			if (open(CONFIG, "$DataDir/config")) {
				local $/;

				eval scalar <CONFIG>;
				die "eval $DataDir/config failed: $@" if $@;
				close(CONFIG);
			}
			else {
				die "couldn't open config: $!";
			}
		}
		else {
			die "couldn't find $DataDir/config: $!";
		}

		# A safe place for our changes.
		if (-f "$DataDir/config.custom") {
			if (open(CUSTOM, "$DataDir/config.custom")) {
				local $/;

				eval scalar <CUSTOM>;
				die "eval $DataDir/config.custom failed: $@" if $@;
				close(CUSTOM);
			}
			else {
				warn "couldn't open $DataDir/config.custom: $!";
			}
		}
	}

	# Validate configuration.

	die "no document root; set \$DataDir manually" unless defined $DataDir;
	die "document root $DataDir doesn't exist" unless -e $DataDir;
	unless (-d $DataDir || -l $DataDir) {
		die "document root $DataDir isn't a directory";
	}

	init_link_patterns();
}

sub init_link_patterns {

	# Field separators are used in the URL-style patterns below.
	$FS  = "\xb3";       # The FS character is a superscript "3"
	$FS1 = $FS . "1";    # The FS values are used to separate fields
	$FS2 = $FS . "2";    # in stored hashtables and other data structures.
	$FS3 = $FS . "3";    # The FS character is not allowed in user data.

	my $UpperLetter = "[A-Z";
	my $LowerLetter = "[a-z";
	my $AnyLetter   = "[A-Za-z";

	if ($NonEnglish) {
		$UpperLetter .= "\xc0-\xde";
		$LowerLetter .= "\xdf-\xff";
		$AnyLetter   .= "\xc0-\xff";
	}

	unless ($SimpleLinks) {
		$AnyLetter .= "_:0-9";
	}

	$UpperLetter .= "]";
	$LowerLetter .= "]";
	$AnyLetter   .= "]";

	# Main link pattern: lowercase between uppercase, then anything
	my $LpA = (
		$UpperLetter . "+" . $LowerLetter . "+" . $UpperLetter . $AnyLetter . "*"
	);

	# Optional subpage link pattern: uppercase, lowercase, then anything
	my $LpB = $UpperLetter . "+" . $LowerLetter . "+" . $AnyLetter . "*";

	if ($UseSubpage) {

		# Loose pattern: If subpage is used, subpage may be simple name
		$LinkPattern = "((?:(?:$LpA)?\\/$LpB)|$LpA)";

		# Strict pattern: both sides must be the main LinkPattern
		# $LinkPattern = "((?:(?:$LpA)?\\/)?$LpA)";
	}
	else {
		$LinkPattern = "($LpA)";
	}

	my $QDelim = '(?:"")?';    # Optional quote delimiter (not in output)
	$LinkPattern .= $QDelim;

	# Inter-site convention: sites must start with uppercase letter
	# (Uppercase letter avoids confusion with URLs)
	$InterSitePattern = $UpperLetter . $AnyLetter . "+";
	$InterLinkPattern = "((?:$InterSitePattern:[^\\]\\s\"<>$FS]+)$QDelim)";

	if ($FreeLinks) {

		# Note: the - character must be first in $AnyLetter definition
		if ($NonEnglish) {
			$AnyLetter = "[-,.:' _0-9A-Za-z\xc0-\xff]";
		}
		else {
			$AnyLetter = "[-,.:' _0-9A-Za-z]";
		}
	}
	$FreeLinkPattern = "($AnyLetter+)";
	if ($UseSubpage) {
		$FreeLinkPattern = "((?:(?:$AnyLetter+)?\\/)?$AnyLetter+)";
	}
	$FreeLinkPattern .= $QDelim;

	# Url-style links are delimited by one of:
	#   1.  Whitespace                           (kept in output)
	#   2.  Left or right angle-bracket (< or >) (kept in output)
	#   3.  Right square-bracket (])             (kept in output)
	#   4.  A single double-quote (")            (kept in output)
	#   5.  A $FS (field separator) character    (kept in output)
	#   6.  A double double-quote ("")           (removed from output)

	$UrlProtocols = (
		"http|https|ftp|afs|news|nntp|mid|cid|mailto|wais|" .
		"prospero|telnet|gopher"
	);

	$UrlProtocols .= '|file' if $NetworkFile;
	$UrlPattern      = "((?:(?:$UrlProtocols):[^\\]\\s\"<>$FS]+)$QDelim)";
	$ImageExtensions = "(gif|jpg|png|bmp|jpeg)";
	$RFCPattern      = "RFC\\s?(\\d+)";
	$ISBNPattern     = "ISBN:?([0-9- xX]{10,})";
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

	if (open(IN, "<$fileName")) {
		local $/;

		my $data = <IN>;
		close IN;
		return (1, $data);
	}

	return (0, "");
}

sub append_string_to_file {
	my ($file, $string) = @_;

	open(OUT, ">>$file") or die("cant write $file: $!");
	print OUT $string;
	close(OUT) or die "close failed (append_string_to_file) on $file: $!";
}

sub create_directory {
	my ($newdir) = @_;

	mkdir($newdir, 0775) unless -d $newdir;
	die "Failed to mkdir $newdir: $!" unless -d $newdir;
}

sub write_string_to_file {
	my ($file, $string) = @_;

	open(OUT, ">$file") or die("cant write $file: $!");
	print OUT $string;
	close(OUT) or die "close failed (write_string_to_file) on $file: $!";
}

sub read_file_or_die {
	my ($fileName) = @_;

	my ($status, $data) = read_file($fileName);
	die "Can't open $fileName: $!" unless $status;

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

	if ($UseSubpage) {
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

	if ($FreeLinks) {
		$id =~ s/ /_/g;
		unless ($UseSubpage) {
			if ($id =~ /\//) {
				return "Invalid Page $id (/ not allowed)";
			}
		}

		unless ($id =~ m!$FreeLinkPattern!) {
			return "Invalid Page $id";
		}

		return "";
	}
	else {
		unless ($id =~ /^$LinkPattern$/o) {
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

# TODO - I suspect that timezone handling is broken.

sub render_date_as_text {
	my ($ts) = @_;
	return strftime("%B %e, %y", gmtime($ts));
}

sub render_time_as_text {
	my ($ts) = @_;
	return strftime("%r GMT", gmtime()) if $UseAmPm;
	return strftime("%T GMT", gmtime());
}

sub render_date_time_as_text {
	my ($t) = @_;
	return render_date_as_text($t) . " " . render_time_as_text($t);
}

sub request_lock_dir {
	my ($name, $tries, $wait, $errorDie) = @_;

	create_directory($TempDir);
	my $lockName = $LockDir . $name;
	my $n        = 0;

	while (mkdir($lockName, 0555) == 0) {

		# TODO - POSIX or Errno instead
		if ($! != 17) {
			die("can't make $LockDir: $!\n") if $errorDie;
			return 0;
		}

		return 0 if $n++ >= $tries;
		sleep($wait);
	}

	return 1;
}

sub release_lock_dir {
	my ($name) = @_;
	rmdir($LockDir . $name);
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
	$html =~ s/&amp;([\#a-zA-Z0-9]+);/&$1;/g if $AllowCharRefs;

	return $html;
}

sub unquote_html {
	my ($html) = @_;

	$html =~ s/&amp;/&/g;
	$html =~ s/&lt;/</g;
	$html =~ s/&gt;/>/g;

	# Allow character references?
	$html =~ s/&\#(\d+);/chr($1)/ge if $AllowCharRefs;

	return $html;
}

sub get_interwiki_url {
	my ($site) = @_;

	unless ($InterSiteInit) {
		$InterSiteInit = 1;
		my ($status, $data) = read_file($InterFile);

		return "" unless $status;

		%InterSite = split(/\s+/, $data);    # Later consider defensive code
	}

	return $InterSite{$site} if defined $InterSite{$site};
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

		if (($Text{'text'} =~ /$string/i) || ($name =~ /$string/i)) {
			push(@found, $name);
			next;
		}

		if ($FreeLinks && ($name =~ m/_/)) {
			my $freeName = $name;
			$freeName =~ s/_/ /g;
			push(@found, $name) if $freeName =~ /$string/i;
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
		if ($Text{'text'} =~ /$string/i) {
			push(@found, $name);
		}
	}

	return @found;
}

##################
### HTML CACHE ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub try_html_cache {

	return 0 unless $UseCache;
	my $query = $ENV{'QUERY_STRING'};

	if (($query eq "") && ($ENV{'REQUEST_METHOD'} eq "GET")) {
		$query = $HomePage;    # Allow caching of home page.
	}

	unless ($query =~ /^$LinkPattern$/o) {
		unless ($FreeLinks && ($query =~ /^$FreeLinkPattern/o)) {
			return 0;            # Only use cache for simple links
		}
	}

	my $idFile = get_html_cache_filename_for_id($query);

	if (-f $idFile) {
		open(INFILE, "<$idFile") or return 0;
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
		$HtmlDir . "/" . get_directory_for_page_id($id) . "/$id.htm"
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
	create_page_directory($HtmlDir, $id);

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
		$PageDir . "/" . get_directory_for_page_id($id) . "/$id.db"
	);
}

sub open_or_create_page {
	my ($id) = @_;

	# No need to open, if it's already open.
	return if $OpenPageName eq $id;

	%Section  = ();
	%Text     = ();
	my $fname = get_filename_for_page_id($id);

	if (-f $fname) {
		my $data = read_file_or_die($fname);
		%Page = split(/$FS1/o, $data, -1);    # -1 keeps trailing null fields
	}
	else {
		%Page = (
			version   => 3,                     # Data format version
			revision  => 0,                     # Number of edited times
			tscreate  => $^T,                   # Set once at creation
			ts        => $^T,                   # Updated every edit
		);
	}

	print render_error_page_as_html("Bad page version.") if $Page{'version'} != 3;

	$OpenPageName = $id;
}

sub save_page_to_file {

	# NB - Must always call save_page_to_file() within a lock.
	# TODO - Ensure it is so.

	my $file = get_filename_for_page_id($OpenPageName);

	$Page{'revision'} += 1;    # Number of edited times
	$Page{'ts'} = $^T;         # Updated every edit

	create_page_directory($PageDir, $OpenPageName);
	write_string_to_file($file, join($FS1, %Page));
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
	$new    = ucfirst($new);
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

	create_page_directory($PageDir, $new);    # It might not exist yet
	rename($oldfname, $newfname);
	create_page_directory($KeepDir, $new);

	my $oldkeep = normalize_filename(
		$KeepDir . "/" .  get_directory_for_page_id($old) . "/$old.kp"
	);
	my $newkeep = normalize_filename(
		$KeepDir . "/" .  get_directory_for_page_id($new) . "/$new.kp"
	);
	unlink($newkeep) if (-f $newkeep);    # Clean up if needed.
	rename($oldkeep, $newkeep);
	unlink($IndexFile) if ($UseIndex);
	edit_recent_changes(2, $old, $new) if ($doRC);
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
		$KeepDir . "/" . get_directory_for_page_id($page) . "/$page.kp"
	);
	unlink($fname) if -f $fname;

	unlink($IndexFile) if $UseIndex;

	edit_recent_changes(1, $page, "") if $doRC;

	# Currently don't do anything with page text.
}

sub get_page_lock_filename {
	my ($id) = @_;

	return normalize_filename(
		$PageDir . "/" . get_directory_for_page_id($id) . "/$id.lck"
	);
}

sub get_links_from_a_page {
	my ($name, $pagelink, $interlink, $urllink) = @_;

	open_or_create_page($name);
	open_default_text();

	my $text = $Text{'text'};

	$text =~ s/<html>((.|\n)*?)<\/html>/ /ig;
	$text =~ s/<nowiki>(.|\n)*?\<\/nowiki>/ /ig;
	$text =~ s/<pre>(.|\n)*?\<\/pre>/ /ig;
	$text =~ s/<code>(.|\n)*?\<\/code>/ /ig;
	$text =~ s/<perl>(.|\n)*?\<\/perl>/ /ig;
	$text =~ s/<boxes>(.|\n)*?\<\/boxes>/ /ig;

	my @links;
	if ($interlink) {
		$text =~ s/''+/ /g;    # Quotes can adjacent to inter-site links
		$text =~ s/$InterLinkPattern/push(@links, strip_trailing_punct_from_url($1)), ' '/geo;
	}
	else {
		$text =~ s/$InterLinkPattern/ /go;
	}

	if ($urllink) {
		$text =~ s/''+/ /g;    # Quotes can adjacent to URLs
		$text =~ s/$UrlPattern/push(@links, strip_trailing_punct_from_url($1)), ' '/geo;
	}
	else {
		$text =~ s/$UrlPattern/ /go;
	}

	if ($pagelink) {
		if ($FreeLinks) {
			$text =~ s/\[\[$FreeLinkPattern\|[^\]]+\]\]/push(@links, replace_whitespace($1)),' '/geo;
			$text =~ s/\[\[$FreeLinkPattern\]\]/push(@links, replace_whitespace($1)), ' '/geo;
		}

		if ($WikiLinks) {
			$text =~ s/$LinkPattern/push(@links, strip_trailing_punct_from_url($1)), ' '/geo;
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
		foreach my $section (keys %Page) {
			if ($section =~ /^text_/) {
				open_or_create_section($section);
				%Text    = split(/$FS3/o, $Section{'data'}, -1);
				my $oldText = $Text{'text'};
				my $newText = substitute_text_links($old, $new, $oldText);
				if ($oldText ne $newText) {
					$Text{'text'} = $newText;
					$Section{'data'} = join($FS3, %Text);
					$Page{$section} = join($FS2, %Section);
					$changed = 1;
				}
			}
			elsif ($section =~ /^cache_diff/) {
				my $oldText = $Page{$section};
				my $newText = substitute_text_links($old, $new, $oldText);
				if ($oldText ne $newText) {
					$Page{$section} = $newText;
					$changed = 1;
				}
			}

			# Later: add other text-sections (categories) here
		}

		if ($changed) {
			my $file = get_filename_for_page_id($page);
			write_string_to_file($file, join($FS1, %Page));
		}

		rename_keep_text($page, $old, $new);
	}
}

sub substitute_text_links {
	my ($old, $new, $text) = @_;

	# Much of this is taken from the common markup
	%SaveUrl      = ();
	$SaveUrlIndex = 0;
	$text =~ s/$FS//g;    # Remove separators (paranoia)

	if ($RawHtml) {
		$text =~ s/(<html>((.|\n)*?)<\/html>)/store_raw_html($1)/ige;
	}

	$text =~ s/(<pre>((.|\n)*?)<\/pre>)/render_pre_as_stored_html($1)/ige;
	$text =~ s/(<code>((.|\n)*?)<\/code>)/store_raw_html($1)/ige;
	$text =~ s/(<perl>((.|\n)*?)<\/perl>)/render_perl_as_stored_html($1)/ige;
	$text =~ s/(<projects>((.|\n)*?)<\/projects>)/render_projects_as_html($1)/smige;
	$text =~ s/(<outline>((.|\n)*?)<\/outline>)/store_outline($1,"bullets")/smige;
	$text =~ s/(<outline-head>((.|\n)*?)<\/outline>)/store_outline($1,"headers")/smige;
	$text =~ s/(<outline-todo>((.|\n)*?)<\/outline>)/store_outline($1,"todo")/smige;
	$text =~ s/(<components>((.|\n)*?)<\/components>)/render_components_as_html($1)/smige;
	$text =~ s/(<nowiki>((.|\n)*?)<\/nowiki>)/store_raw_html($1)/ige;

	if ($FreeLinks) {
		$text =~ s/\[\[$FreeLinkPattern\|([^\]]+)\]\]/render_sub_free_link_as_stored_html($1,$2,$old,$new)/geo;
		$text =~ s/\[\[$FreeLinkPattern\]\]/render_sub_free_link_as_stored_html($1,"",$old,$new)/geo;
	}

	if ($BracketText) {    # Links like [URL text of link]
		$text =~ s/(\[$UrlPattern\s+([^\]]+?)\])/store_raw_html($1)/geo;
		$text =~ s/(\[$InterLinkPattern\s+([^\]]+?)\])/store_raw_html($1)/geo;
	}

	$text =~ s/(\[?$UrlPattern\]?)/store_raw_html($1)/geo;
	$text =~ s/(\[?$InterLinkPattern\]?)/store_raw_html($1)/geo;

	if ($WikiLinks) {
		$text =~ s/$LinkPattern/render_sub_wiki_link_as_stored_html($1, $old, $new)/geo;
	}

	$text =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;    # Restore saved text
	return $text;
}

######################
### RECENT CHANGES ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub append_recent_changes_log {
	my ($id, $summary, $isEdit, $editTime, $name, $rhost) = @_;

	my %extra;
	$extra{'id'} = $UserID if ($UserID > 0);
	$extra{'name'} = $name if ($name ne "");
	my $extraTemp = join($FS2, %extra);

	# The two fields at the end of a line are kind and extension-hash
	my $rc_line = join(
		$FS3, $editTime, $id, $summary, $isEdit, $rhost, "0", $extraTemp
	);

	open(OUT, ">>$RcFile") or die "$RCName log error: $!";
	print OUT $rc_line . "\n";
	close(OUT);
}

sub edit_recent_changes {
	my ($action, $old, $new) = @_;

	edit_recent_changes_file($RcFile,    $action, $old, $new);
	edit_recent_changes_file($RcOldFile, $action, $old, $new);
}

sub edit_recent_changes_file {
	my ($fname, $action, $old, $new) = @_;

	my ($status, $fileData) = read_file($fname);
	unless ($status) {

		# Save error text if needed.
		my $errorText = (
			"<p><strong>Could not open $RCName log file:" .
			"</strong> $fname<p>Error was:\n<pre>$!</pre>\n"
		);
		print $errorText;    # Maybe handle differently later?
		return;
	}

	my $outrc = "";
	my @rclist = split(/\n/, $fileData);

	RCLINE: foreach my $rcline (@rclist) {
		my ($ts, $page, $junk) = split(/$FS3/o, $rcline);
		if ($page eq $old) {

			# Delete by not adding line to new RC.
			next RCLINE if $action == 1;

			if ($action == 2) {
				$junk = $rcline;
				$junk =~ s/^(\d+$FS3)$old($FS3)/"$1$new$2"/geo;
				$outrc .= $junk . "\n";
			}

			# TODO - What happens here?
		}
		else {
			$outrc .= $rcline . "\n";
		}
	}

	write_string_to_file($fname . ".old", $fileData);    # Backup copy
	write_string_to_file($fname,          $outrc);
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
		while (<$PageDir/$dir/*.db $PageDir/$dir/*/*.db>) {
			s!^$PageDir/!!;
			m!^[^/]+/(\S*).db!;
			my $id = $1;
			push(@pages, $id);
		}
	}

	return sort(@pages);
}

sub get_all_pages_for_entire_site {
	return get_all_pages_from_filesystem() unless $UseIndex;

	my $refresh = get_request_param("refresh", 0);

	if ($IndexInit && !$refresh) {

		# May need to change for mod_perl eventually (cache consistency)
		# Possibly check timestamp of file then?
		return @IndexList;
	}

	if ((!$refresh) && (-f $IndexFile)) {
		my ($status, $rawIndex) = read_file($IndexFile);
		if ($status) {
			%IndexHash = split(/\s+/, $rawIndex);
			@IndexList = sort(keys %IndexHash);
			$IndexInit = 1;
			return @IndexList;
		}

		# If open fails just refresh the index.
	}

	@IndexList = ();
	%IndexHash = ();

	request_index_lock() or return @IndexList;    # Maybe generate? (high load?)
	@IndexList = get_all_pages_from_filesystem();

	foreach (@IndexList) {
		$IndexHash{$_} = 1;
	}

	write_string_to_file($IndexFile, join(" ", %IndexHash));
	$IndexInit = 1;
	release_index_lock();
	return @IndexList;
}

sub get_links_for_entire_site {
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
			if (($unique > 0) && ($seen{$link} != 1)) {
				next;
			}

			if (($exists == 0) && ($pgExists{$link} == 1)) {
				next;
			}

			if (($exists == 1) && ($pgExists{$link} != 1)) {
				next;
			}

			if (($search ne "") && !($link =~ /$search/)) {
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

	request_main_lock() or die(
		"run_page_and_link_update_script could not get main lock"
	);
	unlink($IndexFile) if $UseIndex;

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
	unlink($IndexFile) if ($UseIndex);
	release_main_lock();
}

################
### SECTIONS ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub create_new_section {
	my ($name, $data) = @_;

	%Section = (
		name      => $name,
		version   => 1,     # Data format version.
		revision  => 0,     # Number of times edited.
		tscreate  => $^T,   # Set once at creation.
		ts        => $^T,   # Updated every edit.
		ip        => $ENV{REMOTE_ADDR},
		host      => '',    # Updated only for real edits (may be slow)
		id        => $UserID,
		username  => get_request_param('username', ''),
		data      => $data
	);

	$Page{$name} = join($FS2, %Section);    # Replace with save?
}

sub open_or_create_section {
	my ($name) = @_;

	if (defined $Page{$name}) {
		%Section = split(/$FS2/o, $Page{$name}, -1);
	}
	else {
		create_new_section($name, "");
	}
}

sub save_section { # TODO
	my ($name, $data) = @_;

	$Section{'revision'} += 1;    # Number of edited times
	$Section{'ts'}       = $^T;                         # Updated every edit
	$Section{'ip'}       = $ENV{REMOTE_ADDR};
	$Section{'id'}       = $UserID;
	$Section{'username'} = get_request_param("username", "");
	$Section{'data'}     = $data;
	$Page{$name} = join($FS2, %Section);
}

############
### TEXT ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub open_or_create_text {
	my ($name) = @_;

	if (defined $Page{"text_$name"}) {
		open_or_create_section("text_$name");
		%Text = split(/$FS3/o, $Section{'data'}, -1);
	}
	else {
		%Text = (
			text => (
				"Empty page.\n\n" .
				"Edit this page (below), or try [[$HomePage|the home page]].\n\n" .
				"<!--\n" .
				"\" vim: syntax=wiki\n" .
				"-->\n"
			),
			minor => 0,       # Default as major edit.
			newauthor => 1,   # Default as new author.
			summary   => '',  # TODO - Can we default the summary?
		);

		create_new_section("text_$name", join($FS3, %Text));
	}
}

sub open_default_text {
	open_or_create_text('default');
}

sub save_text { # TODO
	my ($name) = @_;

	save_section("text_$name", join($FS3, %Text));
}

sub save_default_text { # TODO
	save_text('default');
}

#################################
### "KEPT" (whatever that is) ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub open_kept_list { # TODO
	@KeptList = ();
	my $fname    = get_keep_path_for_open_page();
	return unless -f $fname;

	my $data = read_file_or_die($fname);
	@KeptList = split(/$FS1/o, $data, -1);    # -1 keeps trailing null fields
}

sub open_kept_revisions { # TODO
	my ($name) = @_;    # Name of section

	%KeptRevisions = ();
	open_kept_list();

	foreach (@KeptList) {
		my %tempSection = split(/$FS2/o, $_, -1);
		next if ($tempSection{'name'} ne $name);

		$KeptRevisions{$tempSection{'revision'}} = $_;
	}
}

sub open_kept_revision { # TODO
	my ($revision) = @_;

	%Section = split(/$FS2/o, $KeptRevisions{$revision}, -1);
	%Text    = split(/$FS3/o, $Section{'data'},          -1);
}

sub get_keep_path_for_open_page {
	return normalize_filename(
		$KeepDir . "/" . get_directory_for_page_id($OpenPageName) . "/$OpenPageName.kp"
	);
}

sub save_keep_section { # TODO
	my $file = get_keep_path_for_open_page();
	my $data;

	return if ($Section{'revision'} < 1);    # Don't keep "empty" revision

	$Section{'keepts'} = $^T;
	$data = $FS1 . join($FS2, %Section);

	create_page_directory($KeepDir, $OpenPageName);
	append_string_to_file($file, $data);
}

sub expire_keep_file { # TODO
	my ($fname, $data, @kplist, %tempSection, $expirets);

	$fname = get_keep_path_for_open_page();
	return unless -f $fname;

	$data = read_file_or_die($fname);
	@kplist = split(/$FS1/o, $data, -1);    # -1 keeps trailing null fields
	return if (length(@kplist) < 1);    # Also empty

	shift(@kplist) if ($kplist[0] eq "");    # First can be empty
	return if (length(@kplist) < 1);         # Also empty

	%tempSection = split(/$FS2/o, $kplist[0], -1);
	unless (defined $tempSection{'keepts'}) {
		# die("Bad keep file." . join("|", %tempSection));
		return;
	}

	$expirets = $^T - ($KeepDays * 24 * 60 * 60);

	return if ($tempSection{'keepts'} >= $expirets);    # Nothing old enough

	my $anyExpire = 0;
	my $anyKeep   = 0;
	my %keepFlag  = ();
	my $oldMajor  = get_page_cache('oldmajor');
	my $oldAuthor = get_page_cache('oldauthor');

	foreach (reverse @kplist) {
		%tempSection = split(/$FS2/o, $_, -1);
		my $sectName    = $tempSection{'name'};
		my $sectRev     = $tempSection{'revision'};
		my $expire      = 0;

		if ($sectName eq "text_default") {
			if ( ($KeepMajor && ($sectRev == $oldMajor))
				|| ($KeepAuthor && ($sectRev == $oldAuthor))) {
				$expire = 0;
			}
			elsif ($tempSection{'keepts'} < $expirets) {
				$expire = 1;
			}
		}
		else {
			if ($tempSection{'keepts'} < $expirets) {
				$expire = 1;
			}
		}

		if ($expire) {
			$anyExpire = 1;
		}
		else {
			$keepFlag{$sectRev . "," . $sectName} = 1;
			$anyKeep = 1;
		}
	}

	unless ($anyKeep) {    # Empty, so remove file
		unlink($fname);
		return;
	}

	return unless $anyExpire;    # No sections expired

	open(OUT, ">$fname") or die("cant write $fname: $!");

	foreach (@kplist) {
		%tempSection = split(/$FS2/o, $_, -1);
		my $sectName    = $tempSection{'name'};
		my $sectRev     = $tempSection{'revision'};

		if ($keepFlag{$sectRev . "," . $sectName}) {
			print OUT $FS1, $_;
		}
	}

	close(OUT) or die "can't close (expire_keep_file) on $fname: $!";
}

sub rename_keep_text { # TODO
	my ($page, $old, $new) = @_;

	my $fname = normalize_filename(
		$KeepDir . "/" . get_directory_for_page_id($page) . "/$page.kp"
	);
	return unless -f $fname;

	my ($status, $data) = read_file($fname);
	return unless $status;

	my @kplist = split(/$FS1/o, $data, -1); # -1 keeps trailing null fields
	return if (length(@kplist) < 1);        # Also empty

	shift(@kplist) if ($kplist[0] eq "");   # First can be empty
	return if (length(@kplist) < 1);        # Also empty

	my %tempSection = split(/$FS2/o, $kplist[0], -1);

	unless (defined $tempSection{'keepts'}) {
		return;
	}

	# First pass: optimize for nothing changed
	my $changed = 0;
	foreach (@kplist) {
		%tempSection = split(/$FS2/o, $_, -1);
		my $sectName = $tempSection{'name'};

		if ($sectName =~ /^(text_)/) {
			%Text = split(/$FS3/o, $tempSection{'data'}, -1);
			my $newText = substitute_text_links($old, $new, $Text{'text'});
			$changed = 1 if ($Text{'text'} ne $newText);
		}

		# Later add other section types? (maybe)
	}

	return unless $changed;    # No sections changed

	open(OUT, ">$fname") or return;
	foreach (@kplist) {
		%tempSection = split(/$FS2/o, $_, -1);
		my $sectName = $tempSection{'name'};
		if ($sectName =~ /^(text_)/) {
			%Text = split(/$FS3/o, $tempSection{'data'}, -1);
			my $newText = substitute_text_links($old, $new, $Text{'text'});
			$Text{'text'} = $newText;
			$tempSection{'data'} = join($FS3, %Text);
			print OUT $FS1, join($FS2, %tempSection);
		}
		else {
			print OUT $FS1, $_;
		}
	}
	close(OUT);
}

##################
### PAGE CACHE ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub get_page_cache {
	my ($name) = @_;
	return $Page{"cache_$name"};
}

sub set_page_cache {
	my ($name, $data) = @_;
	$Page{"cache_$name"} = $data;
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

	return unless $UseCache;

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
	%UserData = ();
	my ($status, $data) = read_file(get_user_data_filename($UserID));

	unless ($status) {
		$UserID = UID_ENOUSERFILE;
		return;
	}

	%UserData = split(/$FS1/o, $data, -1);    # -1 keeps trailing null fields
}

sub get_user_data_filename {
	my ($id) = @_;

	return "" if ($id < 1);
	return normalize_filename($UserDir . "/" . ($id % 10) . "/$id.db");
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

	unless ($EditAllowed) {
		return 1 if user_is_editor();
		return 0;
	}

	if (-f "$DataDir/noedit") {
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

	my ($status, $data) = read_file("$DataDir/banlist");

	# No file exists, so no ban.
	return 0 unless $status;

	my $ip   = $ENV{'REMOTE_ADDR'};
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
	return 0 if $AdminPass eq "";

	my $userPassword = get_request_param("adminpw", "");
	return 0 if ($userPassword eq "");

	foreach (split(/\s+/, $AdminPass)) {
		next if ($_ eq "");
		return 1 if $userPassword eq $_;
	}

	return 0;
}

sub user_is_editor {
	# Administrators are also editors.
	return 1 if user_is_admin();

	# However, nobody else may be an editor if there's no password.
	return 0 if $EditPass eq "";

	my $userPassword = get_request_param("adminpw", "");
	return 0 if $userPassword eq "";

	foreach (split(/\s+/, $EditPass)) {
		next if ($_ eq "");
		return 1 if $userPassword eq $_;
	}

	return 0;
}

sub do_new_login {

	# TODO - Consider warning if cookie already exists.  Maybe use
	# "replace=1" parameter?

	create_user_directories();
	$SetCookie{'id'}      = get_new_user_id();
	$SetCookie{'randkey'} = int(rand(1000000000));
	$SetCookie{'rev'}     = 1;
	%UserCookie           = %SetCookie;
	$UserID               = $SetCookie{'id'};

	# The cookie will be transmitted in the next header.

	%UserData               = %UserCookie;
	$UserData{'createtime'} = $^T;
	$UserData{'createip'}   = $ENV{REMOTE_ADDR};

	save_user_data();
}

sub do_login {
	my $success = 0;
	my $uid = get_request_param("p_userid", "");
	$uid =~ s/\D//g;
	my $password = get_request_param("p_password", "");

	if (($uid > 199) && ($password ne "") && ($password ne "*")) {
		$UserID = $uid;
		load_user_data();
		if ($UserID > 199) {
			if (defined($UserData{'password'})
				&& ($UserData{'password'} eq $password)) {
				$SetCookie{'id'}      = $uid;
				$SetCookie{'randkey'} = $UserData{'randkey'};
				$SetCookie{'rev'}     = 1;
				$success              = 1;
			}
		}
	}

	print render_page_header_as_html("", "Login Results", "", "norobots");

	if ($success) {
		print "Login for user ID $uid complete.";
	}
	else {
		print "Login for user ID $uid failed.";
	}

	my %data;
	$data{footer} = "<hr>\n" . render_goto_bar_as_html("") . $q->endform;

	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/footer.html"
	);

	print $template->fill_in(HASH => \%data);
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

	request_main_lock() or die "Could not get user-ID lock";

	while (-f get_user_data_filename($id)) {
		$id++;
	}

	write_string_to_file(get_user_data_filename($id), "lock");    # reserve the ID
	release_main_lock();
	return $id;
}

sub save_user_data {
	create_user_directories();
	my $userFile = get_user_data_filename($UserID);
	my $data = join($FS1, %UserData);
	write_string_to_file($userFile, $data);
}

sub create_user_directories {
	unless (-d "$UserDir/0") {
		create_directory($UserDir);

		foreach my $n (0 .. 9) {
			my $subdir = "$UserDir/$n";
			create_directory($subdir);
		}
	}
}

sub user_is_editor_or_render_error {
	return 1 if user_is_editor();

	print "<p>This operation is restricted to site editors only...\n";
	print render_common_footer_as_html();
	return 0;
}

sub user_is_admin_or_render_error {
	return 1 if user_is_admin();

	print "<p>This operation is restricted to administrators only...\n";
	print render_common_footer_as_html();
	return 0;
}

sub set_user_pref_from_request_text {
	my ($param) = @_;

	my $temp = get_request_param("p_$param", "*");

	return if ($temp eq "*");
	$UserData{$param} = $temp;
}

sub set_user_pref_from_request_number {
	my ($param, $integer, $min, $max) = @_;

	my $temp = get_request_param("p_$param", "*");
	return if ($temp eq "*");

	$temp =~ s/[^-\d\.]//g;
	$temp =~ s/\..*// if ($integer);
	return if ($temp eq "");
	return if (($temp < $min) || ($temp > $max));

	$UserData{$param} = $temp;

	# Later consider returning status?
}

sub set_user_pref_from_request_bool {
	my ($param) = @_;

	my $temp = get_request_param("p_$param", "*");

	$UserData{$param} = 1 if ($temp eq "on");
	$UserData{$param} = 0 if ($temp eq "*");

	# It is possible to skip updating by using another value, like "2"
}

#################
### DIFF DATA ###

# XXX - ALL FUNCTION THAT WRITE TO DISK MUST DO SO WITHIN LOCKS.

sub write_diff_log {
	my ($id, $editTime, $diffString) = @_;

	open(OUT, ">>$DataDir/diff_log") or die "cant write diff_log";
	print OUT "------\n" . $id . "|" . $editTime . "\n", $diffString;
	close(OUT);
}

sub update_diffs {
	my ($id, $editTime, $old, $new, $isEdit, $newAuthor) = @_;

	# 0 = "already in lock".
	my $editDiff  = find_differences($old, $new, 0);
	my $oldMajor  = get_page_cache('oldmajor');
	my $oldAuthor = get_page_cache('oldauthor');

	write_diff_log($id, $editTime, $editDiff) if $UseDiffLog;

	set_page_cache('diff_default_minor', $editDiff);

	if ($isEdit || !$newAuthor) {
		open_kept_revisions('text_default');
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
	if (defined($KeptRevisions{$oldRevision})) {
		my %sect = split(/$FS2/o, $KeptRevisions{$oldRevision}, -1);
		my %data = split(/$FS3/o, $sect{'data'}, -1);
		$oldText = $data{'text'};
	}

	# Old revision not found, so no diff.
	return "" if $oldText eq "";

	return find_differences($oldText, $newText, $lock);
}

sub find_differences {
	my ($old, $new, $lock) = @_;

	create_directory($TempDir);
	my $oldName = "$TempDir/old_diff";
	my $newName = "$TempDir/new_diff";

	if ($lock) {
		request_diff_lock() or return "";
		$oldName .= "_locked";
		$newName .= "_locked";
	}

	write_string_to_file($oldName, $old);
	write_string_to_file($newName, $new);

	# TODO - Taint?  Also fully-qualify diff path.
	my $diff_out = `diff $oldName $newName`;
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
	return $file_name unless $ForceLcaseFiles;

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
	my @ScriptPath = split('/', "$ENV{SCRIPT_NAME}");

	$CGI::POST_MAX        = 1024 * 200;    # max 200K posts
	$CGI::DISABLE_UPLOADS = 1;             # no uploads
	$q                    = new CGI;

	# TODO: AUGH! What were they THINKING?! This needs to change. Somehow.
	$^T = time;                            # Reset in case script is persistent

	# Do we want to grab the script name and use it, or ignore it so that
	# things like http://domain/?Wiki_Link work?

	if ($UseScriptName) {
		$ScriptName = pop(@ScriptPath);    # Name used in links
	}
	else {
		$ScriptName = '';
	}

	$IndexInit     = 0;
	$InterSiteInit = 0;
	%InterSite     = ();
	$MainPage      = ".";    # For subpages only, the name of the top-level page
	$OpenPageName  = "";     # Currently open page

	# Create the data directory if it doesn't exist.
	create_directory($DataDir);

	unless (-d $DataDir) {
		print render_error_page_as_html("Could not create $DataDir: $!");
		return 0;
	}

	# Reads in user data.
	init_request_cookie();           # Reads in user data

	return 1;
}

sub init_request_cookie {
	%SetCookie      = ();
	$TimeZoneOffset = 0;
	%UserCookie     = $CookieName ? $q->cookie($CookieName) : ();

	$UserID = $UserCookie{'id'} || 0;
	$UserID =~ s/\D//g;    # Numeric only

	if ($UserID < UID_MINPOSSIBLE) {
		$UserID = UID_ENOCOOKIE;
	}
	else {
		load_user_data($UserID);
	}

	if ($UserID > 199) {
		if (
			($UserData{'id'} != $UserCookie{'id'}) or
			($UserData{'randkey'} != $UserCookie{'randkey'})
		) {
			$UserID   = UID_EBADCOOKIE;
			%UserData = ();    # Invalid.  Later consider warning message.
		}
	}

	$TimeZoneOffset = ($UserData{'tzoffset'} || 0) * (60 * 60);
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

	my $result = $q->param($name);
	return $result if defined $result;
	return $UserData{$name} if defined $UserData{$name};
	return $default;
}

#####################################
### TOP-LEVEL REQUEST DISPATCHERS ###

sub dispatch_browse_request {

	# No parameters.  Browse the home page.
	unless ($q->param) {
		action_browse_page($HomePage);
		return 1;
	}

	# Just index.cgi?PageName.
	if (my $id = get_request_param("keywords", "")) {
		action_browse_page($id) if is_valid_page_id_or_error($id);
		return 1;
	}

	# Otherwise it may be an action.
	my $action  = lc(get_request_param("action", ""));
	my $id      = get_request_param("id", "");

	# Browse a page.
	if ($action eq "browse") {
		action_browse_page($id) if is_valid_page_id_or_error($id);
		return 1;
	}

	# Recent changes.
	if ($action eq "rc") {
		action_browse_page($RCName);
		return 1;
	}

	# Random page.
	if ($action eq "random") {
		action_browse_random_page();
		return 1;
	}

	# Revision history for the current page.
	if ($action eq "history") {
		action_page_history($id) if is_valid_page_id_or_error($id);
		return 1;
	}

	# Request not handled.
	return 0;
}

sub dispatch_change_request {

	my $action = get_request_param("action", "");
	my $id     = get_request_param("id",     "");

	if ($action ne "") {
		$action = lc($action);

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

		if ($action eq "newlogin") {
			$UserID = 0;

			# Also creates a new ID, because $UserID < 400.
			action_open_preferences_editor();
			return;
		}

		print render_error_page_as_html("Invalid action parameter $action");
		return;
	}

	if (get_request_param("edit_prefs", 0)) {
		action_write_updated_preferences();
		return;
	}

	if (get_request_param("edit_ban", 0)) {
		action_write_updated_ban_list();
		return;
	}

	if (get_request_param("enter_login", 0)) {
		do_login();
		return;
	}

	if (get_request_param("edit_links", 0)) {
		action_write_updated_links();
		return;
	}

	my $search = get_request_param("search", "");
	if (($search ne "") || (get_request_param("dosearch", "") ne "")) {
		# Searching for nothing.  Return everything.
		if ($search eq "") {
			print render_page_index_as_html();
			return;
		}

		my @search_results = search_title_and_body($search);
		print render_search_results_page_as_html($search, @search_results);
		return;
	}

	# Handle posted pages
	if (get_request_param("oldtime", "") ne "") {
		$id = get_request_param("title", "");
		action_write_updated_page() if is_valid_page_id_or_error($id);
		return;
	}

	print render_error_page_as_html("Invalid URL.");
}

####################################
### TOP-LEVEL REQUESTS & ACTIONS ###

# TODO - Many of these combine action logic and response HTML.  They
# should be broken into action logic (with a return value), and
# response generators that render the return values of the actions
# into appropriate HTML.  This will let us templatize the responses.

sub redirect_browse_page {
	my ($id, $oldId, $isEdit) = @_;

	if ($oldId ne "") {
		print render_redirect_page_as_html(
			"action=browse&id=$id&oldid=$oldId", $id, $isEdit
		);
	}
	else {
		print render_redirect_page_as_html($id, $id, $isEdit);
	}
}

sub action_browse_page {
	my ($id) = @_;

	open_or_create_page($id);
	open_default_text();

	my $newText  = $Text{'text'};               # For differences
	my $openKept = 0;

	my $revision = get_request_param("revision", "");
	$revision =~ s/\D//g;                       # Remove non-numeric chars

	my $goodRevision = $revision;               # Non-blank only if exists

	if ($revision ne "") {
		open_kept_revisions('text_default');

		$openKept = 1;

		unless (defined $KeptRevisions{$revision}) {
			$goodRevision = "";
		}
		else {
			open_kept_revision($revision);
		}
	}

	# Handle a single-level redirect
	my $oldId = get_request_param("oldid", "");
	if (($oldId eq "") && (substr($Text{'text'}, 0, 10) eq "#REDIRECT ")) {
		$oldId = $id;

		if (($FreeLinks) && ($Text{'text'} =~ /\#REDIRECT\s+\[\[.+\]\]/)) {
			($id) = ($Text{'text'} =~ /\#REDIRECT\s+\[\[(.+)\]\]/);
			$id =~ s/ /_/g;    # Convert from typed form to internal form
		}
		else {
			($id) = ($Text{'text'} =~ /\#REDIRECT\s+(\S+)/);
		}

		if (is_valid_page_id($id) eq "") {

			# Later consider revision in rebrowse?
			redirect_browse_page($id, $oldId, 0);
			return;
		}
		else {               # Not a valid target, so continue as normal page
			$id    = $oldId;
			$oldId = "";
		}
	}

	$MainPage = $id;
	$MainPage =~ s!/.*!!;    # Only the main page name (remove subpage)

	# Need to know if this is a diff (also looking at older revision)
	# so we can stop search robots from indexing it.
	my $allDiff = get_request_param("alldiff", 0);
	if ($allDiff != 0) {
		$allDiff = get_request_param("defaultdiff", 1);
	}

	if (($id eq "$RCName") && get_request_param("norcdiff", 1)) {
		$allDiff = 0;          # Only show if specifically requested
	}

	my $header_revision = $revision;

	my $showDiff = get_request_param("diff", $allDiff);
	my $diffRevision;
	if ($UseDiff && $showDiff) {
		$diffRevision = $goodRevision;
		$diffRevision = get_request_param("diffrevision", $diffRevision);

		# Later try to avoid the following keep-loading if possible?
		open_kept_revisions('text_default') unless $openKept;
		$header_revision ||= 1;
	}

	# TODO - Put render_page_header_as_html() into each page renderer, so we can
	# them template-ize them.

	my $fullHtml = render_page_header_as_html(
		$id, quote_html($id), $oldId, $header_revision
	);

	if ($UseDiff && $showDiff) {
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

	$fullHtml .= render_wiki_page_as_html($Text{'text'}) . "\n";    #  . "<hr>\n";

	if ($id eq "$RCName") {
		print $fullHtml;
		print render_recent_changes_page_as_html();
		print render_complex_page_footer_as_html($id, $goodRevision);
		return;
	}

	$fullHtml .= render_complex_page_footer_as_html($id, $goodRevision);
	print $fullHtml;

	# Don't cache special versions.
	return if ($showDiff || ($revision ne ""));

	update_html_cache($id, $fullHtml) if $UseCache;
}

sub action_browse_random_page {
	my @pageList = get_all_pages_for_entire_site();
	my $id       = $pageList[rand @pageList];
	redirect_browse_page($id, "", 0);
}

sub action_page_history {
	my ($id) = @_;

	print render_page_header_as_html("", quote_html("History of $id"), "", "norobots") . "<br>";

	open_or_create_page($id);
	open_default_text();

	my $canEdit = user_can_edit($id);
	$canEdit = 0;                   # Turn off direct "Edit" links

	my $html = render_history_line_as_html($id, $Page{'text_default'}, $canEdit, 1);

	open_kept_revisions('text_default');

	foreach (reverse sort { $a <=> $b } keys %KeptRevisions) {
		next if ($_ eq "");           # (needed?)
		$html .= render_history_line_as_html($id, $KeptRevisions{$_}, $canEdit, 0);
	}

	print $html, render_common_footer_as_html();
}

sub action_lock_or_unlock_entire_site_edits {
	print render_page_header_as_html(
		"", "Set or Remove global edit lock", "", "norobots"
	);

	return unless user_is_admin_or_render_error();

	my $fname = "$DataDir/noedit";

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
	print render_page_header_as_html("", "Set or Remove page edit lock", "", "norobots");
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
		render_page_header_as_html("", "Removing edit lock", "", "norobots"),
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
			"", "Maintenance on all pages", "", "norobots"
		),
		"<br>"
	);

	my $fname = "$DataDir/maintain";
	unless (user_is_admin()) {
		if ((-f $fname) && ((-M $fname) < 0.5)) {
			print(
				"Maintenance not done.  ",
				"(Maintenance can only be done once every 12 hours.)  ",
				"Remove the \"maintain\" file or wait.",
				render_common_footer_as_html()
			);
			return;
		}
	}

	request_main_lock() or die "Could not get maintain-lock";

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

	$fname = "$DataDir/editlinks";
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

# Edit ban list.

sub action_open_ban_list_editor {
	print render_page_header_as_html("", "Editing Banned list", "", "norobots");
	return unless user_is_admin_or_render_error();

	my ($status, $banList) = read_file("$DataDir/banlist");
	$banList = "" unless $status;
	print(
		render_form_start_as_html(),
		render_hidden_input_as_html("edit_ban", 1),
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
		$q->endform,
		render_simple_page_footer_as_html()
	);
}

sub action_write_updated_ban_list {
	print render_page_header_as_html("", "Updating Banned list", "", "norobots");

	return unless user_is_admin_or_render_error();

	my $fname = "$DataDir/banlist";
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

	my $recentName = $RCName;
	$recentName =~ s/_/ /g;

	do_new_login() if $UserID < 400;

	print(
		render_page_header_as_html("", "Editing Preferences", "", "norobots"),
		render_form_start_as_html(),
		render_hidden_input_as_html("edit_prefs", 1),
		"\n",
		"<b>User Information:</b>\n",
		"<br>Your User ID number: $UserID <b>(Needed to log back in.)</b>\n",
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

	if ($AdminPass ne "") {
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
		render_form_text_input_as_html('rcdays', $RcDefault, 4, 9),
		"<br>",
		render_form_checkbox_as_html(
			'rcnewtop', $RecentTop, 'Most recent changes on top'
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
		$q->popup_menu(
			-name   => 'p_rcshowedit',
			-values => [0, 1, 2],
			-labels => \%labels,
			-default => get_request_param("rcshowedit", $ShowEdits)
		),
		"<br>",
		render_form_checkbox_as_html(
			'rcchangehist', 1, 'Use "changes" as link to history'
		),
	);

	if ($UseDiff) {
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
			$q->popup_menu(
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
		render_date_time_as_text($^T - $TimeZoneOffset),
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

	if ($UserCSS) {
		print(
			"<br>Site-wide custom CSS (don't put &lt;style&gt; tags in here)<br>",
			q{<textarea name="p_css" rows="4" cols="65">},
			($UserData{'css'} || ''),
			q{</textarea>},
		);
	}

	my %data;
	$data{footer} = (
		"<br>" .
		q{<input type="submit" name="Save" value="Save">} .
		"<hr>\n" .
		render_goto_bar_as_html("") .
		$q->endform
	);

	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/footer.html"
	);

	print $template->fill_in(HASH => \%data);
}

sub action_write_updated_preferences {
	# All link bar settings should be updated before printing the header.
	set_user_pref_from_request_bool("toplinkbar");
	set_user_pref_from_request_bool("linkrandom");

	print(
		render_page_header_as_html(
			"", "Saving Preferences", "", "norobots"
		),
		"<br>"
	);

	if ($UserID < UID_MINLEGAL) {
		print "<b>Invalid UserID $UserID, preferences not saved.</b>";

		if ($UserID == UID_ENOCOOKIE) {
			print "<br>(Preferences require cookies, but no cookie was sent.)";
		}

		print render_common_footer_as_html();
		return;
	}

	my $username = get_request_param("p_username", "");

	if ($FreeLinks) {
		$username =~ s/^\[\[(.+)\]\]/$1/;    # Remove [[ and ]] if added
		$username = ucfirst($username);
	}

	if ($username eq "") {
		print "UserName removed.<br>";
		$UserData{'username'} = undef;
	}
	elsif ((!$FreeLinks) && (!($username =~ /^$LinkPattern$/o))) {
		print "Invalid UserName $username: not saved.<br>\n";
	}
	elsif ($FreeLinks && (!($username =~ /^$FreeLinkPattern$/o))) {
		print "Invalid UserName $username: not saved.<br>\n";
	}
	elsif (length($username) > 50) {    # Too long
		print "UserName must be 50 characters or less. (not saved)<br>\n";
	}
	else {
		print "UserName $username saved.<br>";
		$UserData{'username'} = $username;
	}

	my $password = get_request_param("p_password", "");

	if ($password eq "") {
		print "Password removed.<br>";
		$UserData{'password'} = undef;
	}
	elsif ($password ne "*") {
		print "Password changed.<br>";
		$UserData{'password'} = $password;
	}

	if ($AdminPass ne "") {
		$password = get_request_param("p_adminpw", "");
		if ($password eq "") {
			print "Administrator password removed.<br>";
			$UserData{'adminpw'} = undef;
		}
		elsif ($password ne "*") {
			print "Administrator password changed.<br>";
			$UserData{'adminpw'} = $password;
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

	if ($UseDiff) {
		set_user_pref_from_request_bool("norcdiff");
		set_user_pref_from_request_bool("diffrclink");
		set_user_pref_from_request_bool("alldiff");
		set_user_pref_from_request_number("defaultdiff", 1, 1, 3);
	}

	set_user_pref_from_request_number("rcshowedit", 1, 0,    2);
	set_user_pref_from_request_number("tzoffset",   0, -999, 999);
	set_user_pref_from_request_number("editrows",   1, 1,    999);
	set_user_pref_from_request_number("editcols",   1, 1,    999);
	set_user_pref_from_request_text("css") if $UserCSS;

	print(
		"Server time: ",
		render_date_time_as_text($^T - $TimeZoneOffset),
		"<br>"
	);

	$TimeZoneOffset = get_request_param("tzoffset", 0) * (60 * 60);
	print "Local time: ", render_date_time_as_text($^T), "<br>";

	save_user_data();
	print "<b>Preferences saved.</b>", render_common_footer_as_html();
}

# Edit links.

sub action_open_links_editor {
	print render_page_header_as_html("", "Editing Links", "", "norobots");

	if ($AdminDelete) {
		return unless user_is_admin_or_render_error();
	}
	else {
		return unless user_is_editor_or_render_error();
	}

	print(
		render_form_start_as_html(),
		render_hidden_input_as_html("edit_links", 1),
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
		$q->checkbox(
			-name     => "p_changerc",
			-override => 1,
			-checked  => 1,
			-label    => "Edit $RCName"
		),
		"<br>\n",
		$q->checkbox(
			-name     => "p_changetext",
			-override => 1,
			-checked  => 1,
			-label    => "Substitute text for rename"
		),
		"<br>", q{<input type="submit" name="Edit" value="Edit">},
		"<hr>\n",
		render_goto_bar_as_html(""),
		$q->endform,
		render_simple_page_footer_as_html()
	);
}

sub action_write_updated_links {
	print render_page_header_as_html("", "Updating Links", "", "norobots");

	if ($AdminDelete) {
		return unless user_is_admin_or_render_error();
	}
	else {
		return unless user_is_editor_or_render_error();
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
		print render_page_header_as_html("", "Editing Denied", "", "norobots");

		if (user_is_banned()) {
			print(
				"Editing not allowed: user, ip, or network is blocked.",
				"<p>Contact the system administrator for more information."
			);
		}
		else {
			print "Editing not allowed: $SiteName is read-only.";
		}

		print render_common_footer_as_html();
		return;
	}

	open_or_create_page($id);
	open_default_text();

	my $pageTime = $Section{'ts'};
	my $header   = "Editing $id";

	# Old revision handling
	my $revision = get_request_param("revision", "");
	$revision =~ s/\D//g;    # Remove non-numeric chars
	if ($revision ne "") {
		open_kept_revisions('text_default');
		if (defined $KeptRevisions{$revision}) {
			open_kept_revision($revision);
			$header = "Editing Revision $revision of $id";
		}
		else {
			$revision = "";

			# Later look for better solution, like error message?
		}
	}

	my $oldText = $Text{'text'};

	if ($preview && !$isConflict) {
		$oldText = $newText;
	}

	my $editRows = get_request_param("editrows", 20);
	my $editCols = get_request_param("editcols", 65);

	print render_page_header_as_html("", quote_html($header), "", "norobots");

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
		render_form_start_as_html(),
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
		$q->textfield(
			-name      => 'summary',
			-default   => $summary,
			-override  => 1,
			-size      => 60,
			-maxlength => 200
		)
	);

	if (get_request_param("recent_edit") eq "on") {
		print(
			"<br>",
			$q->checkbox(
				-name    => 'recent_edit',
				-checked => 1,
				-label   => 'This change is a minor edit.'
			)
		);
	}
	else {
		print(
			"<br>",
			$q->checkbox(
				-name  => 'recent_edit',
				-label => 'This change is a minor edit.'
			)
		);
	}

	print q{<br><input type="submit" name="Save" value="Save">};

	my $userName = get_request_param("username", "");
	if ($userName ne "") {
		print " (Your user name is " . render_unnamed_page_link_as_html($userName) . ") ";
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

		$MainPage = $id;
		$MainPage =~ s!/.*!!;    # Only the main page name (remove subpage)

		print(
			render_wiki_page_as_html($oldText) .
			"<hr>\n",
			"<h2>Preview only, not yet saved</h2>\n"
		);
	}

	my %data;

	$data{footer} = (
		render_history_link_as_html($id, "View other revisions") .
		"<br>\n" .
		render_goto_bar_as_html($id) .
		$q->endform
	);

	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/footer.html"
	);

	print $template->fill_in(HASH => \%data);
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
		print render_error_page_as_html("[[Sample Undefined Page]] cannot be defined.");
		return;
	}

	$string  =~ s/$FS//go;
	$summary =~ s/$FS//go;
	$summary =~ s/[\r\n]//g;

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
			| huola\.com | sexyongpin | mianfei | midiwu | nanting | news123\.org | guilinhotel
			| shop263.com | 218\.244\.47\.217
			| www\.wjmgy\.com | 61\.135\.136\.130
			| www\.etoo\.cn | 210\.192\.124\.153
			| www\.timead\.net
			| www\.paite\.net
			| www\.rr365\.net
			| www\.ronren\.com
			| csnec\.net | \d+\.com | bjzyy\.com | lifuchao\.com | pfxb\.com | qzkfw\.com | rxbkfw\.com | xyxy\.com | zhqzw\.com
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
	request_main_lock() or die "Could not get editing lock";

	# Consider extracting lock section into sub, and eval-wrap it?
	# (A few called routines can die, leaving locks.)
	open_or_create_page($id);
	open_default_text();

	my $old    = $Text{'text'};
	my $oldrev = $Section{'revision'};
	my $pgtime = $Section{'ts'};

	my $preview = 0;
	$preview = 1 if (get_request_param("Preview", "") ne "");

	if (!$preview && ($old eq $string)) {    # No changes (ok for preview)
		release_main_lock();
		redirect_browse_page($id, "", 1);
		return;
	}

	# Later extract comparison?
	my $newAuthor;
	if (($UserID > 399) || ($Section{'id'} > 399)) {
		$newAuthor = ($UserID ne $Section{'id'});    # known user(s)
	}
	else {
		$newAuthor = ($Section{'ip'} ne $authorAddr);    # hostname fallback
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
	if (($oldrev > 0) && ($newAuthor && ($oldtime != $pgtime))) {
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
		set_page_cache('oldmajor', $Section{'revision'});
	}

	if ($newAuthor) {
		set_page_cache('oldauthor', $Section{'revision'});
	}

	save_keep_section();
	expire_keep_file();

	if ($UseDiff) {
		update_diffs($id, $editTime, $old, $string, $isEdit, $newAuthor);
	}

	$Text{'text'}      = $string;
	$Text{'minor'}     = $isEdit;
	$Text{'newauthor'} = $newAuthor;
	$Text{'summary'}   = $summary;
	$Section{'host'}   = get_remote_host(1);

	save_default_text();
	save_page_to_file();
	append_recent_changes_log($id, $summary, $isEdit, $editTime, $user, $Section{'host'});

	if ($UseCache) {
		unlink_html_cache($id);    # Old cached copy is invalid
		if ($Page{'revision'} == 1) {    # If this is a new page...
			clear_cached_pages_linking_to($id);       # ...uncache pages linked to this one.
		}
	}

	if ($UseIndex && ($Page{'revision'} == 1)) {
		unlink($IndexFile);              # Regenerate index on next request
	}

	release_main_lock();
	redirect_browse_page($id, "", 1);
}

######################
### PAGE RENDERERS ###

# TODO - These are prime candidates for templates.

sub render_login_page_as_html {
	return(
		render_page_header_as_html("", "Login", "", "norobots") .
		render_form_start_as_html() .
		render_hidden_input_as_html("enter_login", 1),
		"\n" .
		"<br>User ID number: " .
		$q->textfield(
			-name      => 'p_userid',
			-value     => '',
			-size      => 15,
			-maxlength => 50
		) .
		"<br>Password: " .
		q{<input type="password" name="p_password" size=15 maxlength=50>} .
		"<br>" .
		q{<input type="submit" name="Login" value="Login">} .
		"<hr>\n" .
		render_goto_bar_as_html("") .
		$q->endform .
		render_simple_page_footer_as_html()
	);
}

sub render_wiki_page_as_html {
	my ($pageText) = @_;

	%SaveUrl         = ();
	%SaveNumUrl      = ();
	$SaveUrlIndex    = 0;
	$SaveNumUrlIndex = 0;
	$pageText =~ s/$FS//go;    # Remove separators (paranoia)

	if ($RawHtml) {
		$pageText =~ s/<html>((.|\n)*?)<\/html>/store_raw_html($1)/ige;
	}

	$pageText = quote_html($pageText);
	$pageText =~ s/\\ *\r?\n/ /g;    # Join lines with backslash at end
	$pageText = render_common_markup_as_html($pageText, 1, 0);  # Multi-line markup
	$pageText = render_line_based_markup_as_html($pageText);    # Line-oriented markup
	$pageText =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;   # Restore saved text
	$pageText =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;   # Restore nested saved text

	return $pageText;
}

sub render_page_index_as_html {
	return(
		render_page_header_as_html("", "Index of all pages", "", "norobots") .
		"<br>" .
		render_list_of_page_names_as_html(get_all_pages_for_entire_site()) .
		render_common_footer_as_html()
	);
}

sub render_error_page_as_html {
	my @errors = @_;

	my $html = render_page_header_as_html("", "Submission error...", "", "norobots");

	foreach (@errors) {
		$html .= "<h2>$_</h2>";
	}

	$html .= render_complex_page_footer_as_html("SubmissionError", "");

	return $html;
}

sub render_recent_changes_page_as_html {

	# TODO - Include the page header & footer.

	my $html = "";

	my $starttime = 0;
	if (get_request_param("from", 0)) {
		$starttime = get_request_param("from", 0);
		$html .= "<h2>Updates since " . render_date_time_as_text($starttime) . "</h2>\n";
	}
	else {
		my $daysago = get_request_param("days", 0);
		$daysago = get_request_param("rcdays", 0) unless $daysago;

		if ($daysago) {
			$starttime = $^T - ((24 * 60 * 60) * $daysago);
			$html .= (
				"<h2>Updates in the last $daysago day" .
				(($daysago != 1) ? "s" : "") .
				"</h2>\n"
			);
		}
	}

	if ($starttime == 0) {
		$starttime = $^T - ((24 * 60 * 60) * $RcDefault);
		$html .= "<h2>Updates in the last $RcDefault days</h2>\n";
	}

	# Read rclog data (and oldrclog data if needed)
	my ($status, $fileData) = read_file($RcFile);
	my $errorText = "";

	unless ($status) {

		# Save error text if needed.
		$errorText = (
			"<p><strong>Could not open $RCName log file:" .
			"</strong> $RcFile<p>Error was:\n<pre>$!</pre>\n" .
			"<p>Note: This error is normal if no changes" .
			"have been made.\n"
		);
	}

	my @fullrc = split(/\n/, $fileData);
	my $firstTs = 0;

	if (@fullrc > 0) {    # Only false if no lines in file
		($firstTs) = split(/$FS3/o, $fullrc[0]);
	}

	if (($firstTs == 0) || ($starttime <= $firstTs)) {
		($status, my $oldFileData) = read_file($RcOldFile);
		if ($status) {
			@fullrc = split(/\n/, $oldFileData . $fileData);
		}
		else {
			if ($errorText ne "") {    # could not open either rclog file
				$html .= (
					$errorText .
					"<p><strong>Could not open old $RCName log file:" .
					"</strong> $RcOldFile<p>Error was:\n<pre>$!</pre>\n"
				);
				return;
			}
		}
	}

	my $lastTs = 0;
	if (@fullrc > 0) {             # Only false if no lines in file
		($lastTs) = split(/$FS3/o, $fullrc[$#fullrc]);
	}

	$lastTs++ if (($^T - $lastTs) > 5);    # Skip last unless very recent

	my $idOnly = get_request_param("rcidonly", "");
	if ($idOnly ne "") {
		$html .= (
			"<b>(for " .
			render_script_link_as_html($idOnly, $idOnly) .
			" only)</b><br>"
		);
	}

	my $showbar   = 0;
	foreach my $i (@RcDays) {
		$html .= " | " if $showbar;
		$showbar = 1;
		$html .= render_script_link_as_html(
			"action=rc&days=$i", "$i day" . (($i != 1) ? "s" : "")
		);
	}

	$html .=(
		"<br>" .
		render_script_link_as_html(
			"action=rc&from=$lastTs", "List new changes starting from"
		) .
		" " .
		render_date_time_as_text($lastTs) .
		"<br>\n"
	);

	# Later consider a binary search?

	my $ts;
	my $i = 0;
	while ($i < @fullrc) {    # Optimization: skip old entries quickly
		($ts) = split(/$FS3/o, $fullrc[$i]);
		if ($ts >= $starttime) {
			$i -= 1000 if ($i > 0);
			last;
		}
		$i += 1000;
	}

	$i -= 1000 if (($i > 0) && ($i >= @fullrc));
	for (; $i < @fullrc; $i++) {
		($ts) = split(/$FS3/o, $fullrc[$i]);
		last if ($ts >= $starttime);
	}

	if ($i == @fullrc) {
		$html .= (
			"<br><strong>No updates since " .
			render_date_time_as_text($starttime) .
			"</strong><br>\n"
		);
	}
	else {
		splice(@fullrc, 0, $i);    # Remove items before index $i

		# Later consider an end-time limit (items older than X)
		$html .= render_recent_changes_found_as_html(@fullrc);
	}

	$html .= "<p>Page generated " . render_date_time_as_text($^T) . "<br>\n";

	return $html;
}

sub render_redirect_page_as_html {
	my ($newid, $name, $isEdit) = @_;

	# Normally get URL from script, but allow override.
	my $url = ($FullUrl || $q->url(-full => 1)) . "?" . $newid;

	my $html;
	if ($RedirType < 3) {
    # Use CGI.pm
		if ($RedirType == 1) {
			# NOTE: do NOT use -method (does not work with old CGI.pm versions)
			# Thanks to Daniel Neri for fixing this problem.
			$html = $q->redirect(-uri => $url);
		}
		else {
			# Minimal header.
			$html = "Status: 302 Moved\n";
			$html .= "Location: $url\n";
			$html .= "Content-Type: text/html\n";    # Needed for browser failure
			$html .= "\n";
		}

		$html .= "\nYour browser should go to the $newid page.";
		$html .= "  If it does not, click <a href=\"$url\">$name</a>";
		$html .= " to continue.";
	}
	else {
		if ($isEdit) {
			$html = render_page_header_as_html("", "Thanks for editing...", "", "norobots");
			$html .= "Thank you for editing <a href=\"$url\">$name</a>.";
		}
		else {
			$html = render_page_header_as_html("", "Link to another page...", "", "norobots");
		}

		$html .= "\n<p>Follow the <a href=\"$url\">$name</a> link to continue.";
	}

	return $html;
}

sub render_search_results_page_as_html {
	my $search_string = shift;
	my @search_results = @_;
	return (
		render_page_header_as_html(
			"", quote_html("Search for: $search_string"), "", "norobots"
		) .
		"<br>" .
		render_list_of_page_names_as_html(@search_results) .
		render_common_footer_as_html()
	);
}

sub render_links_page_as_html {
	my $html = (
		render_page_header_as_html(
			"", quote_html("Full Link List"), "", "norobots"
		) .
		# Extra line to get below the logo.
		"<hr>" .
		render_link_list_as_html(get_links_for_entire_site()) .
		"\n"
	);

	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/footer.html"
	);

	$html .= $template->fill_in(HASH => {});
	return $html;
}

######################
### HTML RENDERERS ###

sub render_diff_text_as_html {
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

sub render_diff_as_html {
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

	$useMajor  = 0 if ($useMajor  && ($diffText eq get_cache_diff("major")));
	$useMinor  = 0 if ($useMinor  && ($diffText eq get_cache_diff("minor")));
	$useAuthor = 0 if ($useAuthor && ($diffText eq get_cache_diff("author")));
	$useMajor  = 0 if (
		(!defined(get_page_cache('oldmajor'))) or
		(get_page_cache("oldmajor") < 1)
	);

	$useAuthor = 0 if (
		(!defined(get_page_cache('oldauthor'))) or
		(get_page_cache("oldauthor") < 1)
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
		($diffType != 2) &&
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

sub render_diff_color_as_html {
	my ($diff, $color) = @_;

	$diff =~ s/(^|\n)[<>]/$1/g;
	$diff = quote_html($diff);

	# Do some of the Wiki markup rules:
	%SaveUrl         = ();
	%SaveNumUrl      = ();
	$SaveUrlIndex    = 0;
	$SaveNumUrlIndex = 0;

	$diff =~ s/$FS//go;
	$diff = render_common_markup_as_html($diff, 0, 1);  # No images, all patterns
	$diff =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;    # Restore saved text
	$diff =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;    # Restore nested saved text
	$diff =~ s/\r?\n/<br>/g;

	return(
		"<table width=\"95\%\" bgcolor=#$color><tr><td>\n" .
		$diff .
		"</td></tr></table>\n"
	);
}

sub render_form_text_area_as_html {
	my ($name, $text, $rows, $cols) = @_;

	if (get_request_param("editwide", 1)) {
		return $q->textarea(
			-name     => $name,
			-default  => $text,
			-rows     => $rows,
			-columns  => $cols,
			-override => 1,
			-style    => 'width:100%',
			-wrap     => 'virtual'
		);
	}

	return $q->textarea(
		-name     => $name,
		-default  => $text,
		-rows     => $rows,
		-columns  => $cols,
		-override => 1,
		-wrap     => 'virtual'
	);
}

sub render_form_text_input_as_html {
	my ($name, $default, $size, $max) = @_;

	my $text = get_request_param($name, $default);

	return $q->textfield(
		-name      => "p_$name",
		-default   => $text,
		-override  => 1,
		-size      => $size,
		-maxlength => $max
	);
}

sub render_form_checkbox_as_html {
	my ($name, $default, $label) = @_;

	my $checked = (get_request_param($name, $default) > 0);

	return $q->checkbox(
		-name     => "p_$name",
		-override => 1,
		-checked  => $checked,
		-label    => $label
	);
}

sub render_common_markup_as_html {
	my ($text, $useImage, $doLines) = @_;
	local $_ = $text;

	# 2 = do line-oriented only
	if ($doLines < 2) {
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

		if ($HtmlTags) {
			foreach my $t (@HtmlPairs) {
				s/\&lt;$t(\s[^<>]+?)?\&gt;(.*?)\&lt;\/$t\&gt;/<$t$1>$2<\/$t>/gis;
			}

			foreach my $t (@HtmlSingle) {
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

		if ($HtmlLinks) {
			s/\&lt;A(\s[^<>]+?)\&gt;(.*?)\&lt;\/a\&gt;/render_href_as_stored_html($1, $2)/gise;
		}

		if ($FreeLinks) {

			# Consider: should local free-link descriptions be conditional?
			# Also, consider that one could write [[Bad Page|Good Page]]?
			s/\[\[$FreeLinkPattern\|([^\]]+)\]\]/render_page_or_edit_link_as_stored_html($1, $2)/geo;
			s/\[\[$FreeLinkPattern\]\]/render_page_or_edit_link_as_stored_html($1, "")/geo;
		}

		if ($BracketText) {    # Links like [URL text of link]
			s/\[$UrlPattern\s+([^\]]+?)\]/render_bracketed_url_as_stored_html($1, $2)/geos;
			s/\[$InterLinkPattern\s+([^\]]+?)\]/render_bracketed_inter_page_link_as_stored_html($1, $2)/geos;

			if ($WikiLinks && $BracketWiki) {    # Local bracket-links
				s/\[$LinkPattern\s+([^\]]+?)\]/render_bracketed_link_as_stored_html($1, $2)/geos;
			}
		}

		s/\[$UrlPattern\]/render_bracketed_url_as_stored_html($1, "")/geo;
		s/\[$InterLinkPattern\]/render_bracketed_inter_page_link_as_stored_html($1, "")/geo;
		s/$UrlPattern/render_url_as_stored_html($1, $useImage)/geo;
		s/$InterLinkPattern/render_and_store_inter_page_link($1)/geo;

		if ($WikiLinks) {
			s/$LinkPattern/render_page_or_edit_link_as_html($1, "")/geo;
		}

		s/$RFCPattern/render_rfc_link_as_stored_html($1)/geo;
		s/$ISBNPattern/render_isbn_link_as_stored_html($1)/geo;

		if ($ThinLine) {
			s/----+/<hr noshade size=1>/g;
			s/====+/<hr noshade size=2>/g;
		}
		else {
			s/----+/<hr>/g;
		}
	}

	if ($doLines) {    # 0 = no line-oriented, 1 or 2 = do line-oriented
		# The quote markup patterns avoid overlapping tags (with 5 quotes)
		# by matching the inner quotes for the strong pattern.
		s/(\'*)\'\'\'(.*?)\'\'\'/$1<strong>$2<\/strong>/g;
		s/\'\'(.*?)\'\'/<em>$1<\/em>/g;

		if ($UseHeadings) {
			s/(^|\n)\s*(\=+)\s+([^\n]+)\s+\=+/render_wiki_heading_as_html($1, $2, $3)/geo;
		}
	}

	return $_;
}

sub render_line_based_markup_as_html {
	my ($pageText) = @_;

	my @htmlStack = ();
	my $depth     = 0;
	my $pageHtml  = "";

	foreach (split(/\n/, $pageText)) {    # Process lines one-at-a-time
		$_ .= "\n";

		my ($code, $depth);
		if (s/^(\;+)([^:]+\:?)\:?/<dt>$2<dd>/) {
			$code  = "DL";
			$depth = length $1;
		}
		elsif (s/^(\:+)/<dt><dd>/) {
			$code  = "DL";
			$depth = length $1;
		}
		elsif (s/^(\*+)/<li>/) {
			$code  = "UL";
			$depth = length $1;
		}
		elsif (s/^(\#+)/<li>/) {
			$code  = "OL";
			$depth = length $1;
		}
		elsif (/^[ \t].*\S/) {
			$code  = "PRE";
			$depth = 1;
		}
		else {
			$depth = 0;
		}

		while (@htmlStack > $depth) {    # Close tags as needed
			my $code = pop(@htmlStack);
			$pageHtml .= "</$code>";
			$pageHtml .= "</td></tr></table>" if $code eq 'PRE';
		}

		if ($depth > 0) {
			$depth = $IndentLimit if ($depth > $IndentLimit);

			if (@htmlStack) {              # Non-empty stack
				my $oldCode = pop(@htmlStack);

				if ($oldCode ne $code) {

					$pageHtml .= "</$oldCode>";

					# Handle PRE being in tables.
					$pageHtml .= "</td></tr></table>" if $oldCode eq 'PRE';
					$pageHtml .= "<table border='1' cellspacing='0'><tr><td nowrap>"
						if $code eq 'PRE';

					$pageHtml .= "<$code>";
				}

				push(@htmlStack, $code);
			}

			while (@htmlStack < $depth) {
				push(@htmlStack, $code);

				$pageHtml .= "<table border='1' cellspacing='0'><tr><td nowrap>"
					if $code eq 'PRE';

				$pageHtml .= "<$code>\n";
			}
		}

		s/^\s*$/<p>\n/;    # Blank lines become <p> tags

		$pageHtml .= render_common_markup_as_html($_, 1, 2);    # Line-oriented common markup
	}

	while (@htmlStack > 0) {                   # Clear stack
		my $code = pop(@htmlStack);
		$pageHtml .= "</$code>";
		$pageHtml .= "</td></tr></table>" if $code eq 'PRE';
	}

	return $pageHtml;
}

sub render_recent_changes_found_as_html {
	my @outrc = @_;

	my %extra      = ();
	my %changetime = ();
	my %pagecount  = ();

	my $showedit = get_request_param("rcshowedit", $ShowEdits);
	$showedit    = get_request_param("showedit",   $showedit);

	if ($showedit != 1) {
		my @temprc = ();
		foreach my $rcline (@outrc) {
			my ($ts, $pagename, $summary, $isEdit, $host) = split(/$FS3/o, $rcline);
			if ($showedit == 0) {    # 0 = No edits
				push(@temprc, $rcline) unless $isEdit;
			}
			else {                   # 2 = Only edits
				push(@temprc, $rcline) if $isEdit;
			}
		}
		@outrc = @temprc;
	}

	# Later consider folding into loop above?
	# Later add lines to assoc. pagename array (for new RC display)
	foreach my $rcline (@outrc) {
		my ($ts, $pagename) = split(/$FS3/o, $rcline);
		$pagecount{$pagename}++;
		$changetime{$pagename} = $ts;
	}

	my $date   = "";
	my $inlist = 0;
	my $html   = "";

	my $all    = get_request_param("rcall", 0);
	$all       = get_request_param("all", $all);

	my $newtop = get_request_param("rcnewtop", $RecentTop);
	$newtop    = get_request_param("newtop", $newtop);

	my $idOnly = get_request_param("rcidonly", "");

	@outrc = reverse @outrc if ($newtop);
	foreach my $rcline (@outrc) {
		my ($ts, $pagename, $summary, $isEdit, $host, $kind, $extraTemp) = split(
			/$FS3/o, $rcline
		);

		# Later: need to change $all for new-RC?
		next if ((!$all) && ($ts < $changetime{$pagename}));
		next if (($idOnly ne "") && ($idOnly ne $pagename));

		%extra = split(/$FS2/o, $extraTemp, -1);
		if ($date ne render_date_as_text($ts)) {
			$date = render_date_as_text($ts);
			if ($inlist) {
				$html .= "</UL>\n";
				$inlist = 0;
			}
			$html .= "<p><strong>" . $date . "</strong><p>\n";
		}

		unless ($inlist) {
			$html .= "<UL>\n";
			$inlist = 1;
		}

		$host = quote_html($host);

		my $author;
		if (defined($extra{'name'}) && defined($extra{'id'})) {
			$author = render_author_link_as_html($host, $extra{'name'}, $extra{'id'});
		}
		else {
			$author = render_author_link_as_html($host, "", 0);
		}

		my $sum = "";
		if (($summary ne "") && ($summary ne "*")) {
			$summary = quote_html($summary);
			$sum     = "<strong>[$summary]</strong> ";
		}

		$sum = "(no summary, tch tch tch)" unless defined $sum and length $sum;

		my $edit = "";
		$edit = "<em>(edit)</em> " if ($isEdit);

		my $count = "";
		if (!$all and $pagecount{$pagename} > 1) {
			$count = "($pagecount{$pagename} ";
			if (get_request_param("rcchangehist", 1)) {
				$count .= render_history_link_as_html($pagename, "changes");
			}
			else {
				$count .= "changes";
			}

			$count .= ") ";
		}

		my $link = "";
		if ($UseDiff && get_request_param("diffrclink", 1)) {
			$link .= render_diff_link_as_html(4, $pagename, "(diff)", "") . "  ";
		}

		$link .= render_unnamed_page_link_as_html($pagename);

		$html .= "<li>$link ";

		# Later do new-RC looping here.
		$html .= render_time_as_text($ts) . " $count$edit by $author<br>$sum";
	}

	$html .= "</UL>\n" if ($inlist);
	return $html;
}

sub render_history_line_as_html {
	my ($id, $section, $canEdit, $isCurrent) = @_;

	my %sect    = split(/$FS2/o, $section, -1);
	my %revtext = split(/$FS3/o, $sect{'data'});
	my $rev     = $sect{'revision'};
	my $summary = $revtext{'summary'};

	my $host;
	if ((defined($sect{'host'})) && ($sect{'host'} ne "")) {
		$host = $sect{'host'};
	}
	else {
		$host = $sect{'ip'};
		$host =~ s/\d+$/xxx/;    # Be somewhat anonymous (if no host)
	}

	my $user     = $sect{'username'};
	my $uid      = $sect{'id'};
	my $ts       = $sect{'ts'};
	my $minor    = $revtext{'minor'} ? "<i>(edit)</i> " : "";
	my $expirets = $^T - ($KeepDays * 24 * 60 * 60);

	my $html = "Revision $rev: ";
	if ($isCurrent) {
		$html .= render_named_page_link_as_html($id, 'View') . " ";

		if ($canEdit) {
			$html .= render_edit_link_as_html($id, 'Edit') . " ";
		}

		if ($UseDiff) {
			$html .= "Diff ";
		}
	}
	else {
		$html .= render_old_page_link_as_html('browse', $id, $rev, 'View') . " ";

		if ($canEdit) {
			$html .= render_old_page_link_as_html('edit', $id, $rev, 'Edit') . " ";
		}

		if ($UseDiff) {
			$html .= render_diff_link_with_revision_as_html(1, $id, $rev, 'Diff') . " ";
		}
	}

	$html .= ". . " . $minor . render_date_time_as_text($ts) . " ";
	$html .= "by " . render_author_link_as_html($host, $user, $uid) . " ";

	if (defined($summary) && ($summary ne "") && ($summary ne "*")) {
		$summary = quote_html($summary);    # Thanks Sunir! :-)
		$html .= "<b>[$summary]</b> ";
	}

	$html .= "<br>\n";

	return $html;
}

sub render_script_link_as_html {
	my ($action, $text) = @_;
	return qq(<a href="$ScriptName?$action" rel="nofollow">$text</a>);
}

sub render_unnamed_page_link_as_html {
	my ($id) = @_;
	return render_named_page_link_as_html($id, $id);
}

sub render_named_page_link_as_html {
	my ($id, $name) = @_;

	$id =~ s!^/!$MainPage/!;

	if ($FreeLinks) {
		$id =~ s/ /_/g;
		$id = ucfirst($id);
		$name =~ s/_/ /g;
	}

	return render_script_link_as_html($id, $name);
}

sub render_edit_link_as_html {
	my ($id, $name) = @_;

	if ($FreeLinks) {
		$id =~ s/ /_/g;
		$id = ucfirst($id);
		$name =~ s/_/ /g;
	}

	return render_script_link_as_html("action=edit&id=$id", $name);
}

sub render_old_page_link_as_html {
	my ($kind, $id, $revision, $name) = @_;

	if ($FreeLinks) {
		$id =~ s/ /_/g;
		$id = ucfirst($id);
		$name =~ s/_/ /g;
	}

	return render_script_link_as_html("action=$kind&id=$id&revision=$revision", $name);
}

sub render_page_or_edit_link_as_html {
	my ($id, $name) = @_;

	if ($name eq "") {
		$name = $id;
		if ($FreeLinks) {
			$name =~ s/_/ /g;
		}
	}

	$id =~ s!^/!$MainPage/!;

	if ($FreeLinks) {
		$id =~ s/ /_/g;
		$id = ucfirst($id);
	}

	my $exists = 0;

	if ($UseIndex) {
		unless ($IndexInit) {
			my @temp = get_all_pages_for_entire_site();    # Also initializes hash
		}
		$exists = 1 if ($IndexHash{$id});
	}
	elsif (-f get_filename_for_page_id($id)) {    # Page file exists
		$exists = 1;
	}

	if ($exists) {
		return render_named_page_link_as_html($id, $name);
	}

	if ($FreeLinks) {
		if ($name =~ m!\s!) {           # Not a single word
			$name = "[$name]";            # Add brackets so boundaries are obvious
		}
	}

	return $name . render_edit_link_as_html($id, "?");
}

sub render_page_or_edit_link_as_stored_html {
	my ($page, $name) = @_;

	if ($FreeLinks) {
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

	if ($FreeLinks) {
		$name =~ s/_/ /g;               # Display with spaces
		$id   =~ s/_/+/g;               # Search for url-escaped spaces
	}

	return render_script_link_as_html("search=$id", $name);
}

sub render_prefs_link_as_html {
	return render_script_link_as_html("action=editprefs", "Signup/Preferences");
}

sub render_login_link_as_html {
	return render_script_link_as_html("action=login", "Login");
}

sub render_random_link_as_html {
	return render_script_link_as_html("action=random", "Random Page");
}

sub render_diff_link_as_html {
	my ($diff, $id, $text, $rev) = @_;

	$rev = "&revision=$rev" if ($rev ne "");
	$diff = get_request_param("defaultdiff", 1) if ($diff == 4);

	return render_script_link_as_html("action=browse&diff=$diff&id=$id$rev", $text);
}

sub render_diff_link_with_revision_as_html {
	my ($diff, $id, $rev, $text) = @_;

	$rev = "&diffrevision=$rev" if ($rev ne "");
	$diff = get_request_param("defaultdiff", 1) if ($diff == 4);

	return render_script_link_as_html("action=browse&diff=$diff&id=$id$rev", $text);
}

sub render_script_link_with_title_as_html {
	my ($action, $text, $title) = @_;
	$action =~ s/ /_/g if $FreeLinks;
	return qq(<a href="$ScriptName?$action" title="$title" rel="nofollow">$text</a>);
}

sub render_author_link_as_html {
	my ($host, $userName, $uid) = @_;

	my $userNameShow = $userName;

	if ($FreeLinks) {
		$userName     =~ s/ /_/g;
		$userNameShow =~ s/_/ /g;
	}

	if (is_valid_page_id($userName) ne "") {    # Invalid under current rules
		$userName = "";                   # Just pretend it isn't there.
	}

	# Later have user preference for link titles and/or host text?
	my $html;
	if (($uid > 0) && ($userName ne "")) {
		$html = render_script_link_with_title_as_html($userName, $userNameShow, "ID $uid from $host");
	}
	else {
		$html = $host;
	}

	return $html;
}

sub render_history_link_as_html {
	my ($id, $text) = @_;
	$id =~ s/ /_/g if $FreeLinks;
	return render_script_link_as_html("action=history&id=$id", $text);
}

sub render_list_of_page_names_as_html {
	my $html = "<h2>" . ($#_ + 1) . " pages found:</h2>\n";
	foreach my $pagename (@_) {
		$html .= ".... " if $pagename =~ m!/!;
		$html .= render_unnamed_page_link_as_html($pagename) . "<br>\n";
	}
	return $html;
}

sub render_hidden_input_as_html {
	my ($name, $value) = @_;

	$q->param($name, $value);

	return $q->hidden($name);
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

sub render_page_header_as_html {
	my ($id, $title, $oldId, $revision) = @_;
	my $header    = "";
	my $LogoImage = "";
	my $result;
	my $cookie;

	my %data;

	if (defined($SetCookie{'id'})) {
		$cookie = (
			"$CookieName=" . "rev&" .
			$SetCookie{'rev'} . "&id&" .
			$SetCookie{'id'} .
			"&randkey&" .
			$SetCookie{'randkey'}
		);

		$cookie .= ";expires=Fri, 08-Sep-2010 19:48:23 GMT";
		$result = $q->header(-cookie => $cookie);
	}
	else {
		$result = $q->header();
	}

	$data{GlobalCSS} = $GlobalCSS if $GlobalCSS;

	# Display as spaces.
	$title =~ s/_/ /g if $FreeLinks;

	if (lc $title eq lc $SiteName) {
		$data{doctitle} = $SiteName;
	}
	elsif ($ReverseTitle) {
		$data{doctitle} = "$title - $SiteName";
	}
	else {
		$title =~ s/^\s*($SiteName)?\s*/$SiteName: /;
		$title =~ s!/! - !g;
		$data{doctitle} = $title;
	}

	if ($UserCSS && $UserData{'css'}) {
		$data{CSS} = $UserData{'css'};
	}

	if ($oldId ne "") {
		$data{redirect} .= (
			q{<h3>} .
			("(redirected from " . render_edit_link_as_html($oldId, $oldId) . ")") .
			q{</h3>}
		);
	}

	if ($LogoUrl ne "") {
		$LogoImage = "img src=\"$LogoUrl\" alt=\"[Home]\" border=0";

		unless ($LogoLeft) {
			$LogoImage .= " align=\"right\"";
		}

		$header = render_script_link_as_html($HomePage, "<$LogoImage>");
	}

	if ($EnableInlineTitle) {
		if ($EnableSelfLinks && $id ne "") {
			$data{header} .= q{<h1>} . ($header . render_search_link_as_html($id)) . q{</h1>};
		}
		else {
			$data{header} .= q{<h1>} . ($header . $title) . q{</h1>};
		}
	}

	if ($WantTopLinkBar && get_request_param("toplinkbar", 1)) {

		# Later consider smaller size?
		$data{header} .= render_goto_bar_as_html($id) . "<hr>";
	}

	print $result if $result;

	if ($revision) {
		$data{meta_robot} = "NOINDEX,NOFOLLOW";
	}
	else {
		$data{meta_robot} = "INDEX,FOLLOW";
	}

	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/header.html"
	);

	$result = $template->fill_in(HASH => \%data);

	return $result;
}

sub render_complex_page_footer_as_html {
	my ($id, $rev) = @_;

	my %data = (
		footer => render_goto_bar_as_html($id),
	);

	if (user_can_edit($id, 0)) {
		my $userName = get_request_param("username", "");
		if ($userName eq "") {
			$data{footer} .= "Must login to edit";
		}
		else {
			if ($rev ne "") {
				$data{footer} .= (
					render_old_page_link_as_html(
						'edit', $id, $rev, "Edit revision $rev of this page"
					)
				);
			}
			else {
				$data{footer} .= render_edit_link_as_html($id, "Edit text of this page");
			}
		}

		$data{footer} .= " | " . render_history_link_as_html($id, "View other revisions");
	}
	else {
		$data{footer} .= "This page is read-only";
		$data{footer} .= " | " . render_history_link_as_html($id, "View other revisions");
	}

	if ($rev ne "") {
		$data{footer} .= " | " . render_named_page_link_as_html($id, "View current revision");
	}

	if ($Section{'revision'} > 0) {
		$data{footer} .= "<br>";
		if ($rev eq "") {    # Only for most current rev
			$data{footer} .= "Last edited ";
		}
		else {
			$data{footer} .= "Edited ";
		}

		$data{footer} .= render_date_time_as_text($Section{ts});
	}

	if ($UseDiff) {
		$data{footer} .= " " . render_diff_link_as_html(4, $id, "(diff)", $rev);
	}

	#$data{footer} .= "<br>" . render_search_form_as_html();
	if ($DataDir =~ m!/tmp/!) {
		$data{footer} .= (
			"<br><b>Warning:</b> Database is stored in temporary" .
			" directory $DataDir<br>"
		);
	}

	$data{footer} .= (
		" - Or find pages that link to <b>" . render_search_link_as_html($id) . "</b>"
	);

	if (length $Footer) {
		$data{footer} .= $Footer;
	}

	#$data{footer} .= $q->endform;

	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/footer.html"
	);

	my $result = $template->fill_in(HASH => \%data);

	return $result;
}

sub render_simple_page_footer_as_html {
	my $footer   = shift;
	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/footer.html"
	);
	my $result = $template->fill_in(HASH => {footer => $footer});

	return $result;
}

sub render_common_footer_as_html {
	my %data;

	$data{footer} = (
		"<hr>" .
		render_form_start_as_html() .
		render_goto_bar_as_html("") .
		render_search_form_as_html() .
		$q->endform
	);

	my $template = Text::Template->new(
		TYPE       => 'FILE',
		DELIMITERS => ['<%', '%>'],
		SOURCE     => "$Templates/footer.html"
	);

	my $result = $template->fill_in(HASH => \%data);

	return $result;
}

sub render_form_start_as_html {
	return $q->startform(
		"POST", "$ScriptName", "application/x-www-form-urlencoded"
	);
}

sub render_goto_bar_as_html {
	my ($id) = @_;

	my $bartext = render_unnamed_page_link_as_html($HomePage);

	if ($id =~ m!/!) {
		my $main = $id;
		$main =~ s!/.*!!;    # Only the main page name (remove subpage)
		$bartext .= " | " . render_unnamed_page_link_as_html($main);
	}

	$bartext .= " | " . render_unnamed_page_link_as_html("$RCName");

	my $userName = get_request_param("username", "");
	$bartext .= " | " . render_prefs_link_as_html();
	$bartext .= " | " . render_login_link_as_html();

	if ($userName ne "") {
		$bartext .= " (You are " . render_unnamed_page_link_as_html($userName) . ") ";
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

sub render_search_form_as_html {
	return unless $WantSearch;

	return(
		"Search: " .
		$q->textfield(-name => 'search', -size => 20) .
		render_hidden_input_as_html("dosearch", 1)
	);
}

sub render_projects_as_html {
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

sub render_perl_as_stored_html {
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
		open(WHEE, ">/home/troc/tmp/messy");
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

	$html = (
		"<table border='1' cellspacing='0' width='100%'><tr><td nowrap>" .
		$html .
		"</td></tr></table>"
	);

	DUMP_TIDY and do {
		open(WHEE, ">/home/troc/tmp/tidied");
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

sub render_outline_as_html {
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

sub render_components_as_html {
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

sub render_pre_as_stored_html {
	my $html = shift;
	my $pre = (
		"<table border='1' cellspacing='0'><tr><td nowrap><pre>" .
		$html .
		"</pre></td></tr></table>"
	);

	return store_raw_html($pre);
}

sub render_code_as_stored_html {
	my $html = shift;
	my $code = (
		"<table border='1' cellspacing='0'><tr><td nowrap><code>" .
		$html .
		"</code></td></tr></table>"
	);

	return store_raw_html($code);
}

sub render_rfc_link_as_stored_html {
	my ($num) = @_;
	return store_raw_html("RFC <a href=\"http://www.faqs.org/rfcs/rfc${num}.html\">$num</a>");
}

sub render_isbn_link_as_stored_html {
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
	$html .= " ($second, $third)" if $ExtraISBNLinks;
	$html .= " " if (substr($rawnum, -1, 1) eq ' ');    # preserve ISBN space

	return store_raw_html($html);
}

sub render_inter_page_link_as_html_and_punct {
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

sub render_bracketed_inter_page_link_as_stored_html {
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

sub render_url_link_as_html_and_punct {
	my ($rawname, $useImage) = @_;

	my ($name, $punct) = split_url_from_trailing_punctuation($rawname);

	if ($NetworkFile && $name =~ m!^file:!) {

		# Only do remote file:// links. No file:///c|/windows.
		if ($name =~ m!^file://[^/]!) {
			return ("<a href=\"$name\">$name</a>", $punct);
		}

		return $rawname;
	}

	# Restricted image URLs so that mailto:foo@bar.gif is not an image
	if ($useImage && ($name =~ /^(http:|https:|ftp:).+\.$ImageExtensions$/)) {
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

sub render_wiki_heading_as_html {
	my ($pre, $depth, $text) = @_;

	$depth = length($depth);
	$depth = 6 if ($depth > 6);

	return $pre . "<H$depth>$text</H$depth>\n";
}

sub render_href_as_stored_html {
	my ($anchor, $text) = @_;
	return store_raw_html("<a $anchor>$text</a>");
}

sub render_and_store_inter_page_link {
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
	$SaveUrl{$SaveUrlIndex} = $html;
	return $FS . $SaveUrlIndex++ . $FS;
}

sub render_url_as_stored_html {
	my ($name, $useImage) = @_;

	my ($link, $extra) = render_url_link_as_html_and_punct($name, $useImage);

	# Next line ensures no empty links are stored
	$link  = "" unless defined $link;
	$extra = "" unless defined $extra;
	$link = store_raw_html($link) if $link ne "";
	return $link . $extra;
}

sub render_bracketed_url_as_stored_html {
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
	if ($SaveNumUrl{$id} > 0) {
		return $SaveNumUrl{$id};
	}

	$SaveNumUrlIndex++;    # Start with 1
	$SaveNumUrl{$id} = $SaveNumUrlIndex;

	return $SaveNumUrlIndex;
}

sub render_bracketed_link_as_stored_html {
	my ($name, $text) = @_;

	return store_raw_html(render_named_page_link_as_html($name, "[$text]"));
}

sub render_sub_wiki_link_as_stored_html {
	my ($link, $old, $new) = @_;

	my $newBracket = 0;
	if ($link eq $old) {
		$link = $new;
		unless ($new =~ /^$LinkPattern$/o) {
			$link = "[[$link]]";
		}
	}

	return store_raw_html($link);
}

sub render_sub_free_link_as_stored_html {
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

sub render_link_list_as_html {

	my %pgExists = ();
	foreach my $page (get_all_pages_for_entire_site()) {
		$pgExists{$page} = 1;
	}

	my $html = "";

	my $names    = get_request_param("names",    1);
	my $editlink = get_request_param("editlink", 0);
	foreach my $pagelines (@_) {
		my @links;

		my $link;
		foreach my $page (split(' ', $pagelines)) {
			if ($page =~ /\:/) {    # URL or InterWiki form
				if ($page =~ /$UrlPattern/) {
					($link, my $extra) = render_url_link_as_html_and_punct($page);
				}
				else {
					($link, my $extra) = render_inter_page_link_as_html_and_punct($page);
				}
			}
			else {
				if ($pgExists{$page}) {
					$link = render_unnamed_page_link_as_html($page);
				}
				else {
					$link = $page;
					if ($editlink) {
						$link .= render_edit_link_as_html($page, "?");
					}
				}
			}

			push(@links, $link);
		}

		if ($names) {
			$html .= "<dl><dt>" . shift(@links) . " links to:";
			if (@links > 1) {
				foreach my $lnk (@links) {
					$html .= "<dd>$lnk";
				}
			}
			else {
				$html .= " " . join("; ", @links);
			}

			$html .= "</dl>";
		}
		else {
			shift(@links);
			$html .= join(" ", @links) . "<br />";
		}
	}

	return $html;
}

### MAIN: Handle the wiki request.
# It is called at the end of the program.
# This allows execution of various initializers throughout the code.
# It calls the dispatchers, which call the actions, which in turn call
# various helpers and renderers.

sub main_wiki_request {

	# Call the one-time initialization here.
	if (!$DataDir || $LoadEveryTime) {
		init_wiki();
	}

	unless (try_html_cache()) {
		init_request() or return;
		unless (dispatch_browse_request()) {
			dispatch_change_request();
		}
	}
}

main_wiki_request();
exit;
