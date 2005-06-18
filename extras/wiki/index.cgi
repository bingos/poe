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
# Email and ThinLine options by Jim Mahoney <mahoney@marlboro.edu>
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

use lib qw(/home/troc/lib/local/share/perl);

use CGI::Carp qw(fatalsToBrowser);
use Text::Template;

$| = 1;    # Do not buffer output
undef $/;  # Read complete files
use strict;

# == Configuration ============================================================

# Development flag.  Dump the before and after versions of source code
# as it passes through Perl::Tidy.

sub DUMP_TIDY () { 0 }

# Configuration/constant variables.  Must be C<use vars> because
# they're overridden with a do() function.

use vars qw( @RcDays @HtmlPairs @HtmlSingle $TempDir $LockDir
     $DataDir $HtmlDir $UserDir $KeepDir $PageDir
     $InterFile $RcFile $RcOldFile $IndexFile $FullUrl
     $SiteName $HomePage $LogoUrl $RcDefault $IndentLimit
     $RecentTop $EditAllowed $UseDiff $UseSubpage
     $UseCache $RawHtml $SimpleLinks $NonEnglish
     $LogoLeft $KeepDays $HtmlTags $HtmlLinks $UseDiffLog
     $KeepMajor $KeepAuthor $UseEmailNotify $SendMail
     $NotifyDefault $EmailFrom $ScriptTZ $BracketText
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

$VERSION = (qw($Revision$))[1]; # CVS Version. NO TOUCHIE

sub InitConfig {

  # Main wiki directory.
  if (defined($ENV{SERVER_NAME}) and $ENV{SERVER_NAME} eq "poe.dynodns.net") {
    $DataDir = "/home/troc/public_html/poe/data";
  }
  elsif (defined $ENV{DOCUMENT_ROOT}) {
    $DataDir = $ENV{DOCUMENT_ROOT};
    $DataDir .= '/' unless substr($DataDir,-1,1) eq '/';
    $DataDir .= 'data';
  }

  $UseConfig   = 1;       # 1 = use config file,    0 = do not look for config

  # Default configuration (used if UseConfig is 0)
  $GlobalCSS   = "";              # path to global css style sheet
  $WantSearch  = 1;               # 1 = Show search box; 0 = Dont show search box;
  $WantTopLinkBar = 1;            # 1 = Make top link bar available; 0 = Top link bar is never shown
  $CookieName  = "Wiki";          # Name for this wiki (for multi-wiki sites)
  $SiteName    = "Wiki";          # Name of site (used for titles)
  $HomePage    = "HomePage";      # Home page (change space to _)
  $RCName      = "RecentChanges"; # Name of changes page (change space to _)
  $LogoUrl     = "";     # URL for site logo ("" for no logo)
  $ENV{PATH}   = "/usr/bin/";     # Path used to find "diff"
  $ScriptTZ    = "";              # Local time zone ("" means do not print)
  $RcDefault   = 30;              # Default number of RecentChanges days
  @RcDays      = qw(1 3 7 30 90); # Days for links on RecentChanges
  $KeepDays    = 14;              # Days to keep old revisions
  $SiteBase    = "";              # Full URL for <BASE> header
  $FullUrl     = "";              # Set if the auto-detected URL is wrong
  $RedirType   = 1;               # 1 = CGI.pm, 2 = script, 3 = no redirect
  $AdminPass   = "";              # Set to non-blank to enable password(s)
  $EditPass    = "";              # Like AdminPass, but for editing only

  # Major options:
  $UseSubpage  = 1;       # 1 = use subpages,       0 = do not use subpages
  $UseCache    = 0;       # 1 = cache HTML pages,   0 = generate every page
  $EditAllowed = 1;       # 1 = editing allowed,    0 = read-only
  $RawHtml     = 0;       # 1 = allow <HTML> tag,   0 = no raw HTML in pages
  $HtmlTags    = 0;       # 1 = "unsafe" HTML tags, 0 = only minimal tags
  $UseDiff     = 1;       # 1 = use diff features,  0 = do not use diff
  $FreeLinks   = 1;       # 1 = use [[word]] links, 0 = LinkPattern only
  $WikiLinks   = 1;       # 1 = use LinkPattern,    0 = use [[word]] only
  $AdminDelete = 1;       # 1 = Admin only page,    0 = Editor can delete pages
  $UseScriptName = 0;     # 1 = use SCRIPT_NAME     0 = don't (supports http://wiki/?Link)

  # Minor options:
  $LogoLeft    = 0;       # 1 = logo on left,       0 = logo on right
  $RecentTop   = 1;       # 1 = recent on top,      0 = recent on bottom
  $UseDiffLog  = 1;       # 1 = save diffs to log,  0 = do not save diffs
  $KeepMajor   = 1;       # 1 = keep major rev,     0 = expire all revisions
  $KeepAuthor  = 1;       # 1 = keep author rev,    0 = expire all revisions
  $ShowEdits   = 0;       # 1 = show minor edits,   0 = hide edits by default
  $HtmlLinks   = 0;       # 1 = allow A HREF links, 0 = no raw HTML links
  $SimpleLinks = 0;       # 1 = only letters,       0 = allow _ and numbers
  $NonEnglish  = 0;       # 1 = extra link chars,   0 = only A-Za-z chars
  $ThinLine    = 0;       # 1 = fancy <hr> tags,    0 = classic wiki <hr>
  $BracketText = 1;       # 1 = allow [URL text],   0 = no link descriptions
  $UseAmPm     = 1;       # 1 = use am/pm in times, 0 = use 24-hour times
  $UseIndex    = 0;       # 1 = use index file,     0 = slow/reliable method
  $UseHeadings = 1;       # 1 = allow = h1 text =,  0 = no header formatting
  $NetworkFile = 1;       # 1 = allow remote file:, 0 = no file:// links
  $BracketWiki = 0;       # 1 = [WikiLnk txt] link, 0 = no local descriptions

  $UseEmailNotify = 0;       # 1 = allow email notification,     0 = don't
  $NotifyDefault  = 0;       # Default for email notify checkbox on Edit page.
  $ShowNotify     = 1;       # 1 = show notify option            0 = don't
  $EmailFrom      = "Wiki";  # Text for "From: " field of email notes.
                             # (But Reply-to; is set to same as To: anyway.)
  $SendMail       = "/usr/sbin/sendmail"; # Full path to sendmail executable
  $ExtraISBNLinks = 1;       # 1 = display extra ISBN links.     0 = don't
  $AllowCharRefs  = 1;       # 1 = allow character references    0 = don't
  $UserCSS        = 1;       # 1 = allow per-user CSS prefs      0 = don't
  $ReverseTitle   = 0;       # 1 = page title before SiteName    0 = after

  $EnableSelfLinks = 1;      # 1 = create ?search heading links  0 = don't
  $EnableInlineTitle = 1;    # 1 = use title in page             0 = don't

  $Footer         = "";      # HTML that goes at the end of the footer.
  $ForceLcaseFiles = 0;      # 1 = filename case always lower    0 = not
  $LoadEveryTime  = 0;       # 1 = force config load every run   0 = not

  # HTML tag lists, enabled if $HtmlTags is set.
  # Scripting is currently possible with these tags,
  # so they are *not* particularly "safe".
  # Tags that must be in <tag> ... </tag> pairs:
  @HtmlPairs =
    qw( b i u font big small sub sup h1 h2 h3 h4 h5 h6 cite code span
        perl em s strike strong tt var div center blockquote ol ul dl
        table caption boxes tests
      );
  # Single tags (that do not require a closing /tag)
  @HtmlSingle = qw(br p hr li dt dd tr td th);
  push @HtmlPairs, @HtmlSingle;            # All singles can also be pairs

  # == You should not have to change anything below this line. ================

  $IndentLimit = 20;                  # Maximum depth of nested lists
  $PageDir     = "$DataDir/page";     # Stores page data
  $HtmlDir     = "$DataDir/html";     # Stores HTML versions
  $UserDir     = "$DataDir/user";     # Stores user data
  $KeepDir     = "$DataDir/keep";     # Stores kept (old) page data
  $TempDir     = "$DataDir/temp";     # Temporary files and locks
  $LockDir     = "$TempDir/lock";     # DB is locked if this exists
  $InterFile   = "$DataDir/intermap"; # Interwiki site->url map
  $RcFile      = "$DataDir/rclog";    # New RecentChanges logfile
  $RcOldFile   = "$DataDir/oldrclog"; # Old RecentChanges logfile
  $IndexFile   = "$DataDir/pageidx";  # List of all pages
  $Templates   = "$DataDir/templates/";
}

sub CheckConfig {
  die "no document root; set \$DataDir manually"
    unless defined $DataDir;
  die "document root $DataDir doesn't exist"
    unless -e $DataDir;
  unless ( -d $DataDir || -l $DataDir ) {
    die "document root $DataDir isn't a directory"
  }
}

# Stuff that we should only be doing once per startup.
sub InitWikiStuff {
  &InitConfig();
  if ($UseConfig) {
    if (-f "$DataDir/config") {
      if (open(CONFIG, "$DataDir/config")) {
        eval scalar <CONFIG>;
        die "eval $DataDir/config failed: $@" if $@;
        close(CONFIG);
      } else {
        die "couldn't open config: $!";
      }
    } else {
      die "couldn't find $DataDir/config: $!";
    }

    # A safe place for our changes.
    if (-f "$DataDir/config.custom") {
      if (open(CUSTOM, "$DataDir/config.custom")) {
        eval scalar <CUSTOM>;
        die "eval $DataDir/config.custom failed: $@" if $@;
        close(CUSTOM);
      } else {
        warn "couldn't open $DataDir/config.custom: $!";
      }
    }
  }
  &CheckConfig();
  &InitLinkPatterns();
}

# Return a lowercase version of a file name.

sub fold_to_lowercase {
  my $file = shift;

  return $file if -e $file;
  return $file unless $ForceLcaseFiles;

  # Lowercase subdirectories and everything.
  if ($file =~ s/\/([^\/\.]|other)\/(.*?)\.([^\/\.]+)$//) {
    $file .= "/$1/" . lc($2) . ".$3";
  }

  # No subdirectories?  Lowercase just the base name.
  elsif ($file =~ s/\/([^\/\.]+)\.([^\/\.]+)$//) {
    $file .= "/" . lc($1) . ".$2";
  }

  return $file;
}

# The "main" program, called at the end of this script file.
sub DoWikiRequest {
  # call the one-time init here.
  if (!$DataDir || $LoadEveryTime) {
    &InitWikiStuff();
  }
  if (!&DoCacheBrowse()) {
    eval $BrowseCode;
    &InitRequest() or return;
    if (!&DoBrowseRequest()) {
      eval $OtherCode;
      &DoOtherRequest();
    }
  }
}

# == Common and cache-browsing code ===========================================

sub InitLinkPatterns {
  my ($UpperLetter, $LowerLetter, $AnyLetter, $LpA, $LpB, $QDelim);

  # Field separators are used in the URL-style patterns below.
  $FS  = "\xb3";      # The FS character is a superscript "3"
  $FS1 = $FS . "1";   # The FS values are used to separate fields
  $FS2 = $FS . "2";   # in stored hashtables and other data structures.
  $FS3 = $FS . "3";   # The FS character is not allowed in user data.

  $UpperLetter = "[A-Z";
  $LowerLetter = "[a-z";
  $AnyLetter   = "[A-Za-z";
  if ($NonEnglish) {
    $UpperLetter .= "\xc0-\xde";
    $LowerLetter .= "\xdf-\xff";
    $AnyLetter   .= "\xc0-\xff";
  }
  if (!$SimpleLinks) {
    $AnyLetter .= "_:0-9";
  }
  $UpperLetter .= "]"; $LowerLetter .= "]"; $AnyLetter .= "]";

  # Main link pattern: lowercase between uppercase, then anything
  $LpA = $UpperLetter . "+" . $LowerLetter . "+" . $UpperLetter
         . $AnyLetter . "*";
  # Optional subpage link pattern: uppercase, lowercase, then anything
  $LpB = $UpperLetter . "+" . $LowerLetter . "+" . $AnyLetter . "*";

  if ($UseSubpage) {
    # Loose pattern: If subpage is used, subpage may be simple name
    $LinkPattern = "((?:(?:$LpA)?\\/$LpB)|$LpA)";
    # Strict pattern: both sides must be the main LinkPattern
    # $LinkPattern = "((?:(?:$LpA)?\\/)?$LpA)";
  } else {
    $LinkPattern = "($LpA)";
  }
  $QDelim = '(?:"")?';     # Optional quote delimiter (not in output)
  $LinkPattern .= $QDelim;

  # Inter-site convention: sites must start with uppercase letter
  # (Uppercase letter avoids confusion with URLs)
  $InterSitePattern = $UpperLetter . $AnyLetter . "+";
  $InterLinkPattern = "((?:$InterSitePattern:[^\\]\\s\"<>$FS]+)$QDelim)";

  if ($FreeLinks) {
    # Note: the - character must be first in $AnyLetter definition
    if ($NonEnglish) {
      $AnyLetter = "[-,.:' _0-9A-Za-z\xc0-\xff]";
    } else {
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

  $UrlProtocols = "http|https|ftp|afs|news|nntp|mid|cid|mailto|wais|"
                  . "prospero|telnet|gopher";
  $UrlProtocols .= '|file'  if $NetworkFile;
  $UrlPattern = "((?:(?:$UrlProtocols):[^\\]\\s\"<>$FS]+)$QDelim)";
  $ImageExtensions = "(gif|jpg|png|bmp|jpeg)";
  $RFCPattern = "RFC\\s?(\\d+)";
  $ISBNPattern = "ISBN:?([0-9- xX]{10,})";
}

# Simple HTML cache
sub DoCacheBrowse {
  my ($query, $idFile, $text);

  return 0  if (!$UseCache);
  $query = $ENV{'QUERY_STRING'};
  if (($query eq "") && ($ENV{'REQUEST_METHOD'} eq "GET")) {
    $query = $HomePage;  # Allow caching of home page.
  }
  if (!($query =~ /^$LinkPattern$/o)) {
    if (!($FreeLinks && ($query =~ /^$FreeLinkPattern/o))) {
      return 0;  # Only use cache for simple links
    }
  }
  $idFile = &GetHtmlCacheFile($query);
  if (-f $idFile) {
    open(INFILE, "<$idFile") or return 0;
    $text = <INFILE>;
    close INFILE;
    print $text;
    return 1;
  }
  return 0;
}

sub GetHtmlCacheFile {
  my ($id) = @_;
  return fold_to_lowercase($HtmlDir . "/" . &GetPageDirectory($id) . "/$id.htm");
}

sub GetPageDirectory {
  my ($id) = @_;

  if ($id =~ /^([a-zA-Z])/) {
    return uc($1);
  }
  return "other";
}

# == Normal page-browsing and RecentChanges code ==============================

$BrowseCode = ""; # Comment next line to always compile (slower)
#$BrowseCode = <<'#END_OF_BROWSE_CODE';
use CGI;

sub InitRequest {
  my @ScriptPath = split('/', "$ENV{SCRIPT_NAME}");

  $CGI::POST_MAX=1024 * 200;  # max 200K posts
  $CGI::DISABLE_UPLOADS = 1;  # no uploads
  $q = new CGI;

  # TODO: AUGH! What were they THINKING?! This needs to change. Somehow.
  $^T = time;                      # Reset in case script is persistent
  # do we want to grab the script name and use it, or ignore it so that
  # things like http://domain/?Wiki_Link work?
  if ($UseScriptName) {
    $ScriptName = pop(@ScriptPath);  # Name used in links
  } else {
    $ScriptName = '';
  }

  $IndexInit = 0;
  $InterSiteInit = 0;
  %InterSite = ();
  $MainPage = ".";       # For subpages only, the name of the top-level page
  $OpenPageName = "";    # Currently open page
  &CreateDir($DataDir);  # Create directory if it doesn't exist
  if (!-d $DataDir) {
    &ReportError("Could not create $DataDir: $!");
    return 0;
  }
  &InitCookie();         # Reads in user data
  return 1;
}

sub GetCookie {
  # we need a cookie name here
  return undef unless defined $_[0];
  # return the cookie
  return $q->cookie($_[0]);
}

sub InitCookie {
  %SetCookie = ();
  $TimeZoneOffset = 0;
  %UserCookie = &GetCookie($CookieName);
  $UserID = $UserCookie{'id'};
  $UserID =~ s/\D//g;  # Numeric only
  if ($UserID < 1) {
    $UserID = 111;
  } else {
    &LoadUserData($UserID);
  }
  if ($UserID > 199) {
    if (($UserData{'id'}       != $UserCookie{'id'})      ||
        ($UserData{'randkey'}  != $UserCookie{'randkey'})) {
      $UserID = 113;
      %UserData = ();   # Invalid.  Later consider warning message.
    }
  }
  if ($UserData{'tzoffset'} != 0) {
    $TimeZoneOffset = $UserData{'tzoffset'} * (60 * 60);
  }
}

sub GotParams {
  return $q->param ? 1 : undef;
}

sub DoBrowseRequest {
  my ($id, $action, $text);

  if (!&GotParams()) {             # No parameters
    &BrowsePage($HomePage);
    return 1;
  }
  $id = &GetParam("keywords", "");
  if ($id) {                    # Just script?PageName
    &BrowsePage($id) if &ValidIdOrDie($id);
    return 1;
  }
  $action = lc(&GetParam("action", ""));
  $id = &GetParam("id", "");
  if ($action eq "browse") {
    &BrowsePage($id)  if &ValidIdOrDie($id);
    return 1;
  } elsif ($action eq "rc") {
    &BrowsePage("$RCName");
    return 1;
  } elsif ($action eq "random") {
    &DoRandom();
    return 1;
  } elsif ($action eq "history") {
    &DoHistory($id)   if &ValidIdOrDie($id);
    return 1;
  }
  return 0;  # Request not handled
}

sub BrowsePage {
  my ($id) = @_;
  my ($fullHtml, $oldId, $allDiff, $showDiff, $openKept);
  my ($revision, $goodRevision, $diffRevision, $newText);

  &OpenPage($id);
  &OpenDefaultText();
  $newText = $Text{'text'};     # For differences
  $openKept = 0;
  $revision = &GetParam("revision", "");
  $revision =~ s/\D//g;           # Remove non-numeric chars
  $goodRevision = $revision;      # Non-blank only if exists
  if ($revision ne "") {
    &OpenKeptRevisions('text_default');
    $openKept = 1;
    if (!defined($KeptRevisions{$revision})) {
      $goodRevision = "";
    } else {
      &OpenKeptRevision($revision);
    }
  }
  # Handle a single-level redirect
  $oldId = &GetParam("oldid", "");
  if (($oldId eq "") && (substr($Text{'text'}, 0, 10) eq "#REDIRECT ")) {
    $oldId = $id;
    if (($FreeLinks) && ($Text{'text'} =~ /\#REDIRECT\s+\[\[.+\]\]/)) {
      ($id) = ($Text{'text'} =~ /\#REDIRECT\s+\[\[(.+)\]\]/);
      $id =~ s/ /_/g;  # Convert from typed form to internal form
    } else {
      ($id) = ($Text{'text'} =~ /\#REDIRECT\s+(\S+)/);
    }
    if (&ValidId($id) eq "") {
      # Later consider revision in rebrowse?
      &ReBrowsePage($id, $oldId, 0);
      return;
    } else {  # Not a valid target, so continue as normal page
      $id = $oldId;
      $oldId = "";
    }
  }
  $MainPage = $id;
  $MainPage =~ s|/.*||;  # Only the main page name (remove subpage)

  # Need to know if this is a diff (also looking at older revision)
  # so we can stop search robots from indexing it.
  $allDiff  = &GetParam("alldiff", 0);
  if ($allDiff != 0) {
    $allDiff = &GetParam("defaultdiff", 1);
  }
  if (($id eq "$RCName") && &GetParam("norcdiff", 1)) {
    $allDiff = 0;  # Only show if specifically requested
  }

  my $header_revision = $revision;

  $showDiff = &GetParam("diff", $allDiff);
  if ($UseDiff && $showDiff) {
    $diffRevision = $goodRevision;
    $diffRevision = &GetParam("diffrevision", $diffRevision);
    # Later try to avoid the following keep-loading if possible?
    &OpenKeptRevisions('text_default')  if (!$openKept);
    $header_revision ||= 1;
  }

  $fullHtml = &GetHeader($id, &QuoteHtml($id), $oldId, $header_revision);

  if ($UseDiff && $showDiff) {
    $fullHtml .= &GetDiffHTML($showDiff, $id, $diffRevision, $newText);
  }

  if ($revision ne "") {
    # Later maybe add edit time?
    if ($goodRevision ne "") {
      $fullHtml .= "<b>Showing revision $revision</b><br>";
    } else {
      $fullHtml .= "<b>Revision $revision not available " .
                   "(showing current revision instead)</b><br>";
    }
  }

  $fullHtml .= &WikiToHTML($Text{'text'}) . "\n"; #  . "<hr>\n";
  if ($id eq "$RCName") {
    print $fullHtml;
    &DoRc();
    print &GetFooterText($id, $goodRevision);
    return;
  }
  $fullHtml .= &GetFooterText($id, $goodRevision);
  print $fullHtml;
  return  if ($showDiff || ($revision ne ""));  # Don't cache special version
  &UpdateHtmlCache($id, $fullHtml)  if $UseCache;
}

sub ReBrowsePage {
  my ($id, $oldId, $isEdit) = @_;

  if ($oldId ne "") {   # Target of #REDIRECT (loop breaking)
    print &GetRedirectPage("action=browse&id=$id&oldid=$oldId",
                           $id, $isEdit);
  } else {
    print &GetRedirectPage($id, $id, $isEdit);
  }
}

sub DoRc {
  my ($fileData, $rcline, $i, $daysago, $lastTs, $ts, $idOnly);
  my (@fullrc, $status, $oldFileData, $firstTs, $errorText);
  my $starttime = 0;
  my $showbar = 0;

  if (&GetParam("from", 0)) {
    $starttime = &GetParam("from", 0);
    print "<h2>Updates since ", &TimeToText($starttime), "</h2>\n";
  } else {
    $daysago = &GetParam("days", 0);
    $daysago = &GetParam("rcdays", 0)  if ($daysago == 0);
    if ($daysago) {
      $starttime = $^T - ((24*60*60)*$daysago);
      print "<h2>Updates in the last $daysago day",
            (($daysago != 1)?"s":""), "</h2>\n";
    }
  }
  if ($starttime == 0) {
    $starttime = $^T - ((24*60*60)*$RcDefault);
    print "<h2>Updates in the last $RcDefault days</h2>\n";
  }

  # Read rclog data (and oldrclog data if needed)
  ($status, $fileData) = &ReadFile($RcFile);
  $errorText = "";
  if (!$status) {
    # Save error text if needed.
    $errorText = "<p><strong>Could not open $RCName log file:"
                 . "</strong> $RcFile<p>Error was:\n<pre>$!</pre>\n"
                 . "<p>Note: This error is normal if no changes"
                 . "have been made.\n";
  }
  @fullrc = split(/\n/, $fileData);
  $firstTs = 0;
  if (@fullrc > 0) {  # Only false if no lines in file
    ($firstTs) = split(/$FS3/o, $fullrc[0]);
  }
  if (($firstTs == 0) || ($starttime <= $firstTs)) {
    ($status, $oldFileData) = &ReadFile($RcOldFile);
    if ($status) {
      @fullrc = split(/\n/, $oldFileData . $fileData);
    } else {
      if ($errorText ne "") {  # could not open either rclog file
        print $errorText,
              "<p><strong>Could not open old $RCName log file:"
                   . "</strong> $RcOldFile<p>Error was:\n<pre>$!</pre>\n";
        return;
      }
    }
  }
  $lastTs = 0;
  if (@fullrc > 0) {  # Only false if no lines in file
    ($lastTs) = split(/$FS3/o, $fullrc[$#fullrc]);
  }
  $lastTs++  if (($^T - $lastTs) > 5);  # Skip last unless very recent

  $idOnly = &GetParam("rcidonly", "");
  if ($idOnly ne "") {
    print "<b>(for " . &ScriptLink($idOnly, $idOnly)
          . " only)</b><br>";
  }
  foreach $i (@RcDays) {
    print " | "  if $showbar;
    $showbar = 1;
    print &ScriptLink("action=rc&days=$i", "$i day" . (($i != 1)?"s":""));
  }
  print "<br>" . &ScriptLink("action=rc&from=$lastTs",
                             "List new changes starting from"),
        " " . &TimeToText($lastTs), "<br>\n";

  # Later consider a binary search?
  $i = 0;
  while ($i < @fullrc) {  # Optimization: skip old entries quickly
    ($ts) = split(/$FS3/o, $fullrc[$i]);
    if ($ts >= $starttime) {
      $i -= 1000  if ($i > 0);
      last;
    }
    $i += 1000;
  }
  $i -= 1000  if (($i > 0) && ($i >= @fullrc));
  for (; $i < @fullrc ; $i++) {
    ($ts) = split(/$FS3/o, $fullrc[$i]);
    last if ($ts >= $starttime);
  }
  if ($i == @fullrc) {
    print "<br><strong>No updates since ", &TimeToText($starttime),
          "</strong><br>\n";
  } else {
    splice(@fullrc, 0, $i);  # Remove items before index $i
    # Later consider an end-time limit (items older than X)
    print &GetRcHtml(@fullrc);
  }
  print "<p>Page generated ", &TimeToText($^T), "<br>\n";
}

sub GetRcHtml {
  my @outrc = @_;
  my ($rcline, $html, $date, $sum, $edit, $count, $newtop, $author);
  my ($showedit, $inlist, $link, $all, $idOnly);
  my ($ts, $pagename, $summary, $isEdit, $host, $kind, $extraTemp);
  my %extra = ();
  my %changetime = ();
  my %pagecount = ();

  $showedit = &GetParam("rcshowedit", $ShowEdits);
  $showedit = &GetParam("showedit", $showedit);
  if ($showedit != 1) {
    my @temprc = ();
    foreach $rcline (@outrc) {
      ($ts, $pagename, $summary, $isEdit, $host) = split(/$FS3/o, $rcline);
      if ($showedit == 0) {  # 0 = No edits
        push(@temprc, $rcline)  if (!$isEdit);
      } else {               # 2 = Only edits
        push(@temprc, $rcline)  if ($isEdit);
      }
    }
    @outrc = @temprc;
  }

  # Later consider folding into loop above?
  # Later add lines to assoc. pagename array (for new RC display)
  foreach $rcline (@outrc) {
    ($ts, $pagename) = split(/$FS3/o, $rcline);
    $pagecount{$pagename}++;
    $changetime{$pagename} = $ts;
  }
  $date = "";
  $inlist = 0;
  $html = "";
  $all = &GetParam("rcall", 0);
  $all = &GetParam("all", $all);
  $newtop = &GetParam("rcnewtop", $RecentTop);
  $newtop = &GetParam("newtop", $newtop);
  $idOnly = &GetParam("rcidonly", "");

  @outrc = reverse @outrc if ($newtop);
  foreach $rcline (@outrc) {
    ($ts, $pagename, $summary, $isEdit, $host, $kind, $extraTemp)
      = split(/$FS3/o, $rcline);
    # Later: need to change $all for new-RC?
    next  if ((!$all) && ($ts < $changetime{$pagename}));
    next  if (($idOnly ne "") && ($idOnly ne $pagename));
    %extra = split(/$FS2/o, $extraTemp, -1);
    if ($date ne &CalcDay($ts)) {
      $date = &CalcDay($ts);
      if ($inlist) {
        $html .= "</UL>\n";
        $inlist = 0;
      }
      $html .= "<p><strong>" . $date . "</strong><p>\n";
    }
    if (!$inlist) {
      $html .= "<UL>\n";
      $inlist = 1;
    }

    $host = &QuoteHtml($host);
    if (defined($extra{'name'}) && defined($extra{'id'})) {
      $author = &GetAuthorLink($host, $extra{'name'}, $extra{'id'});
    } else {
      $author = &GetAuthorLink($host, "", 0);
    }

    $sum = "";
    if (($summary ne "") && ($summary ne "*")) {
      $summary = &QuoteHtml($summary);
      $sum = "<strong>[$summary]</strong> ";
    }
    $sum = "(no summary, tch tch tch)" unless defined $sum and length $sum;

    $edit = "";
    $edit = "<em>(edit)</em> "  if ($isEdit);

    $count = "";
    if ((!$all) && ($pagecount{$pagename} > 1)) {
      $count = "($pagecount{$pagename} ";
      if (&GetParam("rcchangehist", 1)) {
        $count .= &GetHistoryLink($pagename, "changes");
      } else {
        $count .= "changes";
      }
      $count .= ") ";
    }
    
    $link = "";
    if ($UseDiff && &GetParam("diffrclink", 1)) {
      $link .= &ScriptLinkDiff(4, $pagename, "(diff)", "") . "  ";
    }
    $link .= &GetPageLink($pagename);

    $html .= "<li>$link ";
    # Later do new-RC looping here.
    $html .= &CalcTime($ts) . " $count$edit by $author<br>$sum";
  }
  $html .= "</UL>\n" if ($inlist);
  return $html;
}

sub DoRandom {
  my ($id, @pageList);

  @pageList = &AllPagesList();  # Optimize?
  $id = $pageList[int(rand($#pageList + 1))];
  &ReBrowsePage($id, "", 0);
}

sub DoHistory {
  my ($id) = @_;
  my ($html, $canEdit);

  print &GetHeader("",&QuoteHtml("History of $id"), "", "norobots") . "<br>";
  &OpenPage($id);
  &OpenDefaultText();
  $canEdit = &UserCanEdit($id);
  $canEdit = 0;  # Turn off direct "Edit" links
  $html = &GetHistoryLine($id, $Page{'text_default'}, $canEdit, 1);
  &OpenKeptRevisions('text_default');
  foreach (reverse sort {$a <=> $b} keys %KeptRevisions) {
    next  if ($_ eq "");  # (needed?)
    $html .= &GetHistoryLine($id, $KeptRevisions{$_}, $canEdit, 0);
  }
  print $html, &GetCommonFooter();
}

sub GetHistoryLine {
  my ($id, $section, $canEdit, $isCurrent) = @_;
  my ($html, $expirets, $rev, $summary, $host, $user, $uid, $ts, $minor);
  my (%sect, %revtext);

  %sect = split(/$FS2/o, $section, -1);
  %revtext = split(/$FS3/o, $sect{'data'});
  $rev = $sect{'revision'};
  $summary = $revtext{'summary'};
  if ((defined($sect{'host'})) && ($sect{'host'} ne "")) {
    $host = $sect{'host'};
  } else {
    $host = $sect{'ip'};
    $host =~ s/\d+$/xxx/;      # Be somewhat anonymous (if no host)
  }
  $user = $sect{'username'};
  $uid = $sect{'id'};
  $ts = $sect{'ts'};
  $minor = "";
  $minor = "<i>(edit)</i> "  if ($revtext{'minor'});
  $expirets = $^T - ($KeepDays * 24 * 60 * 60);

  $html  = "Revision $rev: ";
  if ($isCurrent) {
    $html .= &GetPageLinkText($id, 'View') . " ";
    if ($canEdit) {
      $html .= &GetEditLink($id, 'Edit') . " ";
    }
    if ($UseDiff) {
      $html .= "Diff ";
    }
  } else {
    $html .= &GetOldPageLink('browse', $id, $rev, 'View') . " ";
    if ($canEdit) {
      $html .= &GetOldPageLink('edit',   $id, $rev, 'Edit') . " ";
    }
    if ($UseDiff) {
      $html .= &ScriptLinkDiffRevision(1, $id, $rev, 'Diff') . " ";
    }
  }
  $html .= ". . " . $minor . &TimeToText($ts) . " ";
  $html .= "by " . &GetAuthorLink($host, $user, $uid) . " ";
  if (defined($summary) && ($summary ne "") && ($summary ne "*")) {
    $summary = &QuoteHtml($summary);   # Thanks Sunir! :-)
    $html .= "<b>[$summary]</b> ";
  }
  $html .= "<br>\n";
  return $html;
}

# ==== HTML and page-oriented functions =======================================

sub ScriptLink {
  my ($action, $text) = @_;

  return "<a href=\"$ScriptName?$action\">$text</a>";
}

sub GetPageLink {
  my ($id) = @_;
  my $name = $id;

  $id =~ s|^/|$MainPage/|;
  if ($FreeLinks) {
    $id =~ s/ /_/g;
    $id = ucfirst($id);
    $name =~ s/_/ /g;
  }
  return &ScriptLink($id, $name);
}

sub GetPageLinkText {
  my ($id, $name) = @_;

  $id =~ s|^/|$MainPage/|;
  if ($FreeLinks) {
    $id =~ s/ /_/g;
    $id = ucfirst($id);
    $name =~ s/_/ /g;
  }
  return &ScriptLink($id, $name);
}

sub GetEditLink {
  my ($id, $name) = @_;

  if ($FreeLinks) {
    $id =~ s/ /_/g;
    $id = ucfirst($id);
    $name =~ s/_/ /g;
  }
  return &ScriptLink("action=edit&id=$id", $name);
}

sub GetOldPageLink {
  my ($kind, $id, $revision, $name) = @_;

  if ($FreeLinks) {
    $id =~ s/ /_/g;
    $id = ucfirst($id);
    $name =~ s/_/ /g;
  }
  return &ScriptLink("action=$kind&id=$id&revision=$revision", $name);
}

sub GetPageOrEditLink {
  my ($id, $name) = @_;
  my (@temp, $exists);

  if ($name eq "") {
    $name = $id;
    if ($FreeLinks) {
      $name =~ s/_/ /g;
    }
  }
  $id =~ s|^/|$MainPage/|;
  if ($FreeLinks) {
    $id =~ s/ /_/g;
    $id = ucfirst($id);
  }
  $exists = 0;
  if ($UseIndex) {
    if (!$IndexInit) {
      @temp = &AllPagesList();          # Also initializes hash
    }
    $exists = 1  if ($IndexHash{$id});
  } elsif (-f &GetPageFile($id)) {      # Page file exists
    $exists = 1;
  }
  if ($exists) {
    return &GetPageLinkText($id, $name);
  }
  if ($FreeLinks) {
    if ($name =~ m| |) {  # Not a single word
      $name = "[$name]";  # Add brackets so boundaries are obvious
    }
  }
  return $name . &GetEditLink($id,"?");
}

sub GetSearchLink {
  my ($id) = @_;
  my $name = $id;

  $id =~ s|.+/|/|;   # Subpage match: search for just /SubName
  if ($FreeLinks) {
    $name =~ s/_/ /g;  # Display with spaces
    $id =~ s/_/+/g;    # Search for url-escaped spaces
  }
  return &ScriptLink("search=$id", $name);
}

sub GetPrefsLink {
  return &ScriptLink("action=editprefs", "Signup/Preferences");
}

sub GetLoginLink {
  return &ScriptLink("action=login", "Login");
}

sub GetRandomLink {
  return &ScriptLink("action=random", "Random Page");
}

sub ScriptLinkDiff {
  my ($diff, $id, $text, $rev) = @_;

  $rev = "&revision=$rev"  if ($rev ne "");
  $diff = &GetParam("defaultdiff", 1)  if ($diff == 4);
  return &ScriptLink("action=browse&diff=$diff&id=$id$rev", $text);
}

sub ScriptLinkDiffRevision {
  my ($diff, $id, $rev, $text) = @_;

  $rev = "&diffrevision=$rev"  if ($rev ne "");
  $diff = &GetParam("defaultdiff", 1)  if ($diff == 4);
  return &ScriptLink("action=browse&diff=$diff&id=$id$rev", $text);
}

sub ScriptLinkTitle {
  my ($action, $text, $title) = @_;

  if ($FreeLinks) {
    $action =~ s/ /_/g;
  }
  return "<a href=\"$ScriptName?$action\" title=\"$title\">$text</a>";
}

sub GetAuthorLink {
  my ($host, $userName, $uid) = @_;
  my ($html, $title, $userNameShow);

  $userNameShow = $userName;
  if ($FreeLinks) {
    $userName     =~ s/ /_/g;
    $userNameShow =~ s/_/ /g;
  }
  if (&ValidId($userName) ne "") {  # Invalid under current rules
    $userName = "";  # Just pretend it isn't there.
  }
  # Later have user preference for link titles and/or host text?
  if (($uid > 0) && ($userName ne "")) {
    $html = &ScriptLinkTitle($userName, $userNameShow, "ID $uid from $host");
  } else {
    $html = $host;
  }
  return $html;
}

sub GetHistoryLink {
  my ($id, $text) = @_;

  if ($FreeLinks) {
    $id =~ s/ /_/g;
  }
  return &ScriptLink("action=history&id=$id", $text);
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

sub GetHeader {
    my ($id, $title, $oldId, $revision) = @_;
    my $header = "";
    my $LogoImage = "";
    my $result;
    my $cookie;

    my %data;

    # Set Cookie #{{{
    if (defined($SetCookie{'id'})) {
        $cookie = "$CookieName="
                . "rev&" . $SetCookie{'rev'}
                . "&id&" . $SetCookie{'id'}
                . "&randkey&" . $SetCookie{'randkey'};
        $cookie .= ";expires=Fri, 08-Sep-2010 19:48:23 GMT";
        $result = $q->header(-cookie=>$cookie);
    } else {
        $result = $q->header();
    }
    #}}}

    $data{GlobalCSS} = $GlobalCSS if $GlobalCSS;

    if ($FreeLinks) {
        $title =~ s/_/ /g;   # Display as spaces
    }

    if (lc $title eq lc $SiteName) {
        $data{doctitle} = $SiteName;
    } elsif ($ReverseTitle) {
        $data{doctitle} = "$title - $SiteName";
    } else {
        $data{doctitle} = "$SiteName: $title";
    }

    if($UserCSS && $UserData{'css'}) {
        $data{CSS} = $UserData{'css'};
    }

    if ($oldId ne "") {
        $data{redirect} .= q{<h3>}.("(redirected from "
                        . &GetEditLink($oldId, $oldId) . ")").q{</h3>};
    }

    if ($LogoUrl ne "") {
        $LogoImage = "img src=\"$LogoUrl\" alt=\"[Home]\" border=0";
        if (!$LogoLeft) {
            $LogoImage .= " align=\"right\"";
        }
        $header = &ScriptLink($HomePage, "<$LogoImage>");
    }

    if ($EnableInlineTitle) {
      if ($EnableSelfLinks && $id ne "") {
        $data{header} .= q{<h1>}.($header . &GetSearchLink($id)).q{</h1>};
      } else {
        $data{header} .= q{<h1>}.($header . $title).q{</h1>};
      }
    }

    if ($WantTopLinkBar && &GetParam("toplinkbar", 1)) {
        # Later consider smaller size?
        $data{header} .= &GetGotoBar($id) . "<hr>";
    }
    print $result if $result;

    if ($revision) {
      $data{meta_robot} = "NOINDEX,NOFOLLOW";
    }
    else {
      $data{meta_robot} = "INDEX,FOLLOW";
    }

    my $template =
      Text::Template->new( TYPE => 'FILE',
                           DELIMITERS => [ '<%','%>' ],
                           SOURCE => "$Templates/header.html"
                         );
    $data{bgcolor} = day2color((gmtime)[7]);
    $result = $template->fill_in(HASH => \%data);

    return $result;
}

sub day2color {
  my $day = shift;

  # Spring begins about 80 days into the year.  Since we start spring
  # at hue 0, subtract 80 from the day of the year, then correct for
  # negative days.  I think this will tolerate some sloppiness.

  my $hue = $day - 80;
  $hue += 365 if $hue < 0;

  my $sat = 0.10;         # Low saturation for a tint of white.
  my $val = 1.00;         # High value so it's not a tint of grey.

  # Gray.
  if ($hue < 0 or $sat == 0) {
    my $gray = $val * 255;
    return sprintf("#%2x%2x%2x", $gray, $gray, $gray);
  }

  # Cap the hue at 360, because we'll be converting day-of-year into
  # hue.  Then, if it's 360, roll it around to zero.
  $hue = 360 if $hue > 360;
  $hue = 0 if $hue == 360;
  $hue = $hue / 60;

  my $j = int($hue);
  my $f = $hue - $j;
  my $p = 255 * ($val * (1 - $sat));
  my $q = 255 * ($val * (1 - ($sat * $f)));
  my $t = 255 * ($val * (1 - ($sat * (1 - $f))));

  $val = $val * 255;

  return sprintf("#%2x%2x%2x", $val, $t, $p) if $j == 0;
  return sprintf("#%2x%2x%2x", $q, $val, $p) if $j == 1;
  return sprintf("#%2x%2x%2x", $p, $val, $t) if $j == 2;
  return sprintf("#%2x%2x%2x", $p, $q, $val) if $j == 3;
  return sprintf("#%2x%2x%2x", $t, $p, $val) if $j == 4;
  return sprintf("#%2x%2x%2x", $val, $p, $q) if $j == 5;
  die "j should never equal $j\n";
}

sub GetFooterText {
    my ($id, $rev) = @_;
    my %data;


    $data{footer} = &GetFormStart();
    $data{footer} .= &GetGotoBar($id);
    if (&UserCanEdit($id, 0)) {
        my $userName = &GetParam("username", "");
	if ($userName eq "") {
	  $data{footer} .= "Must login to edit";
	}
	else {
          if ($rev ne "") {
            $data{footer} .= &GetOldPageLink('edit',   $id, $rev, "Edit revision $rev of this page");
          } else {
            $data{footer} .= &GetEditLink($id, "Edit text of this page");
          }
	}
        $data{footer} .= " | " . &GetHistoryLink($id, "View other revisions");
    } else {
        $data{footer} .= "This page is read-only";
        $data{footer} .= " | " . &GetHistoryLink($id, "View other revisions");
    }
    if ($rev ne "") {
        $data{footer} .= " | " . &GetPageLinkText($id, "View current revision");
    }
    if ($Section{'revision'} > 0) {
        $data{footer} .= "<br>";
        if ($rev eq "") {  # Only for most current rev
            $data{footer} .= "Last edited ";
        } else {
            $data{footer} .= "Edited ";
        }
        $data{footer} .= &TimeToText($Section{ts});
    }
    if ($UseDiff) {
        $data{footer} .= " " . &ScriptLinkDiff(4, $id, "(diff)", $rev);
    }
    $data{footer} .= "<br>" . &GetSearchForm();
    if ($DataDir =~ m|/tmp/|) {
        $data{footer} .= "<br><b>Warning:</b> Database is stored in temporary"
                      . " directory $DataDir<br>";
    }
    $data{footer} .= " - Or find pages that link to <b>" . GetSearchLink($id) . "</b>";
    if (length $Footer) {
        $data{footer} .= $Footer;
    }
    $data{footer} .= $q->endform;

    my $template = Text::Template->new(TYPE => 'FILE', DELIMITERS => [ '<%','%>' ], SOURCE => "$Templates/footer.html");
    my $result = $template->fill_in(HASH => \%data);

    return $result;
}

sub end_html {
    my $footer = shift;
    my $template = Text::Template->new(TYPE => 'FILE', DELIMITERS => [ '<%','%>' ], SOURCE => "$Templates/footer.html");
    my $result = $template->fill_in(HASH => { footer => $footer });

    return $result;
}

sub GetCommonFooter {
    my %data;
    $data{footer} = "<hr>" . &GetFormStart() . &GetGotoBar("") . &GetSearchForm() . $q->endform;
    my $template = Text::Template->new(TYPE => 'FILE', DELIMITERS => [ '<%','%>' ], SOURCE => "$Templates/footer.html");
    my $result .= $template->fill_in(HASH => \%data);
    return $result;
}

sub GetFormStart {
  return $q->startform("POST", "$ScriptName",
                       "application/x-www-form-urlencoded");
}

sub GetGotoBar {
  my ($id) = @_;
  my ($main, $bartext);

  $bartext  = &GetPageLink($HomePage);
  if ($id =~ m|/|) {
    $main = $id;
    $main =~ s|/.*||;  # Only the main page name (remove subpage)
    $bartext .= " | " . &GetPageLink($main);
  }
  $bartext .= " | " . &GetPageLink("$RCName");

  my $userName = &GetParam("username", "");
  $bartext .= " | " . &GetPrefsLink();
  $bartext .= " | " . &GetLoginLink();
    if ($userName ne "") {
        $bartext .= " (You are " . &GetPageLink($userName) . ") ";
    } else {
        $bartext .= " (Not logged in) ";
    }

  if (&GetParam("linkrandom", 0)) {
    $bartext .= " | " . &GetRandomLink();
  }
  $bartext .= "<br>\n";
  return $bartext;
}

sub GetSearchForm {
    my ($result);
    if($WantSearch) {
        $result = "Search: " . $q->textfield(-name=>'search', -size=>20)
            . &GetHiddenValue("dosearch", 1);
    }
    return $result;
}

sub GetUrl {
  return $q->url(@_);
}

sub GetFullUrl {
  return &GetUrl(-full=>1);
}

sub GetRedirectPage {
  my ($newid, $name, $isEdit) = @_;
  my ($url, $html);

  # Normally get URL from script, but allow override.
  $url = ($FullUrl || &GetFullUrl()) . "?" . $newid;
  if ($RedirType < 3) {
    if ($RedirType == 1) {             # Use CGI.pm
      # NOTE: do NOT use -method (does not work with old CGI.pm versions)
      # Thanks to Daniel Neri for fixing this problem.
      $html = $q->redirect(-uri=>$url);
    } else {                           # Minimal header
      $html  = "Status: 302 Moved\n";
      $html .= "Location: $url\n";
      $html .= "Content-Type: text/html\n";  # Needed for browser failure
      $html .= "\n";
    }
    $html .= "\nYour browser should go to the $newid page.";
    $html .= "  If it does not, click <a href=\"$url\">$name</a>";
    $html .= " to continue.";
  } else {
    if ($isEdit) {
      $html  = &GetHeader("","Thanks for editing...", "", "norobots");
      $html .= "Thank you for editing <a href=\"$url\">$name</a>.";
    } else {
      $html  = &GetHeader("","Link to another page...", "", "norobots");
    }
    $html .= "\n<p>Follow the <a href=\"$url\">$name</a> link to continue.";
  }
  return $html;
}

# ==== Common wiki markup =====================================================

sub WikiToHTML {
  my ($pageText) = @_;

  %SaveUrl = ();
  %SaveNumUrl = ();
  $SaveUrlIndex = 0;
  $SaveNumUrlIndex = 0;
  $pageText =~ s/$FS//go;              # Remove separators (paranoia)

  if ($RawHtml) {
    $pageText =~ s/<html>((.|\n)*?)<\/html>/&StoreRaw($1)/ige;
  }

  $pageText = &QuoteHtml($pageText);
  $pageText =~ s/\\ *\r?\n/ /g;          # Join lines with backslash at end
  $pageText = &CommonMarkup($pageText, 1, 0);   # Multi-line markup
  $pageText = &WikiLinesToHtml($pageText);      # Line-oriented markup
  $pageText =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;  # Restore saved text
  $pageText =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;  # Restore nested saved text
  return $pageText;
}

sub CommonMarkup {
  my ($text, $useImage, $doLines) = @_;
  local $_ = $text;

  if ($doLines < 2) { # 2 = do line-oriented only
    # The <nowiki> tag stores text with no markup (except quoting HTML)
    s/\&lt;nowiki\&gt;((.|\n)*?)\&lt;\/nowiki\&gt;/&StoreRaw($1)/ige;
    # The <pre> tag wraps the stored text with the HTML <pre> tag
    s/\&lt;pre\&gt;((.|\n)*?)\&lt;\/pre\&gt;/&StorePre($1)/ige;
    s/\&lt;code\&gt;((.|\n)*?)\&lt;\/code\&gt;/&StoreCode($1)/ige;
    s/\&lt;perl\&gt;\s*\n?((.|\n)*?)\&lt;\/perl\&gt;/&StorePerl($1)/ige;
    s/\&lt;boxes\&gt;\s*\n?((.|\n)*?)\&lt;\/boxes\&gt;/&StoreBoxes($1)/ige;
    s/\&lt;tests\&gt;\s*\n?((.|\n)*?)\&lt;\/tests\&gt;/&StoreTests($1)/ige;
    s/\&lt;projects\&gt;\s*\n?((.|\n)*?)\&lt;\/projects\&gt;/&StoreProjects($1)/ige;
    s/\&lt;outline\&gt;\s*\n?((.|\n)*?)\&lt;\/outline\&gt;/&StoreOutline($1,"bullets")/ige;
    s/\&lt;outline-head\&gt;\s*\n?((.|\n)*?)\&lt;\/outline\&gt;/&StoreOutline($1,"headers")/ige;
    s/\&lt;outline-todo\&gt;\s*\n?((.|\n)*?)\&lt;\/outline\&gt;/&StoreOutline($1,"todo")/ige;
    s/\&lt;components\&gt;\s*\n?((.|\n)*?)\&lt;\/components\&gt;/&StoreComponents($1)/ige;

    if ($HtmlTags) {
        my ($t);
        foreach $t (@HtmlPairs) {
            s/\&lt;$t(\s[^<>]+?)?\&gt;(.*?)\&lt;\/$t\&gt;/<$t$1>$2<\/$t>/gis;
        }
        foreach $t (@HtmlSingle) {
            s/\&lt;$t(\s[^<>]+?)?\&gt;/<$t$1>/gi;
        }
    } else {
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

    s/\&lt;tt\&gt;(.*?)\&lt;\/tt\&gt;/<tt>$1<\/tt>/gis;  # <tt> (MeatBall)
    if ($HtmlLinks) {
      s/\&lt;A(\s[^<>]+?)\&gt;(.*?)\&lt;\/a\&gt;/&StoreHref($1, $2)/gise;
    }
    if ($FreeLinks) {
      # Consider: should local free-link descriptions be conditional?
      # Also, consider that one could write [[Bad Page|Good Page]]?
      s/\[\[$FreeLinkPattern\|([^\]]+)\]\]/&StorePageOrEditLink($1, $2)/geo;
      s/\[\[$FreeLinkPattern\]\]/&StorePageOrEditLink($1, "")/geo;
    }
    if ($BracketText) {  # Links like [URL text of link]
      s/\[$UrlPattern\s+([^\]]+?)\]/&StoreBracketUrl($1, $2)/geos;
      s/\[$InterLinkPattern\s+([^\]]+?)\]/&StoreBracketInterPage($1, $2)/geos;
      if ($WikiLinks && $BracketWiki) {  # Local bracket-links
        s/\[$LinkPattern\s+([^\]]+?)\]/&StoreBracketLink($1, $2)/geos;
      }
    }
    s/\[$UrlPattern\]/&StoreBracketUrl($1, "")/geo;
    s/\[$InterLinkPattern\]/&StoreBracketInterPage($1, "")/geo;
    s/$UrlPattern/&StoreUrl($1, $useImage)/geo;
    s/$InterLinkPattern/&StoreInterPage($1)/geo;
    if ($WikiLinks) {
      s/$LinkPattern/&GetPageOrEditLink($1, "")/geo;
    }
    s/$RFCPattern/&StoreRFC($1)/geo;
    s/$ISBNPattern/&StoreISBN($1)/geo;
    if ($ThinLine) {
      s/----+/<hr noshade size=1>/g;
      s/====+/<hr noshade size=2>/g;
    } else {
      s/----+/<hr>/g;
    }
  }
  if ($doLines) { # 0 = no line-oriented, 1 or 2 = do line-oriented
    # The quote markup patterns avoid overlapping tags (with 5 quotes)
    # by matching the inner quotes for the strong pattern.
    s/(\'*)\'\'\'(.*?)\'\'\'/$1<strong>$2<\/strong>/g;
    s/\'\'(.*?)\'\'/<em>$1<\/em>/g;
    if ($UseHeadings) {
      s/(^|\n)\s*(\=+)\s+([^\n]+)\s+\=+/&WikiHeading($1, $2, $3)/geo;
    }
  }
  return $_;
}

sub WikiLinesToHtml {
  my ($pageText) = @_;
  my ($pageHtml, @htmlStack, $code, $depth, $oldCode);

  @htmlStack = ();
  $depth = 0;
  $pageHtml = "";
  foreach (split(/\n/, $pageText)) {  # Process lines one-at-a-time
    $_ .= "\n";
    if (s/^(\;+)([^:]+\:?)\:?/<dt>$2<dd>/) {
      $code = "DL";
      $depth = length $1;
    } elsif (s/^(\:+)/<dt><dd>/) {
      $code = "DL";
      $depth = length $1;
    } elsif (s/^(\*+)/<li>/) {
      $code = "UL";
      $depth = length $1;
    } elsif (s/^(\#+)/<li>/) {
      $code = "OL";
      $depth = length $1;
    } elsif (/^[ \t].*\S/) {
      $code = "PRE";
      $depth = 1;
    } else {
      $depth = 0;
    }
    while (@htmlStack > $depth) {   # Close tags as needed
      my $code = pop(@htmlStack);
      $pageHtml .=  "</$code>";
      $pageHtml .= "</td></tr></table>" if $code eq 'PRE';
    }
    if ($depth > 0) {
      $depth = $IndentLimit  if ($depth > $IndentLimit);
      if (@htmlStack) {  # Non-empty stack
        $oldCode = pop(@htmlStack);
        if ($oldCode ne $code) {

          $pageHtml .= "</$oldCode>";

          # Handle PRE being in tables.
          $pageHtml .= "</td></tr></table>" if $oldCode eq 'PRE';
          $pageHtml .=  "<table border='1' cellspacing='0'><tr><td nowrap>"
            if $code eq 'PRE';

          $pageHtml .= "<$code>";
        }
        push(@htmlStack, $code);
      }
      while (@htmlStack < $depth) {
        push(@htmlStack, $code);
        $pageHtml .=  "<table border='1' cellspacing='0'><tr><td nowrap>"
          if $code eq 'PRE';
        $pageHtml .= "<$code>\n";
      }
    }
    s/^\s*$/<p>\n/;                        # Blank lines become <p> tags
    $pageHtml .= &CommonMarkup($_, 1, 2);  # Line-oriented common markup
  }
  while (@htmlStack > 0) {       # Clear stack
    my $code = pop(@htmlStack);
    $pageHtml .=  "</$code>";
    $pageHtml .= "</td></tr></table>" if $code eq 'PRE';
  }
  return $pageHtml;
}

sub QuoteHtml {
  my ($html) = @_;

  $html =~ s/&/&amp;/g;
  $html =~ s/</&lt;/g;
  $html =~ s/>/&gt;/g;
  $html =~ s/\&lt;!--/<!--/g;
  $html =~ s/--&gt;/-->/g;
  if ($AllowCharRefs) {
    $html =~ s/&amp;([\#a-zA-Z0-9]+);/&$1;/g;  # Allow character references
  }
  return $html;
}

sub UnquoteHtml {
  my ($html) = @_;

  $html =~ s/&amp;/&/g;
  $html =~ s/&lt;/</g;
  $html =~ s/&gt;/>/g;
  if ($AllowCharRefs) {
    $html =~ s/&\#(\d+);/chr($1)/ge;  # Allow character references
  }
  return $html;
}

sub StoreInterPage {
  my ($id) = @_;
  my ($link, $extra);

  ($link, $extra) = &InterPageLink($id);
  # Next line ensures no empty links are stored
  $link = &StoreRaw($link)  if ($link ne "");
  return $link . $extra;
}

sub InterPageLink {
  my ($id) = @_;
  my ($name, $site, $remotePage, $url, $punct);

  ($id, $punct) = &SplitUrlPunct($id);

  $name = $id;
  ($site, $remotePage) = split(/:/, $id, 2);
  $url = &GetSiteUrl($site);
  # The next line is an evil hack to prevent warnings
  # in the error logs.  Do something better later. -><-
  $url = "" unless defined $url;
  $id = "" unless defined $id;
  $punct = "" unless defined $punct;
  return ("", $id . $punct)  if ($url eq "");
  $remotePage =~ s/&amp;/&/g;  # Unquote common URL HTML
  $url .= $remotePage;
  return ("<a href=\"$url\">$name</a>", $punct);
}

sub StoreBracketInterPage {
  my ($id, $text) = @_;
  my ($site, $remotePage, $url, $index);

  ($site, $remotePage) = split(/:/, $id, 2);
  $remotePage =~ s/&amp;/&/g;  # Unquote common URL HTML
  $url = &GetSiteUrl($site);
  if ($text ne "") {
    return "[$id $text]"  if ($url eq "");
  } else {
    return "[$id]"  if ($url eq "");
    $text = &GetBracketUrlIndex($id);
  }
  $url .= $remotePage;
  return &StoreRaw("<a href=\"$url\">[$text]</a>");
}

sub GetBracketUrlIndex {
  my ($id) = @_;
  my ($index, $key);

  # Consider plain array?
  if ($SaveNumUrl{$id} > 0) {
    return $SaveNumUrl{$id};
  }
  $SaveNumUrlIndex++;  # Start with 1
  $SaveNumUrl{$id} = $SaveNumUrlIndex;
  return $SaveNumUrlIndex;
}

sub GetSiteUrl {
  my ($site) = @_;
  my ($data, $url, $status);

  if (!$InterSiteInit) {
    $InterSiteInit = 1;
    ($status, $data) = &ReadFile($InterFile);
    return ""  if (!$status);
    %InterSite = split(/\s+/, $data);  # Later consider defensive code
  }
  $url = $InterSite{$site}  if (defined($InterSite{$site}));
  return $url;
}

sub StoreRaw {
  my ($html) = @_;

  $SaveUrl{$SaveUrlIndex} = $html;
  return $FS . $SaveUrlIndex++ . $FS;
}

sub StorePre {
  my $html = shift;
  my $pre = ( "<table border='1' cellspacing='0'><tr><td nowrap><pre>" .
              $html .
              "</pre></td></tr></table>"
            );
  return &StoreRaw($pre);
}

sub StoreCode {
  my $html = shift;
  my $code = ( "<table border='1' cellspacing='0'><tr><td nowrap><code>" .
               $html .
               "</code></td></tr></table>"
             );
  return &StoreRaw($code);
}

sub StorePerl {
  my $source = shift;

  # Defer compiling the module until it's needed.
  require Perl::Tidy;

  # By the time we get here, the Wiki page has already been HTML
  # quoted.  We need to unquote the HTML for the source code, or it
  # may not look like source!
  $source = UnquoteHtml($source);

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
  Perl::Tidy::perltidy
    ( source      => \$source,
      destination => \$tidied,
      argv        => [ '-q', '-nanl', '-fnl' ],
    );

  # Convert it to HTML.  TODO: Make a clickable option to toggle line
  # numbers (-nnn option in the argv listref).

  my $html = "";
  Perl::Tidy::perltidy
    ( source      => \$tidied,
      destination => \$html,
      argv        => [ '-html', '-pre' ],
    );

  $html = ( "<table border='1' cellspacing='0'><tr><td nowrap>" .
            $html .
            "</td></tr></table>"
          );

  DUMP_TIDY and do {
    open(WHEE, ">/home/troc/tmp/tidied");
    print WHEE $html;
    close WHEE;
  };

  return StoreRaw($html);
}

sub StoreBoxes {
  my $source = shift;
  my @boxes;

  # The Wiki has munged $/, so we munge it back.  By the time we get
  # here, the Wiki page has already been HTML quoted.  We need to
  # unquote the HTML for the source code, or it may not look like
  # source!
  local $/ = "\n";
  $source = UnquoteHtml($source);

  while ($source =~ m/<box>\s*(.*?)\s*<\/box>/sig) {
    local $_ = $1;

    my $name  = "(unknown)"; $name  = $1 if /^\s*name\s*[:=]\s*(.*?)\s*$/mi;
    my $cpu   = "(unknown)"; $cpu   = $1 if /^\s*cpu\s*[:=]\s*(.*?)\s*$/mi;
    my $os    = "(unknown)"; $os    = $1 if /^\s*os\s*[:=]\s*(.*?)\s*$/mi;
    my $perl  = "(unknown)"; $perl  = $1 if /^\s*perl\s*[:=]\s*(.*?)\s*$/mi;
    my $event = "(none)";    $event = $1 if /^\s*event\s*[:=]\s*(.*?)\s*$/mi;
    my $gtk   = "(none)";    $gtk   = $1 if /^\s*gtk\s*[:=]\s*(.*?)\s*$/mi;
    my $iotty = "(none)";    $iotty = $1 if /^\s*iotty\s*[:=]\s*(.*?)\s*$/mi;
    my $tk    = "(none)";    $tk    = $1 if /^\s*tk\s*[:=]\s*(.*?)\s*$/mi;

    push( @boxes,
          "<tr>" .
          "<td>$name</td>" .
          "<td>$cpu</td>" .
          "<td>$os</td>" .
          "<td>$perl</td>" .
          "<td>$event</td>" .
          "<td>$gtk</td>" .
          "<td>$iotty</td>" .
          "<td>$tk</td>" .
          "</tr>"
        );
  }

  my $html =
    ( "<p>" .
      "<table width='100%' border='1' cellspacing='0' cellpadding='2'>" .
      "<tr><th align='center' colspan='8'>Machine Specifications</th></tr>"
    );

  if (@boxes) {
    $html .=
      ( "<tr>" .
        "<th>Machine</th>" .
        "<th>CPU</th>" .
        "<th>Operating System</th>" .
        "<th>Perl</th>" .
        "<th>Event</th>" .
        "<th>Gtk</th>" .
        "<th>IO::Tty</th>" .
        "<th>Tk</th>" .
        "</tr>" .
        join("", @boxes)
      );
  }
  else {
    $html .=
      "<tr><td align='center' colspan='8'>No machines entered.</td></tr>";
  }

  $html .= "</table></p>";

  return $html;
}

sub StoreProjects {
  my $source = shift;
  my @projects;

  # The Wiki has munged $/, so we munge it back.  By the time we get
  # here, the Wiki page has already been HTML quoted.  We need to
  # unquote the HTML for the source code, or it may not look like
  # source!
  local $/ = "\n";
  $source = UnquoteHtml($source);

  while ($source =~ m/<project>\s*(.*?)\s*<\/project>/sig) {
    local $_ = $1;

    my $name  = "(unknown)"; $name  = $1 if /^\s*name\s*[:=]\s*(.*?)\s*$/mi;
    my $url   = "";          $url   = $1 if /^\s*url\s*[:=]\s*(.*?)\s*$/mi;

    my $desc  = "No description.";
    $desc = $1 if /^\s*<desc>\s*(.*?)\s*<\/desc>/sim;
    $desc =~ s/\s+/ /g;

    my $project =
      ( "<p>" .
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

    $project .=
      ( "</td>" .
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

my %otl_colors = (
  "?" => "707070",
  "-" => "008000",
  "=" => "00C000",
  "+" => "004000",
  "*" => "000000",
  "#" => "800000",
);

sub StoreOutline {
  my ($source, $type) = @_;
  $type = "headers" unless defined $type;

  # The Wiki has munged $/, so we munge it back.  By the time we get
  # here, the Wiki page has already been HTML quoted.  We need to
  # unquote the HTML for the source code, or it may not look like
  # source!
  local $/ = "\n";
  $source = UnquoteHtml($source);

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
      my $stuff = ";" x ($level+1);
      $line =~ s/^([\!-\/\:-\@\[-\`\{-\~])\s+/<tt>$1 <\/tt>/;
      my $bullet = $1;

      $line =~ s/\:/&#58;/g;

      # TODO - Make this use style sheets!
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
    for (1..$#outline-1) {
      next if $outline[$_] =~ /\S/;
      if ($outline[$_-1] =~ /^(\s+)/) {
      	my $match = $1;
	if ($outline[$_+1] =~ /^$match/) {
	  $outline[$_] = $match;
	}
      }
    }

    # Close <font> tags in text notes.
    foreach (@outline) {
      s/\s*$/<\/font>/ if /^:/;
    }

    if ($type eq "todo") {
      unshift(
        @outline,
	"  \? = Maybe.  An idea without a plan.",
	"  \- = Planned.",
	"  \= = Started.  Actively being worked on.",
	"  \+ = Almost done.",
	"  \* = Done.  Hooray!",
	"  X = Canceled.",
	"  \# = Blocked.  Someone or something is in the way.",
      );
    }

#    # Wrap indented blocks in <pre></pre>.
#    my $index = @outline;
#    my $outside_pre = 1;
#    while ($index--) {
#      if ($outline[$index] =~ /^ /) {
#      	if ($outside_pre) {
#	  splice(@outline, $index+1, 0, "</pre>");
#	  $outside_pre = 0;
#	}
#        next;
#      }
#      unless ($outside_pre) {
#        splice(@outline, $index, 0, "<pre>");
#	$outside_pre = 1;
#      }
#    }

#return join("\n  ", @outline, "</pre>");
    return WikiLinesToHtml(join "\n", @outline);
  }
  return "<p>No outline.</p>";
}

sub StoreComponents {
  my $source = shift;
  my @components;

  # The Wiki has munged $/, so we munge it back.  By the time we get
  # here, the Wiki page has already been HTML quoted.  We need to
  # unquote the HTML for the source code, or it may not look like
  # source!
  local $/ = "\n";
  $source = UnquoteHtml($source);

  while ($source =~ m/<component>\s*(.*?)\s*<\/component>/sig) {
    local $_ = $1;

    my $name  = "(unknown)"; $name  = $1 if /^\s*name\s*[:=]\s*(.*?)\s*$/mi;
    my $url   = "";          $url   = $1 if /^\s*url\s*[:=]\s*(.*?)\s*$/mi;
    my $auth  = "";          $auth  = $1 if /^\s*author\s*[:=]\s*(.*?)\s*$/mi;
    my $mail  = "";          $mail  = $1 if /^\s*email\s*[:=]\s*(.*?)\s*$/mi;
    my $ver   = "";          $ver   = $1 if /^\s*version\s*[:=]\s*(.*?)\s*$/mi;
    my $cpan  = 0;           $cpan  = 1 if /^\s*<cpan\s*\/>\s*$/mi;

    my $desc  = "No description.";
    $desc = $1 if /^\s*<desc>\s*(.*?)\s*<\/desc>/sim;
    $desc =~ s/\s+/ /g;

    my $component =
      ( "<p>" .
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
      $component .=
        ( "<tr bgcolor=#DDDDDD>" .
          "<td>" .
          "<table border=0 cellpadding=0 cellspacing=0 width='100%'>"
        );

      ### Author.

      if (length($auth) or length($mail)) {
        $component .=
          ( "<tr>" .
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

        $component .=
          ( "</td>" .
            "</tr>"
          );
      }

      ### URL.

      if (length $url) {
        $component .=
          ( "<tr bgcolor=#DDDDDD>" .
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
        $component .=
          ( "<tr bgcolor=#DDDDDD>" .
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

      $component .=
        ( "<tr bgcolor=#DDDDDD>" .
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
      $component .= (
        "</font>" .
        "</td>" .
        "</tr>"
      );

      $component .=
        ( "</table>" .
          "</td>" .
          "</tr>"
        );
    }

    $component .=
      ( "</table>" .
        "</td>" .
        "</tr>" .
        "</table>" .
        "</p>"
      );

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

sub _colored_cell {
  my ($value, $true_color, $false_color) = @_;
  my $bgcolor = $false_color;
  $bgcolor = $true_color if $value;
  return "<td align='right' bgcolor='$bgcolor'>$value</td>";
}

sub StoreTests {
  my $source = shift;
  my @tests;

  # The Wiki has munged $/, so we munge it back.  By the time we get
  # here, the Wiki page has already been HTML quoted.  We need to
  # unquote the HTML for the source code, or it may not look like
  # source!
  local $/ = "\n";
  $source = UnquoteHtml($source);

  my $test_name = "Unknown Project";
  $test_name = $1 if $source =~ /<name>\s*(.*?)\s*<\/name>/si;

  while ($source =~ m/<test>\s*(.*?)\s*<\/test>/sig) {
    local $_ = $1;

    my $box = "(unknown)"; $box = $1 if /^\s*box\s*[:=]\s*(.*?)\s*$/mi;

    my $p_files = 0; $p_files = $1 if /^\s*pass\s*files\s*[:=]\s*(\d+)\s*$/mi;
    my $p_tests = 0; $p_tests = $1 if /^\s*pass\s*tests\s*[:=]\s*(\d+)\s*$/mi;
    my $f_files = 0; $f_files = $1 if /^\s*fail\s*files\s*[:=]\s*(\d+)\s*$/mi;
    my $f_tests = 0; $f_tests = $1 if /^\s*fail\s*tests\s*[:=]\s*(\d+)\s*$/mi;
    my $s_files = 0; $s_files = $1 if /^\s*skip\s*files\s*[:=]\s*(\d+)\s*$/mi;
    my $s_tests = 0; $s_tests = $1 if /^\s*skip\s*tests\s*[:=]\s*(\d+)\s*$/mi;

    my $wall = '(unknown)';
    $wall    = sprintf("%.2f", $1) if /^\s*wall\s*[:=]\s*([\d\.]+)\s*$/mi;
    my $cusr = '(unknown)';
    $cusr    = sprintf("%.2f", $1) if /^\s*cusr\s*[:=]\s*([\d\.]+)\s*$/mi;
    my $csys = '(unknown)';
    $csys    = sprintf("%.2f", $1) if /^\s*csys\s*[:=]\s*([\d\.]+)\s*$/mi;

    my $cpu  = '(unknown)';
    if ($cusr ne '(unknown)' and $csys ne '(unknown)') {
      $cpu = sprintf("%.2f", $cusr + $csys);
    }
    $cpu = sprintf("%.2f", $1) if /^\s*cpu\s*[:=]\s*([\d\.]+)\s*$/mi;

    push( @tests,
          "<tr>" .
          "<td>$box</td>" .
          _colored_cell($p_files, "#ccffcc", "#ffcccc") .
          _colored_cell($p_tests, "#ccffcc", "#ffcccc") .
          _colored_cell($f_files, "#ffcccc", "#ccffcc") .
          _colored_cell($f_tests, "#ffcccc", "#ccffcc") .
          _colored_cell($s_files, "#ffffcc", "#ccffcc") .
          _colored_cell($s_tests, "#ffffcc", "#ccffcc") .
          "<td align='right'>$wall</td>" .
          "<td align='right'>$cusr</td>" .
          "<td align='right'>$csys</td>" .
          "<td align='right'>$cpu</td>" .
          "</tr>"
        );
  }

  my $html =
    ( "<p>" .
      "<table width='100%' border='1' cellspacing='0' cellpadding='2'>" .
      "<tr>" .
      "<th align='center' colspan='11'>Test Results for $test_name</th>" .
      "</tr>"
    );

  if (@tests) {
    $html .=
      ( "<tr>" .
        "<th valign='middle' rowspan='2' align='center'>Machine</th>" .
        "<th colspan='2' align='center'>Passed</th>" .
        "<th colspan='2' align='center'>Failed</th>" .
        "<th colspan='2' align='center'>Skipped</th>" .
        "<th valign='middle' rowspan='2' align='center'>Wall<br>Time</th>" .
        "<th colspan='3' align='center'>CPU Time</th>" .
        "</tr>" .
        "<tr>" .
        "<th align='center'>Files</th>" .
        "<th align='center'>Tests</th>" .
        "<th align='center'>Files</th>" .
        "<th align='center'>Tests</th>" .
        "<th align='center'>Files</th>" .
        "<th align='center'>Tests</th>" .
        "<th align='center'>User</th>" .
        "<th align='center'>Sys</th>" .
        "<th align='center'>Total</th>" .
        "</tr>" .
        join("", @tests)
      );
  }
  else {
    $html .=
      "<tr><td align='center' colspan='11'>No tests entered.</td></tr>";
  }

  $html .= "</table></p>";

  return $html;
}

sub StoreHref {
  my ($anchor, $text) = @_;

  return "<a" . &StoreRaw($anchor) . ">$text</a>";
}

sub StoreUrl {
  my ($name, $useImage) = @_;
  my ($link, $extra);

  ($link, $extra) = &UrlLink($name, $useImage);
  # Next line ensures no empty links are stored
  $link = "" unless defined $link;
  $extra = "" unless defined $extra;
  $link = &StoreRaw($link)  if ($link ne "");
  return $link . $extra;
}

sub UrlLink {
  my ($rawname, $useImage) = @_;
  my ($name, $punct);

  ($name, $punct) = &SplitUrlPunct($rawname);
  if ($NetworkFile && $name =~ m|^file:|) {
    # Only do remote file:// links. No file:///c|/windows.
    if ($name =~ m|^file://[^/]|) {
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
        return(qq{&lt;<a href="$name">$email</a>&gt;}, $punct);
    }

  return ("<a href=\"$name\">$name</a>", $punct);
}

sub StoreBracketUrl {
  my ($url, $text) = @_;

  # we want to translate 'http:/?' into something more meaningful.
  $url =~ s{^http:/{0,2}(?=\?)}{}g;

  if ($text eq "") {
    $text = &GetBracketUrlIndex($url);
  }
  return &StoreRaw("<a href=\"$url\">[$text]</a>");
}

sub StoreBracketLink {
  my ($name, $text) = @_;

  return &StoreRaw(&GetPageLinkText($name, "[$text]"));
}

sub StorePageOrEditLink {
  my ($page, $name) = @_;

  if ($FreeLinks) {
    $page =~ s/^\s+//;      # Trim extra spaces
    $page =~ s/\s+$//;
    $page =~ s|\s*/\s*|/|;  # ...also before/after subpages
  }
  $name =~ s/^\s+//;
  $name =~ s/\s+$//;
  return &StoreRaw(&GetPageOrEditLink($page, $name));
}

sub StoreRFC {
  my ($num) = @_;

  return &StoreRaw(&RFCLink($num));
}

sub RFCLink {
  my ($num) = @_;

  return "RFC <a href=\"http://www.faqs.org/rfcs/rfc${num}.html\">$num</a>";
}

sub StoreISBN {
  my ($num) = @_;

  return &StoreRaw(&ISBNLink($num));
}

sub ISBNLink {
  my ($rawnum) = @_;
  my ($rawprint, $html, $num, $first, $second, $third);

  $num = $rawnum;
  $rawprint = $rawnum;
  $rawprint =~ s/ +$//;
  $num =~ s/[- ]//g;
  if (length($num) != 10) {
    return "ISBN $rawnum";
  }
  $first  = qq{ISBN <a href="http://isbn.nu/$num">$rawnum</a> };
  $second = "<a href=\"http://www.amazon.com/exec/obidos/"
            . "ISBN=$num\">Amazon</a>";
  $third  = "<a href=\"http://www.pricescan.com/books/"
            . "BookDetail.asp?isbn=$num\">Pricescan</a>";
  $html .= "$first";
  $html .= " ($second, $third)" if $ExtraISBNLinks;
  $html .= " "  if (substr($rawnum, -1, 1) eq ' ');  # Add space if old ISBN had space.
  return $html;
}

sub SplitUrlPunct {
  my ($url) = @_;
  my ($punct);

  if ($url =~ s/\"\"$//) {
    return ($url, "");
  }
  $punct = "";
  ($punct) = ($url =~ /([^a-zA-Z0-9\/\xc0-\xff]+)$/);
  $url =~ s/([^a-zA-Z0-9\/\xc0-\xff]+)$//;
  return ($url, $punct);
}

sub StripUrlPunct {
  my ($url) = @_;
  my ($junk);

  ($url, $junk) = &SplitUrlPunct($url);
  return $url;
}

sub WikiHeading {
  my ($pre, $depth, $text) = @_;

  $depth = length($depth);
  $depth = 6  if ($depth > 6);
  return $pre . "<H$depth>$text</H$depth>\n";
}

# ==== Difference markup and HTML =============================================

sub GetDiffHTML {
  my ($diffType, $id, $rev, $newText) = @_;
  my ($html, $diffText, $diffTextTwo, $priorName, $links, $usecomma);
  my ($major, $minor, $author, $useMajor, $useMinor, $useAuthor);

  $links = "(";
  $usecomma = 0;
  $major  = &ScriptLinkDiff(1, $id, "major diff", "");
  $minor  = &ScriptLinkDiff(2, $id, "minor diff", "");
  $author = &ScriptLinkDiff(3, $id, "author diff", "");
  $useMajor  = 1;
  $useMinor  = 1;
  $useAuthor = 1;
  if ($diffType == 1) {
    $priorName = "major";
    $useMajor  = 0;
  } elsif ($diffType == 2) {
    $priorName = "minor";
    $useMinor  = 0;
  } elsif ($diffType == 3) {
    $priorName = "author";
    $useAuthor = 0;
  }
  if ($rev ne "") {
    # Note: OpenKeptRevisions must have been done by caller.
    # Later optimize if same as cached revision
    $diffText = &GetKeptDiff($newText, $rev, 1);  # 1 = get lock
    if ($diffText eq "") {
      $diffText = "(The revisions are identical or unavilable.)";
    }
  } else {
    $diffText  = &GetCacheDiff($priorName);
  }
  $useMajor  = 0  if ($useMajor  && ($diffText eq &GetCacheDiff("major")));
  $useMinor  = 0  if ($useMinor  && ($diffText eq &GetCacheDiff("minor")));
  $useAuthor = 0  if ($useAuthor && ($diffText eq &GetCacheDiff("author")));
  $useMajor  = 0  if ((!defined(&GetPageCache('oldmajor'))) ||
                      (&GetPageCache("oldmajor") < 1));
  $useAuthor = 0  if ((!defined(&GetPageCache('oldauthor'))) ||
                      (&GetPageCache("oldauthor") < 1));
  if ($useMajor) {
    $links .= $major;
    $usecomma = 1;
  }
  if ($useMinor) {
    $links .= ", "  if ($usecomma);
    $links .= $minor;
    $usecomma = 1;
  }
  if ($useAuthor) {
    $links .= ", "  if ($usecomma);
    $links .= $author;
  }
  if (!($useMajor || $useMinor || $useAuthor)) {
    $links .= "no other diffs";
  }
  $links .= ")";

  if ((!defined($diffText)) || ($diffText eq "")) {
    $diffText = "No diff available.";
  }
  if ($rev ne "") {
    $html = "<b>Difference (from revision $rev to current revision)</b>\n"
            . "$links<br>" . &DiffToHTML($diffText) . "<hr>\n";
  } else {
    if (($diffType != 2) &&
        ((!defined(&GetPageCache("old$priorName"))) ||
         (&GetPageCache("old$priorName") < 1))) {
      $html = "<b>No diff available--this is the first $priorName"
              . " revision.</b>\n$links<hr>";
    } else {
      $html = "<b>Difference (from prior $priorName revision)</b>\n"
              . "$links<br>" . &DiffToHTML($diffText) . "<hr>\n";
    }
  }
  return $html;
}

sub GetCacheDiff {
  my ($type) = @_;
  my ($diffText);

  $diffText = &GetPageCache("diff_default_$type");
  $diffText = &GetCacheDiff('minor')  if ($diffText eq "1");
  $diffText = &GetCacheDiff('major')  if ($diffText eq "2");
  return $diffText;
}

# Must be done after minor diff is set and OpenKeptRevisions called
sub GetKeptDiff {
  my ($newText, $oldRevision, $lock) = @_;
  my (%sect, %data, $oldText);

  $oldText = "";
  if (defined($KeptRevisions{$oldRevision})) {
    %sect = split(/$FS2/o, $KeptRevisions{$oldRevision}, -1);
    %data = split(/$FS3/o, $sect{'data'}, -1);
    $oldText = $data{'text'};
  }
  return ""  if ($oldText eq "");  # Old revision not found
  return &GetDiff($oldText, $newText, $lock);
}

sub GetDiff {
  my ($old, $new, $lock) = @_;
  my ($diff_out, $oldName, $newName);

  &CreateDir($TempDir);
  $oldName = "$TempDir/old_diff";
  $newName = "$TempDir/new_diff";
  if ($lock) {
    &RequestDiffLock() or return "";
    $oldName .= "_locked";
    $newName .= "_locked";
  }
  &WriteStringToFile($oldName, $old);
  &WriteStringToFile($newName, $new);
  $diff_out = `diff $oldName $newName`;
  &ReleaseDiffLock()  if ($lock);
  $diff_out =~ s/\\ No newline.*\n//g;   # Get rid of common complaint.
  # No need to unlink temp files--next diff will just overwrite.
  return $diff_out;
}

sub DiffToHTML {
  my ($html) = @_;

  $html =~ s/\n--+//g;
  # Note: Need spaces before <br> to be different from diff section.
  $html =~ s/(^|\n)(\d+.*c.*)/$1 <br><strong>Changed: $2<\/strong><br>/g;
  $html =~ s/(^|\n)(\d+.*d.*)/$1 <br><strong>Removed: $2<\/strong><br>/g;
  $html =~ s/(^|\n)(\d+.*a.*)/$1 <br><strong>Added: $2<\/strong><br>/g;
  $html =~ s/\n((<.*\n)+)/&ColorDiff($1,"ffffaf")/ge;
  $html =~ s/\n((>.*\n)+)/&ColorDiff($1,"cfffcf")/ge;
  return $html;
}

sub ColorDiff {
  my ($diff, $color) = @_;

  $diff =~ s/(^|\n)[<>]/$1/g;
  $diff = &QuoteHtml($diff);
  # Do some of the Wiki markup rules:
  %SaveUrl = ();
  %SaveNumUrl = ();
  $SaveUrlIndex = 0;
  $SaveNumUrlIndex = 0;
  $diff =~ s/$FS//go;
  $diff =  &CommonMarkup($diff, 0, 1);      # No images, all patterns
  $diff =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;  # Restore saved text
  $diff =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;  # Restore nested saved text
  $diff =~ s/\r?\n/<br>/g;
  return "<table width=\"95\%\" bgcolor=#$color><tr><td>\n" . $diff
         . "</td></tr></table>\n";
}

# ==== Database (Page, Section, Text, Kept, User) functions ===================

sub OpenNewPage {
  my ($id) = @_;

  %Page = ();
  $Page{'version'} = 3;     # Data format version
  $Page{'revision'} = 0;    # Number of edited times
  $Page{'tscreate'} = $^T;  # Set once at creation
  $Page{'ts'} = $^T;        # Updated every edit
}

sub OpenNewSection {
  my ($name, $data) = @_;

  %Section = ();
  $Section{'name'} = $name;
  $Section{'version'} = 1;     # Data format version
  $Section{'revision'} = 0;    # Number of edited times
  $Section{'tscreate'} = $^T;  # Set once at creation
  $Section{'ts'} = $^T;        # Updated every edit
  $Section{'ip'} = $ENV{REMOTE_ADDR};
  $Section{'host'} = '';       # Updated only for real edits (can be slow)
  $Section{'id'} = $UserID;
  $Section{'username'} = &GetParam("username", "");
  $Section{'data'} = $data;
  $Page{$name} = join($FS2, %Section);  # Replace with save?
}

sub OpenNewText {
  my ($name) = @_;  # Name of text (usually "default")
  %Text = ();
  $Text{'text'} = "Empty page.  Click on 'Edit text of this page' below, or try [[$HomePage|the home page]].\n\n<!--\n\" vim: syntax=wiki\n-->\n";
  $Text{'minor'} = 0;      # Default as major edit
  $Text{'newauthor'} = 1;  # Default as new author
  $Text{'summary'} = '';
  &OpenNewSection("text_$name", join($FS3, %Text));
}

sub GetPageFile {
  my ($id) = @_;
  return fold_to_lowercase($PageDir . "/" . &GetPageDirectory($id) . "/$id.db");
}

sub OpenPage {
  my ($id) = @_;
  my ($fname, $data);

  if ($OpenPageName eq $id) {
    return;
  }
  %Section = ();
  %Text = ();
  $fname = &GetPageFile($id);
  if (-f $fname) {
    $data = &ReadFileOrDie($fname);
    %Page = split(/$FS1/o, $data, -1);  # -1 keeps trailing null fields
  } else {
    &OpenNewPage($id);
  }
  if ($Page{'version'} != 3) {
    &UpdatePageVersion();
  }
  $OpenPageName = $id;
}

sub OpenSection {
  my ($name) = @_;

  if (!defined($Page{$name})) {
    &OpenNewSection($name, "");
  } else {
    %Section = split(/$FS2/o, $Page{$name}, -1);
  }
}

sub OpenText {
  my ($name) = @_;

  if (!defined($Page{"text_$name"})) {
    &OpenNewText($name);
  } else {
    &OpenSection("text_$name");
    %Text = split(/$FS3/o, $Section{'data'}, -1);
  }
}

sub OpenDefaultText {
  &OpenText('default');
}

# Called after OpenKeptRevisions
sub OpenKeptRevision {
  my ($revision) = @_;

  %Section = split(/$FS2/o, $KeptRevisions{$revision}, -1);
  %Text = split(/$FS3/o, $Section{'data'}, -1);
}

sub GetPageCache {
  my ($name) = @_;

  return $Page{"cache_$name"};
}

# Always call SavePage within a lock.
sub SavePage {
  my $file = &GetPageFile($OpenPageName);

  $Page{'revision'} += 1;   # Number of edited times
  $Page{'ts'} = $^T;        # Updated every edit
  &CreatePageDir($PageDir, $OpenPageName);
  &WriteStringToFile($file, join($FS1, %Page));
}

sub SaveSection {
  my ($name, $data) = @_;

  $Section{'revision'} += 1;   # Number of edited times
  $Section{'ts'} = $^T;        # Updated every edit
  $Section{'ip'} = $ENV{REMOTE_ADDR};
  $Section{'id'} = $UserID;
  $Section{'username'} = &GetParam("username", "");
  $Section{'data'} = $data;
  $Page{$name} = join($FS2, %Section);
}

sub SaveText {
  my ($name) = @_;

  &SaveSection("text_$name", join($FS3, %Text));
}

sub SaveDefaultText {
  &SaveText('default');
}

sub SetPageCache {
  my ($name, $data) = @_;

  $Page{"cache_$name"} = $data;
}

sub UpdatePageVersion {
  &ReportError("Bad page version.");
}

sub KeepFileName {
  return fold_to_lowercase($KeepDir . "/" . &GetPageDirectory($OpenPageName) . "/$OpenPageName.kp");
}

sub SaveKeepSection {
  my $file = &KeepFileName();
  my $data;

  return  if ($Section{'revision'} < 1);  # Don't keep "empty" revision
  $Section{'keepts'} = $^T;
  $data = $FS1 . join($FS2, %Section);
  &CreatePageDir($KeepDir, $OpenPageName);
  &AppendStringToFile($file, $data);
}

sub ExpireKeepFile {
  my ($fname, $data, @kplist, %tempSection, $expirets);
  my ($anyExpire, $anyKeep, $expire, %keepFlag, $sectName, $sectRev);
  my ($oldMajor, $oldAuthor);

  $fname = &KeepFileName();
  return  if (!(-f $fname));
  $data = &ReadFileOrDie($fname);
  @kplist = split(/$FS1/o, $data, -1);  # -1 keeps trailing null fields
  return  if (length(@kplist) < 1);  # Also empty
  shift(@kplist)  if ($kplist[0] eq "");  # First can be empty
  return  if (length(@kplist) < 1);  # Also empty
  %tempSection = split(/$FS2/o, $kplist[0], -1);
  if (!defined($tempSection{'keepts'})) {
#   die("Bad keep file." . join("|", %tempSection));
    return;
  }
  $expirets = $^T - ($KeepDays * 24 * 60 * 60);
  return  if ($tempSection{'keepts'} >= $expirets);  # Nothing old enough

  $anyExpire = 0;
  $anyKeep   = 0;
  %keepFlag  = ();
  $oldMajor  = &GetPageCache('oldmajor');
  $oldAuthor = &GetPageCache('oldauthor');
  foreach (reverse @kplist) {
    %tempSection = split(/$FS2/o, $_, -1);
    $sectName = $tempSection{'name'};
    $sectRev = $tempSection{'revision'};
    $expire = 0;
    if ($sectName eq "text_default") {
      if (($KeepMajor  && ($sectRev == $oldMajor)) ||
          ($KeepAuthor && ($sectRev == $oldAuthor))) {
        $expire = 0;
      } elsif ($tempSection{'keepts'} < $expirets) {
        $expire = 1;
      }
    } else {
      if ($tempSection{'keepts'} < $expirets) {
        $expire = 1;
      }
    }
    if (!$expire) {
      $keepFlag{$sectRev . "," . $sectName} = 1;
      $anyKeep = 1;
    } else {
      $anyExpire = 1;
    }
  }

  if (!$anyKeep) {  # Empty, so remove file
    unlink($fname);
    return;
  }
  return  if (!$anyExpire);  # No sections expired
  open (OUT, ">$fname") or die ("cant write $fname: $!");
  foreach (@kplist) {
    %tempSection = split(/$FS2/o, $_, -1);
    $sectName = $tempSection{'name'};
    $sectRev = $tempSection{'revision'};
    if ($keepFlag{$sectRev . "," . $sectName}) {
      print OUT $FS1, $_;
    }
  }
  close(OUT) or die "can't close (ExpireKeepFile) on $fname: $!";
}

sub OpenKeptList {
  my ($fname, $data);

  @KeptList = ();
  $fname = &KeepFileName();
  return  if (!(-f $fname));
  $data = &ReadFileOrDie($fname);
  @KeptList = split(/$FS1/o, $data, -1);  # -1 keeps trailing null fields
}

sub OpenKeptRevisions {
  my ($name) = @_;  # Name of section
  my ($fname, $data, %tempSection);

  %KeptRevisions = ();
  &OpenKeptList();

  foreach (@KeptList) {
    %tempSection = split(/$FS2/o, $_, -1);
    next  if ($tempSection{'name'} ne $name);
    $KeptRevisions{$tempSection{'revision'}} = $_;
  }
}

sub LoadUserData {
  my ($data, $status);

  %UserData = ();
  ($status, $data) = &ReadFile(&UserDataFilename($UserID));
  if (!$status) {
    $UserID = 112;  # Could not open file.  Later warning message?
    return;
  }
  %UserData = split(/$FS1/o, $data, -1);  # -1 keeps trailing null fields
}

sub UserDataFilename {
  my ($id) = @_;

  return ""  if ($id < 1);
  return fold_to_lowercase($UserDir . "/" . ($id % 10) . "/$id.db");
}

# ==== Misc. functions ========================================================

sub ReportError {
    my @errors = @_;
    my %data;

    my $head = GetHeader("", "Submission error...", "", "norobots");
    my $foot = GetFooterText("SubmissionError", "");

    print $head;
    foreach (@errors) {
      print "<h2>$_</h2>";
    }
    print $foot;
}

sub ValidId {
  my ($id) = @_;

  if (length($id) > 120) {
    return "Page name is too long: $id";
  }
  if ($id =~ m| |) {
    return "Page name may not contain space characters: $id";
  }
  if ($UseSubpage) {
    if ($id =~ m|.*/.*/|) {
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
    if (!$UseSubpage) {
      if ($id =~ /\//) {
        return "Invalid Page $id (/ not allowed)";
      }
    }
    if (!($id =~ m|$FreeLinkPattern|)) {
      return "Invalid Page $id";
    }
    return "";
  } else {
    if (!($id =~ /^$LinkPattern$/o)) {
      return "Invalid Page $id";
    }
  }
  return "";
}

sub ValidIdOrDie {
  my ($id) = @_;
  my $error;

  $error = &ValidId($id);
  if ($error ne "") {
    &ReportError($error);
    return 0;
  }
  return 1;
}

sub UserCanEdit {
  my ($id, $deepCheck) = @_;

  # Optimized for the "everyone can edit" case (don't check passwords)
  if (($id ne "") && (-f &GetLockedPageFile($id))) {
    return 1  if (&UserIsAdmin());  # Requires more privledges
    # Later option for editor-level to edit these pages?
    return 0;
  }
  if (!$EditAllowed) {
    return 1  if (&UserIsEditor());
    return 0;
  }
  if (-f "$DataDir/noedit") {
    return 1  if (&UserIsEditor());
    return 0;
  }
  if ($deepCheck) {   # Deeper but slower checks (not every page)
    return 1  if (&UserIsEditor());
    return 0  if (&UserIsBanned());
  }

  return 1;
}

sub UserIsBanned {
  my ($host, $ip, $data, $status);

  ($status, $data) = &ReadFile("$DataDir/banlist");
  return 0  if (!$status);  # No file exists, so no ban
  $ip = $ENV{'REMOTE_ADDR'};
  $host = &GetRemoteHost(0);
  foreach (split(/\n/, $data)) {
    next  if ((/^\s*$/) || (/^#/));  # Skip empty, spaces, or comments
    return 1  if ($ip   =~ /$_/i);
    return 1  if ($host =~ /$_/i);
  }
  return 0;
}

sub UserIsAdmin {
  my (@pwlist, $userPassword);

  return 0  if ($AdminPass eq "");
  $userPassword = &GetParam("adminpw", "");
  return 0  if ($userPassword eq "");
  foreach (split(/\s+/, $AdminPass)) {
    next  if ($_ eq "");
    return 1  if ($userPassword eq $_);
  }
  return 0;
}

sub UserIsEditor {
  my (@pwlist, $userPassword);

  return 1  if (&UserIsAdmin());             # Admin includes editor
  return 0  if ($EditPass eq "");
  $userPassword = &GetParam("adminpw", "");  # Used for both
  return 0  if ($userPassword eq "");
  foreach (split(/\s+/, $EditPass)) {
    next  if ($_ eq "");
    return 1  if ($userPassword eq $_);
  }
  return 0;
}

sub GetLockedPageFile {
  my ($id) = @_;
  return fold_to_lowercase($PageDir . "/" . &GetPageDirectory($id) . "/$id.lck");
}

sub RequestLockDir {
  my ($name, $tries, $wait, $errorDie) = @_;
  my ($lockName, $n);

  &CreateDir($TempDir);
  $lockName = $LockDir . $name;
  $n = 0;
  while (mkdir($lockName, 0555) == 0) {
    if ($! != 17) {
      die("can't make $LockDir: $!\n") if $errorDie;
      return 0;
    }
    return 0  if ($n++ >= $tries);
    sleep($wait);
  }
  return 1;
}

sub ReleaseLockDir {
  my ($name) = @_;
  rmdir($LockDir . $name);
}

sub RequestLock {
  # 10 tries, 3 second wait, die on error
  return &RequestLockDir("main", 10, 3, 1);
}

sub ReleaseLock {
  &ReleaseLockDir('main');
}

sub ForceReleaseLock {
  my ($name) = @_;
  my $forced;

  # First try to obtain lock (in case of normal edit lock)
  # 5 tries, 3 second wait, do not die on error
  $forced = !&RequestLockDir($name, 5, 3, 0);
  &ReleaseLockDir($name);  # Release the lock, even if we didn't get it.
  return $forced;  # Lock was not forced.
}

sub RequestCacheLock {
  # 4 tries, 2 second wait, do not die on error
  return &RequestLockDir('cache', 4, 2, 0);
}

sub ReleaseCacheLock {
  &ReleaseLockDir('cache');
}

sub RequestDiffLock {
  # 4 tries, 2 second wait, do not die on error
  return &RequestLockDir('diff', 4, 2, 0);
}

sub ReleaseDiffLock {
  &ReleaseLockDir('diff');
}

sub RequestIndexLock {
  # 4 tries, 2 second wait, do not die on error
  return &RequestLockDir('index', 4, 2, 0);
}

sub ReleaseIndexLock {
  &ReleaseLockDir('index');
}

sub ReadFile {
  my ($fileName) = @_;
  my ($data);

  if (open(IN, "<$fileName")) {
    $data=<IN>;
    close IN;
    return (1, $data);
  }
  return (0, "");
}

sub ReadFileOrDie {
  my ($fileName) = @_;
  my ($status, $data);

  ($status, $data) = &ReadFile($fileName);
  if (!$status) {
    die "Can't open $fileName: $!";
  }
  return $data;
}

sub WriteStringToFile {
  my ($file, $string) = @_;

  open (OUT, ">$file") or die ("cant write $file: $!");
  print OUT  $string;
  close(OUT) or die "close failed (WriteStringToFile) on $file: $!";
}

sub AppendStringToFile {
  my ($file, $string) = @_;

  open (OUT, ">>$file") or die ("cant write $file: $!");
  print OUT  $string;
  close(OUT) or die "close failed (AppendStringToFile) on $file: $!";
}

sub CreateDir {
  my ($newdir) = @_;

  mkdir($newdir, 0775) unless -d $newdir;
  die "Failed to mkdir $newdir: $!" unless -d $newdir;
}

sub CreatePageDir {
  my ($dir, $id) = @_;
  my $subdir;

  &CreateDir($dir);  # Make sure main page exists
  $subdir = $dir . "/" . &GetPageDirectory($id);
  &CreateDir($subdir);
  if ($id =~ m|([^/]+)/|) {
    $subdir = $subdir . "/" . lc($1);
    &CreateDir($subdir);
  }
}

sub UpdateHtmlCache {
  my ($id, $html) = @_;
  my $idFile;

  $idFile = &GetHtmlCacheFile($id);
  &CreatePageDir($HtmlDir, $id);
  if (&RequestCacheLock()) {
    &WriteStringToFile($idFile, $html);
    &ReleaseCacheLock();
  }
}

sub GenerateAllPagesList {
  my (@pages, @dirs, $id, $dir);

  @dirs = qw(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z other);
  foreach $dir (@dirs) {
    while (<$PageDir/$dir/*.db $PageDir/$dir/*/*.db>) {
      s|^$PageDir/||;
      m|^[^/]+/(\S*).db|;
      $id = $1;
      push(@pages, $id);
    }
  }
  return sort(@pages);
}

sub AllPagesList {
  my ($rawIndex, $refresh, $status);

  if (!$UseIndex) {
    return &GenerateAllPagesList();
  }
  $refresh = &GetParam("refresh", 0);
  if ($IndexInit && !$refresh) {
    # May need to change for mod_perl eventually (cache consistency)
    # Possibly check timestamp of file then?
    return @IndexList;
  }
  if ((!$refresh) && (-f $IndexFile)) {
    ($status, $rawIndex) = &ReadFile($IndexFile);
    if ($status) {
      %IndexHash = split(/\s+/, $rawIndex);
      @IndexList = sort(keys %IndexHash);
      $IndexInit = 1;
      return @IndexList;
    }
    # If open fails just refresh the index
  }
  @IndexList = ();
  %IndexHash = ();
  &RequestIndexLock() or return @IndexList;   # Maybe generate? (high load?)
  @IndexList = &GenerateAllPagesList();
  foreach (@IndexList) {
    $IndexHash{$_} = 1;
  }
  &WriteStringToFile($IndexFile, join(" ", %IndexHash));
  $IndexInit = 1;
  &ReleaseIndexLock();
  return @IndexList;
}

sub CalcDay {
  my ($ts) = @_;

  $ts += $TimeZoneOffset;
  my ($sec, $min, $hour, $mday, $mon, $year) = localtime($ts);

  return ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November",
          "December")[$mon]. " " . $mday . ", " . ($year+1900);
}

sub CalcDayNow {
  return CalcDay($^T);
}

sub CalcTime {
  my ($ts) = @_;
  my ($ampm, $mytz);

  # Nasty timezone encoding.
  $ts += $TimeZoneOffset;
  my ($sec, $min, $hour, $mday, $mon, $year) = gmtime($ts);
  $ScriptTZ = "GMT";

  $mytz = "";
  if (($TimeZoneOffset == 0) && ($ScriptTZ ne "")) {
    $mytz = " " . $ScriptTZ;
  }
  $ampm = "";
  if ($UseAmPm) {
    $ampm = " am";
    if ($hour > 11) {
      $ampm = " pm";
      $hour = $hour - 12;
    }
    $hour = 12   if ($hour == 0);
  }
  $min = "0" . $min   if ($min<10);
  return $hour . ":" . $min . $ampm . $mytz;
}

sub TimeToText {
  my ($t) = @_;

  return &CalcDay($t) . " " . &CalcTime($t);
}

sub GetParam {
  my ($name, $default) = @_;
  my $result;

  $result = $q->param($name);
  if (!defined($result)) {
    if (defined($UserData{$name})) {
      $result = $UserData{$name};
    } else {
      $result = $default;
    }
  }
  return $result;
}

sub GetHiddenValue {
  my ($name, $value) = @_;

  $q->param($name, $value);
  return $q->hidden($name);
}

sub GetRemoteHost {
  my ($doMask) = @_;
  my ($rhost, $iaddr);

  $rhost = $ENV{REMOTE_HOST};
  if ($rhost eq "") {
    # Catch errors (including bad input) without aborting the script
    eval 'use Socket; $iaddr = inet_aton($ENV{REMOTE_ADDR});'
         . '$rhost = gethostbyaddr($iaddr, AF_INET)';
  }
  if ($rhost eq "") {
    $rhost = $ENV{REMOTE_ADDR};
    $rhost =~ s/\d+$/xxx/  if ($doMask);      # Be somewhat anonymous
  }
  return $rhost;
}
#END_OF_BROWSE_CODE

# == Page-editing and other special-action code ===============================

$OtherCode = ""; # Comment next line to always compile (slower)
#$OtherCode = <<'#END_OF_OTHER_CODE';

sub DoOtherRequest {
  my ($id, $action, $text, $search);

  $action = &GetParam("action", "");
  $id = &GetParam("id", "");
  if ($action ne "") {
    $action = lc($action);
    if      ($action eq "edit") {
      &DoEdit($id, 0, 0, "", 0)  if &ValidIdOrDie($id);
    } elsif ($action eq "unlock") {
      &DoUnlock();
    } elsif ($action eq "index") {
      &DoIndex();
    } elsif ($action eq "links") {
      &DoLinks();
    } elsif ($action eq "maintain") {
      &DoMaintain();
    } elsif ($action eq "pagelock") {
      &DoPageLock();
    } elsif ($action eq "editlock") {
      &DoEditLock();
    } elsif ($action eq "editprefs") {
      &DoEditPrefs();
    } elsif ($action eq "editbanned") {
      &DoEditBanned();
    } elsif ($action eq "editlinks") {
      &DoEditLinks();
    } elsif ($action eq "login") {
      &DoEnterLogin();
    } elsif ($action eq "newlogin") {
      $UserID = 0;
      &DoEditPrefs();  # Also creates new ID
    } else {
      &ReportError("Invalid action parameter $action");
    }
    return;
  }
  if (&GetParam("edit_prefs", 0)) {
    &DoUpdatePrefs();
    return;
  }
  if (&GetParam("edit_ban", 0)) {
    &DoUpdateBanned();
    return;
  }
  if (&GetParam("enter_login", 0)) {
    &DoLogin();
    return;
  }
  if (&GetParam("edit_links", 0)) {
    &DoUpdateLinks();
    return;
  }
  $search = &GetParam("search", "");
  if (($search ne "") || (&GetParam("dosearch", "") ne "")) {
    &DoSearch($search);
    return;
  }
  # Handle posted pages
  if (&GetParam("oldtime", "") ne "") {
    $id = &GetParam("title", "");
    &DoPost()  if &ValidIdOrDie($id);
    return;
  }
  &ReportError("Invalid URL.");
}

sub DoEdit {
  my ($id, $isConflict, $oldTime, $newText, $preview) = @_;
  my ($header, $editRows, $editCols, $userName, $revision, $oldText);
  my ($summary, $isEdit, $pageTime);

  if (!&UserCanEdit($id, 1)) {
    print &GetHeader("", "Editing Denied", "", "norobots");
    if (&UserIsBanned()) {
      print "Editing not allowed: user, ip, or network is blocked.",
            "<p>Contact the system administrator for more information.";
    } else {
      print "Editing not allowed: $SiteName is read-only.";
    }
    print &GetCommonFooter();
    return;
  }
  &OpenPage($id);
  &OpenDefaultText();
  $pageTime = $Section{'ts'};
  $header = "Editing $id";
  # Old revision handling
  $revision = &GetParam("revision", "");
  $revision =~ s/\D//g;  # Remove non-numeric chars
  if ($revision ne "") {
    &OpenKeptRevisions('text_default');
    if (!defined($KeptRevisions{$revision})) {
      $revision = "";
      # Later look for better solution, like error message?
    } else {
      &OpenKeptRevision($revision);
      $header = "Editing Revision $revision of $id";
    }
  }
  $oldText = $Text{'text'};
  if ($preview && !$isConflict) {
    $oldText = $newText;
  }
  $editRows = &GetParam("editrows", 20);
  $editCols = &GetParam("editcols", 65);
  print &GetHeader("", &QuoteHtml($header), "", "norobots");
  if ($revision ne "") {
    print "\n<b>Editing old revision $revision.  Saving this page will"
          . " replace the latest revision with this text.</b><br>"
  }
  if ($isConflict) {
    $editRows -= 10  if ($editRows > 19);
    print "\n<H1>Edit Conflict!</H1>\n";
    if ($isConflict>1) {
      # The main purpose of a new warning is to display more text
      # and move the save button down from its old location.
      print "\n<H2>(This is a new conflict)</H2>\n";
    }
    print "<p><strong>Someone saved this page after you started editing.",
          " The top textbox contains the saved text.",
          " Only the text in the top textbox will be saved.</strong><br>\n",
          " Scroll down to see your edited text.<br>\n",
          "Last save time: ", &TimeToText($oldTime),
          " (Current time is: ", &TimeToText($^T), ")<br>\n";
  }
  print &GetFormStart(),
        &GetHiddenValue("title", $id), "\n",
        &GetHiddenValue("oldtime", $pageTime), "\n",
        &GetHiddenValue("oldconflict", $isConflict), "\n";
  if ($revision ne "") {
    print &GetHiddenValue("revision", $revision), "\n";
  }
  print &GetTextArea('text', $oldText, $editRows, $editCols);
  $summary = &GetParam("summary", "*");
  print "<p>Summary:",
        $q->textfield(-name=>'summary',
                      -default=>$summary, -override=>1,
                      -size=>60, -maxlength=>200);
  if (&GetParam("recent_edit") eq "on") {
    print "<br>", $q->checkbox(-name=>'recent_edit', -checked=>1,
                               -label=>'This change is a minor edit.');
  } else {
    print "<br>", $q->checkbox(-name=>'recent_edit',
                               -label=>'This change is a minor edit.');
  }
  if ($UseEmailNotify) {
    if ($ShowNotify) {
      print "&nbsp;&nbsp;&nbsp;" .
           $q->checkbox(-name=> 'do_email_notify',
             -label=>"Send email notification that $id has been changed.",
             ($NotifyDefault ? ( -checked => 1 ) : () )
           );
    }
    else {
      print
        $q->hidden( -name => 'do_email_notify',
                    -default => ($NotifyDefault ? 1 : 0)
                  );
    }
  }
  print q{<br><input type="submit" name="Save" value="Save">};
  $userName = &GetParam("username", "");
  if ($userName ne "") {
    print " (Your user name is " . &GetPageLink($userName) . ") ";
  } else {
    print( " (Visit " . &GetPrefsLink() . " to set your user name, or ",
           &GetLoginLink() . " to log in.) "
         );
  }
  print q{<input type="submit" name="Preview" value="Preview">};

  if ($isConflict) {
    print "\n<br><hr><p><strong>This is the text you submitted:</strong><p>",
          &GetTextArea('newtext', $newText, $editRows, $editCols),
          "<p>\n";
  }
  print "<hr>\n";
  if ($preview) {
    print "<h2>Preview:</h2>\n";
    if ($isConflict) {
      print "<b>NOTE: This preview shows the other author's revision.",
            "</b><hr>\n";
    }
    $MainPage = $id;
    $MainPage =~ s|/.*||;  # Only the main page name (remove subpage)
    print &WikiToHTML($oldText) . "<hr>\n",
          "<h2>Preview only, not yet saved</h2>\n";
  }
  my %data;

    $data{footer} = &GetHistoryLink($id, "View other revisions") . "<br>\n".
        &GetGotoBar($id).
        $q->endform;

    my $template = Text::Template->new(TYPE => 'FILE', DELIMITERS => [ '<%','%>' ], SOURCE => "$Templates/footer.html");
    print $template->fill_in(HASH => \%data);
}

sub GetTextArea {
  my ($name, $text, $rows, $cols) = @_;

  if (&GetParam("editwide", 1)) {
    return $q->textarea(-name=>$name, -default=>$text,
                        -rows=>$rows, -columns=>$cols, -override=>1,
                        -style=>'width:100%', -wrap=>'virtual');
  }
  return $q->textarea(-name=>$name, -default=>$text,
                      -rows=>$rows, -columns=>$cols, -override=>1,
                      -wrap=>'virtual');
}

sub DoEditPrefs {
  my ($check, $recentName, %labels);

  $recentName = $RCName;
  $recentName =~ s/_/ /g;
  &DoNewLogin()  if ($UserID < 400);
  print &GetHeader("", "Editing Preferences", "", "norobots"),
        &GetFormStart(),
        GetHiddenValue("edit_prefs", 1), "\n",
        "<b>User Information:</b>\n",
        "<br>Your User ID number: $UserID <b>(Needed to log back in.)</b>\n",
        "<br>UserName: ", &GetFormText('username', "", 20, 50),
        " (blank to remove, or valid page name)",
        "<br>Set Password: ",
        q{<input type="password" name="p_password" value="*" size=15 maxlength=50>},
        " (blank to remove password)",
        "<br>(Passwords are only used for sharing user IDs",
        " and preferences between multiple systems.",
        " Passwords are completely optional.)";
  if ($AdminPass ne "") {
    print "<br>Administrator Password: ",
        q{<input type="password" name="p_adminpw" value="*" size=15 maxlength=50>},
          " (blank to remove password)",
        "<br>(Administrator passwords are used for special maintenance.)";
  }
  if ($UseEmailNotify) {
    print "<br>";
    print &GetFormCheck('notify', 1,
      'Include this address in the site email list. '
      . '(Uncheck the box to remove the address.)');
    print "<br> Email Address: ", &GetFormText('email', "", 30, 60);
  }
  print "<hr><b>$recentName:</b>\n",
        "<br>Default days to display: ",
        &GetFormText('rcdays', $RcDefault, 4, 9),
        "<br>", &GetFormCheck('rcnewtop', $RecentTop,
                              'Most recent changes on top'),
        "<br>", &GetFormCheck('rcall', 0,
                              'Show all changes (not just most recent)');
  %labels = (0=>'Hide minor edits', 1=>'Show minor edits',
             2=>'Show only minor edits');
  print "<br>Minor edit display: ",
        $q->popup_menu(-name=>'p_rcshowedit',
                       -values=>[0,1,2], -labels=>\%labels,
                       -default=>&GetParam("rcshowedit", $ShowEdits)),
        "<br>", &GetFormCheck('rcchangehist', 1,
                              'Use "changes" as link to history');
  if ($UseDiff) {
    print "<hr><b>Differences:</b>\n";
    print "<br>", &GetFormCheck('diffrclink', 1,
                                "Show (diff) links on $recentName");
    print "<br>", &GetFormCheck('alldiff', 0,
                                'Show differences on all pages');
    print "  (",  &GetFormCheck('norcdiff', 1,
                                "No differences on $recentName"), ")";
    %labels = (1=>'Major', 2=>'Minor', 3=>'Author');
    print "<br>Default difference type: ";
    print $q->popup_menu(-name=>'p_defaultdiff',
                         -values=>[1,2,3], -labels=>\%labels,
                         -default=>&GetParam("defaultdiff", 1));
  }
  print "<hr><b>Misc:</b>\n",
        "<br>Server time: ", &TimeToText($^T-$TimeZoneOffset),
        "<br>Time Zone offset (hours): ",
        &GetFormText('tzoffset', 0, 4, 9),
        "<br>", &GetFormCheck('editwide', 1,
                              'Use 100% wide edit area (if supported)'),
        "<br>Edit area rows: ", &GetFormText('editrows', 20, 4, 4),
        " columns: ", &GetFormText('editcols', 65, 4, 4),
        "<br>", &GetFormCheck('toplinkbar', 1,
                              'Show link bar on top'),
        "<br>", &GetFormCheck('linkrandom', 0,
                              'Add "Random Page" link to link bar');
  if ($UserCSS) {
    print "<br>Site-wide custom CSS (don't put &lt;style&gt; tags in here)<br>",
             q{<textarea name="p_css" rows="4" cols="65">},
              ( $UserData{'css'} || '' ),
             q{</textarea>},
  }

    my %data;
    $data{footer} = "<br>" . q{<input type="submit" name="Save" value="Save">} .
        "<hr>\n".
        &GetGotoBar("").
        $q->endform;

    my $template = Text::Template->new(TYPE => 'FILE', DELIMITERS => [ '<%','%>' ], SOURCE => "$Templates/footer.html");
    print $template->fill_in(HASH => \%data);
}

sub GetFormText {
  my ($name, $default, $size, $max) = @_;
  my $text = &GetParam($name, $default);

  return $q->textfield(-name=>"p_$name", -default=>$text,
                       -override=>1, -size=>$size, -maxlength=>$max);
}

sub GetFormCheck {
  my ($name, $default, $label) = @_;
  my $checked = (&GetParam($name, $default) > 0);

  return $q->checkbox(-name=>"p_$name", -override=>1, -checked=>$checked,
                      -label=>$label);
}

sub DoUpdatePrefs {
  my ($username, $password);

  # All link bar settings should be updated before printing the header
  &UpdatePrefCheckbox("toplinkbar");
  &UpdatePrefCheckbox("linkrandom");
  print &GetHeader("","Saving Preferences", "", "norobots"),
        "<br>";
  if ($UserID < 1001) {
    print "<b>Invalid UserID $UserID, preferences not saved.</b>";
    if ($UserID == 111) {
      print "<br>(Preferences require cookies, but no cookie was sent.)";
    }
    print &GetCommonFooter();
    return;
  }
  $username = &GetParam("p_username",  "");
  if ($FreeLinks) {
    $username =~ s/^\[\[(.+)\]\]/$1/;  # Remove [[ and ]] if added
    $username =  ucfirst($username);
  }
  if ($username eq "") {
    print "UserName removed.<br>";
    undef $UserData{'username'};
  } elsif ((!$FreeLinks) && (!($username =~ /^$LinkPattern$/o))) {
    print "Invalid UserName $username: not saved.<br>\n";
  } elsif ($FreeLinks && (!($username =~ /^$FreeLinkPattern$/o))) {
    print "Invalid UserName $username: not saved.<br>\n";
  } elsif (length($username) > 50) {  # Too long
    print "UserName must be 50 characters or less. (not saved)<br>\n";
  } else {
    print "UserName $username saved.<br>";
    $UserData{'username'} = $username;
  }
  $password = &GetParam("p_password",  "");
  if ($password eq "") {
    print "Password removed.<br>";
    undef $UserData{'password'};
  } elsif ($password ne "*") {
    print "Password changed.<br>";
    $UserData{'password'} = $password;
  }
  if ($AdminPass ne "") {
    $password = &GetParam("p_adminpw",  "");
    if ($password eq "") {
      print "Administrator password removed.<br>";
      undef $UserData{'adminpw'};
    } elsif ($password ne "*") {
      print "Administrator password changed.<br>";
      $UserData{'adminpw'} = $password;
      if (&UserIsAdmin()) {
        print "User has administrative abilities.<br>";
      } else {
        print "User <b>does not</b> have administrative abilities. ",
              "(Password does not match administrative password(s).)<br>";
      }
    }
  }
  if ($UseEmailNotify) {
    &UpdatePrefCheckbox("notify");
    &UpdateEmailList();
  }
  &UpdatePrefNumber("rcdays", 0, 0, 999999);
  &UpdatePrefCheckbox("rcnewtop");
  &UpdatePrefCheckbox("rcall");
  &UpdatePrefCheckbox("rcchangehist");
  &UpdatePrefCheckbox("editwide");
  if ($UseDiff) {
    &UpdatePrefCheckbox("norcdiff");
    &UpdatePrefCheckbox("diffrclink");
    &UpdatePrefCheckbox("alldiff");
    &UpdatePrefNumber("defaultdiff", 1, 1, 3);
  }
  &UpdatePrefNumber("rcshowedit", 1, 0, 2);
  &UpdatePrefNumber("tzoffset", 0, -999, 999);
  &UpdatePrefNumber("editrows", 1, 1, 999);
  &UpdatePrefNumber("editcols", 1, 1, 999);
  &UpdatePrefText("css") if $UserCSS;
  print "Server time: ", &TimeToText($^T-$TimeZoneOffset), "<br>";
  $TimeZoneOffset = &GetParam("tzoffset", 0) * (60 * 60);
  print "Local time: ", &TimeToText($^T), "<br>";

  &SaveUserData();
  print "<b>Preferences saved.</b>",
        &GetCommonFooter();
}

# add or remove email address from preferences to $DatDir/emails
sub UpdateEmailList {
  my (@old_emails);

  local $/ = "\n";  # don't slurp whole files in this sub.
  if (my $new_email = $UserData{'email'} = &GetParam("p_email", "")) {
    my $notify = $UserData{'notify'};
    if (-f "$DataDir/emails") {
      open(NOTIFY, "$DataDir/emails")
        or die "Couldn't read from $DataDir/emails: $!\n";
      @old_emails = <NOTIFY>;
      close(NOTIFY) or die "can't close (UpdateEmailList.1) on $DataDir/emails: $!";
    } else {
      @old_emails = ();
    }
    my $already_in_list = grep /$new_email/, @old_emails;
    if ($notify and (not $already_in_list)) {
      &RequestLock() or die "Could not get mail lock";
      open(NOTIFY, ">>$DataDir/emails")
        or die "Couldn't append to $DataDir/emails: $!\n";
      print NOTIFY $new_email, "\n";
      close(NOTIFY) or die "can't close (UpdateEmailList.2) on $DataDir/emails: $!";
      &ReleaseLock();
    }
    elsif ((not $notify) and $already_in_list) {
      &RequestLock() or die "Could not get mail lock";
      open(NOTIFY, ">$DataDir/emails")
        or die "Couldn't overwrite $DataDir/emails: $!\n";
      foreach (@old_emails) {
        print NOTIFY "$_" unless /$new_email/;
      }
      close(NOTIFY) or die "can't close (UpdateEmailList.3) on $DataDir/emails: $!";
      &ReleaseLock();
    }
  }
}

sub UpdatePrefCheckbox {
  my ($param) = @_;
  my $temp = &GetParam("p_$param", "*");

  $UserData{$param} = 1  if ($temp eq "on");
  $UserData{$param} = 0  if ($temp eq "*");
  # It is possible to skip updating by using another value, like "2"
}

sub UpdatePrefText {
  my ($param) = @_;
  my $temp = &GetParam("p_$param", "*");

  return  if ($temp eq "*");
  $UserData{$param} = $temp;
}

sub UpdatePrefNumber {
  my ($param, $integer, $min, $max) = @_;
  my $temp = &GetParam("p_$param", "*");

  return  if ($temp eq "*");
  $temp =~ s/[^-\d\.]//g;
  $temp =~ s/\..*//  if ($integer);
  return  if ($temp eq "");
  return  if (($temp < $min) || ($temp > $max));
  $UserData{$param} = $temp;
  # Later consider returning status?
}

sub DoIndex {
  print &GetHeader("","Index of all pages", "", "norobots"),
        "<br>";
  &PrintPageList(&AllPagesList());
  print &GetCommonFooter();
}

# Create a new user file/cookie pair
sub DoNewLogin {
  # Later consider warning if cookie already exists
  # (maybe use "replace=1" parameter)
  &CreateUserDir();
  $SetCookie{'id'} = &GetNewUserId;
  $SetCookie{'randkey'} = int(rand(1000000000));
  $SetCookie{'rev'} = 1;
  %UserCookie = %SetCookie;
  $UserID = $SetCookie{'id'};
  # The cookie will be transmitted in the next header
  %UserData = %UserCookie;
  $UserData{'createtime'} = $^T;
  $UserData{'createip'} = $ENV{REMOTE_ADDR};
  &SaveUserData();
}

sub DoEnterLogin {
    print &GetHeader("", "Login", "", "norobots").
        &GetFormStart().
        &GetHiddenValue("enter_login", 1), "\n",
        "<br>User ID number: ",
        $q->textfield(-name=>'p_userid', -value=>'',
                      -size=>15, -maxlength=>50).
        "<br>Password: ".
        q{<input type="password" name="p_password" size=15 maxlength=50>}.
        "<br>". q{<input type="submit" name="Login" value="Login">}.
        "<hr>\n".
        &GetGotoBar("").
        $q->endform. end_html();
}

sub DoLogin {
  my ($uid, $password, $success);

  $success = 0;
  $uid = &GetParam("p_userid", "");
  $uid =~ s/\D//g;
  $password = &GetParam("p_password",  "");
  if (($uid > 199) && ($password ne "") && ($password ne "*")) {
    $UserID = $uid;
    &LoadUserData();
    if ($UserID > 199) {
      if (defined($UserData{'password'}) &&
          ($UserData{'password'} eq $password)) {
        $SetCookie{'id'} = $uid;
        $SetCookie{'randkey'} = $UserData{'randkey'};
        $SetCookie{'rev'} = 1;
        $success = 1;
      }
    }
  }
  print &GetHeader("", "Login Results", "", "norobots");
  if ($success) {
    print "Login for user ID $uid complete.";
  } else {
    print "Login for user ID $uid failed.";
  }
  my %data;
  $data{footer} = "<hr>\n".
        &GetGotoBar("").
        $q->endform;

    my $template = Text::Template->new(TYPE => 'FILE', DELIMITERS => [ '<%','%>' ], SOURCE => "$Templates/footer.html");
    print $template->fill_in(HASH => \%data);
}

sub GetNewUserId {
  my ($id);

  $id = 1001;
  while (-f &UserDataFilename($id+1000)) {
    $id += 1000;
  }
  while (-f &UserDataFilename($id+100)) {
    $id += 100;
  }
  while (-f &UserDataFilename($id+10)) {
    $id += 10;
  }
  &RequestLock() or die "Could not get user-ID lock";
  while (-f &UserDataFilename($id)) {
    $id++;
  }
  &WriteStringToFile(&UserDataFilename($id), "lock");  # reserve the ID
  &ReleaseLock();
  return $id;
}

# Later get user-level lock
sub SaveUserData {
  my ($userFile, $data);

  &CreateUserDir();
  $userFile = &UserDataFilename($UserID);
  $data = join($FS1, %UserData);
  &WriteStringToFile($userFile, $data);
}

sub CreateUserDir {
  my ($n, $subdir);

  if (!(-d "$UserDir/0")) {
    &CreateDir($UserDir);

    foreach $n (0..9) {
      $subdir = "$UserDir/$n";
      &CreateDir($subdir);
    }
  }
}

sub DoSearch {
  my ($string) = @_;

  if ($string eq "") {
    &DoIndex();
    return;
  }
  print &GetHeader("",&QuoteHtml("Search for: $string"), "", "norobots"),
        "<br>";
  &PrintPageList(&SearchTitleAndBody($string));
  print &GetCommonFooter();
}

sub PrintPageList {
  my $pagename;

  print "<h2>", ($#_ + 1), " pages found:</h2>\n";
  foreach $pagename (@_) {
    print ".... "  if ($pagename =~ m|/|);
    print &GetPageLink($pagename), "<br>\n";
  }
}

sub DoLinks {
  print &GetHeader("",&QuoteHtml("Full Link List"), "", "norobots"),
        "<hr>";  # Extra lines to get below the logo
  &PrintLinkList(&GetFullLinkList());
  print "\n";

  my $template = Text::Template->new(TYPE => 'FILE', DELIMITERS => [ '<%','%>' ], SOURCE => "$Templates/footer.html");
  print $template->fill_in(HASH => {});
}

sub PrintLinkList {
  my ($pagelines, $page, $names, $editlink);
  my ($link, $extra, @links, %pgExists);

  %pgExists = ();
  foreach $page (&AllPagesList()) {
    $pgExists{$page} = 1;
  }
  $names = &GetParam("names", 1);
  $editlink = &GetParam("editlink", 0);
  foreach $pagelines (@_) {
    @links = ();
    foreach $page (split(' ', $pagelines)) {
      if ($page =~ /\:/) {  # URL or InterWiki form
        if ($page =~ /$UrlPattern/) {
          ($link, $extra) = &UrlLink($page);
        } else {
          ($link, $extra) = &InterPageLink($page);
        }
      } else {
        if ($pgExists{$page}) {
          $link = &GetPageLink($page);
        } else {
          $link = $page;
          if ($editlink) {
            $link .= &GetEditLink($page, "?");
          }
        }
      }
      push(@links, $link);
    }
    if (!$names) {
      shift(@links);
      print join(" ", @links), "<br />";
    }
    else {
      print "<dl><dt>", shift(@links), " links to:";
      if (@links > 1) {
        foreach my $lnk (@links) {
          print "<dd>$lnk";
        }
      }
      else {
        print " ", join("; ", @links);
      }
      print "</dl>";
    }
  }
}

sub GetFullLinkList {
  my ($name, $unique, $sort, $exists, $empty, $link, $search);
  my ($pagelink, $interlink, $urllink);
  my (@found, @links, @newlinks, @pglist, %pgExists, %seen);

  $unique = &GetParam("unique", 1);
  $sort = &GetParam("sort", 1);
  $pagelink = &GetParam("page", 1);
  $interlink = &GetParam("inter", 0);
  $urllink = &GetParam("url", 0);
  $exists = &GetParam("exists", 2);
  $empty = &GetParam("empty", 0);
  $search = &GetParam("search", "");
  if (($interlink == 2) || ($urllink == 2)) {
    $pagelink = 0;
  }

  %pgExists = ();
  @pglist = &AllPagesList();
  foreach $name (@pglist) {
    $pgExists{$name} = 1;
  }
  %seen = ();
  foreach $name (@pglist) {
    @newlinks = ();
    if ($unique != 2) {
      %seen = ();
    }
    @links = &GetPageLinks($name, $pagelink, $interlink, $urllink);

    foreach $link (@links) {
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
    
    unshift (@links, $name);

    if ($empty || ($#links > 0)) {  # If only one item, list is empty.
      push(@found, join(' ', @links));
    }
  }
  return @found;
}

sub GetPageLinks {
  my ($name, $pagelink, $interlink, $urllink) = @_;
  my ($text, @links);

  @links = ();
  &OpenPage($name);
  &OpenDefaultText();
  $text = $Text{'text'};
  $text =~ s/<html>((.|\n)*?)<\/html>/ /ig;
  $text =~ s/<nowiki>(.|\n)*?\<\/nowiki>/ /ig;
  $text =~ s/<pre>(.|\n)*?\<\/pre>/ /ig;
  $text =~ s/<code>(.|\n)*?\<\/code>/ /ig;
  $text =~ s/<perl>(.|\n)*?\<\/perl>/ /ig;
  $text =~ s/<boxes>(.|\n)*?\<\/boxes>/ /ig;
  $text =~ s/<tests>(.|\n)*?\<\/tests>/ /ig;

  if ($interlink) {
    $text =~ s/''+/ /g;  # Quotes can adjacent to inter-site links
    $text =~ s/$InterLinkPattern/push(@links, &StripUrlPunct($1)), ' '/geo;
  } else {
    $text =~ s/$InterLinkPattern/ /go;
  }
  if ($urllink) {
    $text =~ s/''+/ /g;  # Quotes can adjacent to URLs
    $text =~ s/$UrlPattern/push(@links, &StripUrlPunct($1)), ' '/geo;
  } else {
    $text =~ s/$UrlPattern/ /go;
  }
  if ($pagelink) {
    if ($FreeLinks) {
      $text =~ s/\[\[$FreeLinkPattern\|[^\]]+\]\]/push(@links,&SpaceToLine($1)),' '/geo;
      $text =~ s/\[\[$FreeLinkPattern\]\]/push(@links, &SpaceToLine($1)), ' '/geo;
    }
    if ($WikiLinks) {
      $text =~ s/$LinkPattern/push(@links, &StripUrlPunct($1)), ' '/geo;
    }
  }
  return @links;
}

sub SpaceToLine {
  my ($id) = @_;

  $id =~ s/ /_/g;
  return lc $id;
}

sub DoPost {
  my ($editDiff, $old, $newAuthor, $pgtime, $oldrev, $preview, $user);
  my $string = &GetParam("text", undef);
  my $id = &GetParam("title", "");
  my $summary = &GetParam("summary", "");
  my $oldtime = &GetParam("oldtime", "");
  my $oldconflict = &GetParam("oldconflict", "");
  my $isEdit = 0;
  my $editTime = $^T;
  my $authorAddr = $ENV{REMOTE_ADDR};

  if (!&UserCanEdit($id, 1)) {
    # This is an internal interface--we don't need to explain
    &ReportError("Editing not allowed for $id.");
    return;
  }

  if ($id eq "SampleUndefinedPage") {
    &ReportError("SampleUndefinedPage cannot be defined.");
    return;
  }
  if ($id eq "Sample_Undefined_Page") {
    &ReportError("[[Sample Undefined Page]] cannot be defined.");
    return;
  }
  $string =~ s/$FS//go;
  $summary =~ s/$FS//go;
  $summary =~ s/[\r\n]//g;
  # Add a newline to the end of the string (if it doesn't have one)
  $string .= "\n"  if (!($string =~ /\n$/));

  # Fucking spammers.
  if (
    $string =~ m{
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
      )
    }ix
    or
    $string =~ m{
      ( Ss+Ss+
      )
    }x
  ) {
    &ReportError("Error submitting your data.", "Please contact the web master if this persists.");
    return;
  }

  # Lock before getting old page to prevent races
  &RequestLock() or die "Could not get editing lock";
  # Consider extracting lock section into sub, and eval-wrap it?
  # (A few called routines can die, leaving locks.)
  &OpenPage($id);
  &OpenDefaultText();
  $old = $Text{'text'};
  $oldrev = $Section{'revision'};
  $pgtime = $Section{'ts'};

  $preview = 0;
  $preview = 1  if (&GetParam("Preview", "") ne "");
  if (!$preview && ($old eq $string)) {  # No changes (ok for preview)
    &ReleaseLock();
    &ReBrowsePage($id, "", 1);
    return;
  }
  # Later extract comparison?
  if (($UserID > 399) || ($Section{'id'} > 399))  {
    $newAuthor = ($UserID ne $Section{'id'});       # known user(s)
  } else {
    $newAuthor = ($Section{'ip'} ne $authorAddr);  # hostname fallback
  }
  $newAuthor = 1  if ($oldrev == 0);  # New page
  $newAuthor = 0  if (!$newAuthor);   # Standard flag form, not empty
  # Detect editing conflicts and resubmit edit
  if (($oldrev > 0) && ($newAuthor && ($oldtime != $pgtime))) {
    &ReleaseLock();
    if ($oldconflict>0) {  # Conflict again...
      &DoEdit($id, 2, $pgtime, $string, $preview);
    } else {
      &DoEdit($id, 1, $pgtime, $string, $preview);
    }
    return;
  }
  if ($preview) {
    &ReleaseLock();
    &DoEdit($id, 0, $pgtime, $string, 1);
    return;
  }

  $user = &GetParam("username", "");
  # If the person doing editing chooses, send out email notification
  if ($UseEmailNotify) {
    EmailNotify($id, $user) if &GetParam("do_email_notify", "") eq 'on';
  }
  if (&GetParam("recent_edit", "") eq 'on') {
    $isEdit = 1;
  }
  if (!$isEdit) {
    &SetPageCache('oldmajor', $Section{'revision'});
  }
  if ($newAuthor) {
    &SetPageCache('oldauthor', $Section{'revision'});
  }
  &SaveKeepSection();
  &ExpireKeepFile();
  if ($UseDiff) {
    &UpdateDiffs($id, $editTime, $old, $string, $isEdit, $newAuthor);
  }
  $Text{'text'} = $string;
  $Text{'minor'} = $isEdit;
  $Text{'newauthor'} = $newAuthor;
  $Text{'summary'} = $summary;
  $Section{'host'} = &GetRemoteHost(1);
  &SaveDefaultText();
  &SavePage();
  &WriteRcLog($id, $summary, $isEdit, $editTime, $user, $Section{'host'});
  if ($UseCache) {
    UnlinkHtmlCache($id);          # Old cached copy is invalid
    if ($Page{'revision'} == 1) {  # If this is a new page...
      &NewPageCacheClear($id);     # ...uncache pages linked to this one.
    }
  }
  if ($UseIndex && ($Page{'revision'} == 1)) {
    unlink($IndexFile);  # Regenerate index on next request
  }
  &ReleaseLock();
  &ReBrowsePage($id, "", 1);
}

sub UpdateDiffs {
  my ($id, $editTime, $old, $new, $isEdit, $newAuthor) = @_;
  my ($editDiff, $oldMajor, $oldAuthor);

  $editDiff  = &GetDiff($old, $new, 0);     # 0 = already in lock
  $oldMajor  = &GetPageCache('oldmajor');
  $oldAuthor = &GetPageCache('oldauthor');
  if ($UseDiffLog) {
    &WriteDiff($id, $editTime, $editDiff);
  }
  &SetPageCache('diff_default_minor', $editDiff);
  if ($isEdit || !$newAuthor) {
    &OpenKeptRevisions('text_default');
  }
  if (!$isEdit) {
    &SetPageCache('diff_default_major', "1");
  } else {
    &SetPageCache('diff_default_major', &GetKeptDiff($new, $oldMajor, 0));
  }
  if ($newAuthor) {
    &SetPageCache('diff_default_author', "1");
  } elsif ($oldMajor == $oldAuthor) {
    &SetPageCache('diff_default_author', "2");
  } else {
    &SetPageCache('diff_default_author', &GetKeptDiff($new, $oldAuthor, 0));
  }
}

# Send an email message.
sub SendEmail {
  my ($to, $from, $reply, $subject, $message) = @_;
    ### debug
    ## print "Content-type: text/plain\n\n";
    ## print " to: '$to'\n";
    ## return;
  # sendmail options:
  #    -odq : send mail to queue (i.e. later when convenient)
  #    -oi  : do not wait for "." line to exit
  #    -t   : headers determine recipient.
  open (SENDMAIL, "| $SendMail -oi -t ") or die "Can't send email: $!\n";
  print SENDMAIL <<"EOF";
From: $from
To: $to
Reply-to: $reply
Subject: $subject\n
$message
EOF
  close(SENDMAIL) or warn "sendmail didn't close nicely";
}

## Email folks who want to know a note that a page has been modified. - JimM.
sub EmailNotify {
  local $/ = "\n";   # don't slurp whole files in this sub.
  if ($UseEmailNotify) {
    my ($id, $user) = @_;
    if ($user) {
      $user = " by $user";
    }
    my $address;
    open(EMAIL, "$DataDir/emails")
      or die "Can't open $DataDir/emails: $!\n";
    $address = join ",", <EMAIL>;
    $address =~ s/\n//g;
    close(EMAIL);
    my $home_url = &GetUrl();
    my $page_url = $home_url . "?$id";
    my $editors_summary = &GetParam("summary", "*");
    if ($editors_summary ne '*' && $editors_summary ne '') {
      $editors_summary = "\n Summary: $editors_summary";
    }
    my $content = <<"END_MAIL_CONTENT";

 The $SiteName page $id at
   $page_url
 has been changed$user to revision $Page{revision}. $editors_summary

 (Replying to this notification will
  send email to the entire mailing list,
  so only do that if you mean to.

  To remove yourself from this list, visit
  ${home_url}?action=editprefs .)
END_MAIL_CONTENT
    my $subject = "The $id page at $SiteName has been changed.";
    # I'm setting the "reply-to" field to be the same as the "to:" field
    # which seems appropriate for a mailing list, especially since the
    # $EmailFrom string needn't be a real email address.
    &SendEmail($address, $EmailFrom, $address, $subject, $content);
  }
}

sub SearchTitleAndBody {
  my ($string) = @_;
  my ($name, $freeName, @found);

  foreach $name (&AllPagesList()) {
    &OpenPage($name);
    &OpenDefaultText();
    if (($Text{'text'} =~ /$string/i) || ($name =~ /$string/i)) {
      push(@found, $name);
    } elsif ($FreeLinks && ($name =~ m/_/)) {
      $freeName = $name;
      $freeName =~ s/_/ /g;
      if ($freeName =~ /$string/i) {
        push(@found, $name);
      }
    }
  }
  return @found;
}

sub SearchBody {
  my ($string) = @_;
  my ($name, @found);

  foreach $name (&AllPagesList()) {
    &OpenPage($name);
    &OpenDefaultText();
    if ($Text{'text'} =~ /$string/i){
      push(@found, $name);
    }
  }
  return @found;
}

sub UnlinkHtmlCache {
  my ($id) = @_;
  my $idFile;

  $idFile = &GetHtmlCacheFile($id);
  if (-f $idFile) {
    unlink($idFile);
  }
}

sub NewPageCacheClear {
  my ($id) = @_;
  my $name;

  return if (!$UseCache);
  $id =~ s|.+/|/|;  # If subpage, search for just the subpage
  foreach $name (&SearchBody($id)) {
    &UnlinkHtmlCache($name);
  }
}

# Note: all diff and recent-list operations should be done within locks.
sub DoUnlock {
  my $LockMessage = "Normal Unlock.";

  print &GetHeader("","Removing edit lock", "", "norobots"),
        "<p>This operation may take several seconds...\n";
  if (&ForceReleaseLock('main')) {
    $LockMessage = "Forced Unlock.";
  }
  # Later display status of other locks?
  &ForceReleaseLock('cache');
  &ForceReleaseLock('diff');
  &ForceReleaseLock('index');
  print "<br><h2>$LockMessage</h2>",
        &GetCommonFooter();
}

# Note: all diff and recent-list operations should be done within locks.
sub WriteRcLog {
  my ($id, $summary, $isEdit, $editTime, $name, $rhost) = @_;
  my ($extraTemp, %extra);

  %extra = ();
  $extra{'id'} = $UserID  if ($UserID > 0);
  $extra{'name'} = $name  if ($name ne "");
  $extraTemp = join($FS2, %extra);
  # The two fields at the end of a line are kind and extension-hash
  my $rc_line = join($FS3, $editTime, $id, $summary,
                     $isEdit, $rhost, "0", $extraTemp);
  if (!open(OUT, ">>$RcFile")) {
    die "$RCName log error: $!";
  }
  print OUT  $rc_line . "\n";
  close(OUT);
}

sub WriteDiff {
  my ($id, $editTime, $diffString) = @_;

  open (OUT, ">>$DataDir/diff_log") or die ("cant write diff_log");
  print OUT  "------\n" . $id . "|" . $editTime . "\n",
             $diffString;
  close(OUT);
}

sub DoMaintain {
  my ($name, $fname, $data);
  print &GetHeader("","Maintenance on all pages", "", "norobots"),
        "<br>";
  $fname = "$DataDir/maintain";
  if (!&UserIsAdmin()) {
    if ((-f $fname) && ((-M $fname) < 0.5)) {
      print "Maintenance not done.  ";
      print "(Maintenance can only be done once every 12 hours.)";
      print "  Remove the \"maintain\" file or wait.";
      print &GetCommonFooter();
      return;
    }
  }
  &RequestLock() or die "Could not get maintain-lock";
  foreach $name (&AllPagesList()) {
    &OpenPage($name);
    &OpenDefaultText();
    &ExpireKeepFile();
    print ".... "  if ($name =~ m|/|);
    print &GetPageLink($name), "<br>\n";
  }
  &WriteStringToFile($fname, "Maintenance done at " . &TimeToText($^T));
  &ReleaseLock();
  # Do any rename/deletion commands
  # (Must be outside lock because it will grab its own lock)
  $fname = "$DataDir/editlinks";
  if (-f $fname) {
    $data = &ReadFileOrDie($fname);
    print "<hr>Processing rename/delete commands:<br>\n";
    &UpdateLinksList($data, 1, 1);  # Always update RC and links
    unlink("$fname.old");
    rename($fname, "$fname.old");
  }
  print &GetCommonFooter();
}

sub UserIsEditorOrError {
  if (!&UserIsEditor()) {
    print "<p>This operation is restricted to site editors only...\n";
    print &GetCommonFooter();
    return 0;
  }
  return 1;
}

sub UserIsAdminOrError {
  if (!&UserIsAdmin()) {
    print "<p>This operation is restricted to administrators only...\n";
    print &GetCommonFooter();
    return 0;
  }
  return 1;
}

sub DoEditLock {
  my ($fname);

  print &GetHeader("","Set or Remove global edit lock", "", "norobots");
  return  if (!&UserIsAdminOrError());
  $fname = "$DataDir/noedit";
  if (&GetParam("set", 1)) {
    &WriteStringToFile($fname, "editing locked.");
  } else {
    unlink($fname);
  }
  if (-f $fname) {
    print "<p>Edit lock created.<br>";
  } else {
    print "<p>Edit lock removed.<br>";
  }
  print &GetCommonFooter();
}

sub DoPageLock {
  my ($fname, $id);

  print &GetHeader("","Set or Remove page edit lock", "", "norobots");
  return  if (!&UserIsAdminOrError());
  if (!&UserIsAdmin()) {
    print "<p>This operation is restricted to administrators only...\n";
    print &GetCommonFooter();
    return;
  }
  $id = &GetParam("id", "");
  if ($id eq "") {
    print "<p>Missing page id to lock/unlock...\n";
    return;
  }
  return  if (!&ValidIdOrDie($id));       # Later consider nicer error?
  $fname = &GetLockedPageFile($id);
  if (&GetParam("set", 1)) {
    &WriteStringToFile($fname, "editing locked.");
  } else {
    unlink($fname);
  }
  if (-f $fname) {
    print "<p>Lock for $id created.<br>";
  } else {
    print "<p>Lock for $id removed.<br>";
  }
  print &GetCommonFooter();
}

sub DoEditBanned {
  my ($banList, $status);

  print &GetHeader("", "Editing Banned list", "", "norobots");
  return  if (!&UserIsAdminOrError());
  ($status, $banList) = &ReadFile("$DataDir/banlist");
  $banList = ""  if (!$status);
  print &GetFormStart(),
        GetHiddenValue("edit_ban", 1), "\n",
        "<b>Banned IP/network/host list:</b><br>\n",
        "<p>Each entry is either a commented line (starting with #), ",
        "or a Perl regular expression (matching either an IP address or ",
        "a hostname).  <b>Note:</b> To test the ban on yourself, you must ",
        "give up your admin access (remove password in Preferences).",
        "<p>Examples:<br>",
        "\\.foocorp.com\$  (blocks hosts ending with .foocorp.com)<br>",
        "^123.21.3.9\$  (blocks exact IP address)<br>",
        "^123.21.3.  (blocks whole 123.21.3.* IP network)<p>",
        &GetTextArea('banlist', $banList, 12, 50),
        "<br>", q{<input type="submit" name="Save" value="Save">},
        "<hr>\n",
        &GetGotoBar(""),
        $q->endform,
        end_html();
}

sub DoUpdateBanned {
  my ($newList, $fname);

  print &GetHeader("", "Updating Banned list", "", "norobots");
  return  if (!&UserIsAdminOrError());
  $fname = "$DataDir/banlist";
  $newList = &GetParam("banlist", "#Empty file");
  if ($newList eq "") {
    print "<p>Empty banned list or error.";
    print "<p>Resubmit with at least one space character to remove.";
  } elsif ($newList =~ /^\s*$/s) {
    unlink($fname);
    print "<p>Removed banned list";
  } else {
    &WriteStringToFile($fname, $newList);
    print "<p>Updated banned list";
  }
  print &GetCommonFooter();
}

# ==== Editing/Deleting pages and links =======================================

sub DoEditLinks {
  print &GetHeader("", "Editing Links", "", "norobots");
  if ($AdminDelete) {
    return  if (!&UserIsAdminOrError());
  } else {
    return  if (!&UserIsEditorOrError());
  }
  print &GetFormStart(),
        GetHiddenValue("edit_links", 1), "\n",
        "<b>Editing/Deleting page titles:</b><br>\n",
        "<p>Enter one command on each line.  Commands are:<br>",
        "<tt>!PageName</tt> -- deletes the page called PageName<br>\n",
        "<tt>=OldPageName=NewPageName</tt> -- Renames OldPageName ",
        "to NewPageName and updates links to OldPageName.<br>\n",
        "<tt>|OldPageName|NewPageName</tt> -- Changes links to OldPageName ",
        "to NewPageName.",
        " (Used to rename links to non-existing pages.)<br>\n",
        &GetTextArea('commandlist', "", 12, 50),
        $q->checkbox(-name=>"p_changerc", -override=>1, -checked=>1,
                      -label=>"Edit $RCName"),
        "<br>\n",
        $q->checkbox(-name=>"p_changetext", -override=>1, -checked=>1,
                      -label=>"Substitute text for rename"),
        "<br>", q{<input type="submit" name="Edit" value="Edit">},
        "<hr>\n",
        &GetGotoBar(""),
        $q->endform,
        end_html();
}

sub UpdateLinksList {
  my ($commandList, $doRC, $doText) = @_;

  &RequestLock() or die "UpdateLinksList could not get main lock";
  unlink($IndexFile)  if ($UseIndex);
  foreach (split(/\n/, $commandList)) {
    s/\s+$//g;
    next  if (!(/^[=!|]/));  # Only valid commands.
    print "Processing $_<br>\n";
    if (/^\!(.+)/) {
      &DeletePage($1, $doRC, $doText);
    } elsif (/^\=(?:\[\[)?([^]=]+)(?:\]\])?\=(?:\[\[)?([^]=]+)(?:\]\])?/) {
      &RenamePage($1, $2, $doRC, $doText);
    } elsif (/^\|(?:\[\[)?([^]|]+)(?:\]\])?\|(?:\[\[)?([^]|]+)(?:\]\])?/) {
      &RenameTextLinks($1, $2);
    }
  }
  &NewPageCacheClear(".");  # Clear cache (needs testing?)
  unlink($IndexFile)  if ($UseIndex);
  &ReleaseLock();
}

sub DoUpdateLinks {
  my ($commandList, $doRC, $doText);

  print &GetHeader("", "Updating Links", "", "norobots");
  if ($AdminDelete) {
    return  if (!&UserIsAdminOrError());
  } else {
    return  if (!&UserIsEditorOrError());
  }
  $commandList = &GetParam("commandlist", "");
  $doRC   = &GetParam("p_changerc", "0");
  $doRC   = 1  if ($doRC eq "on");
  $doText = &GetParam("p_changetext", "0");
  $doText = 1  if ($doText eq "on");
  if ($commandList eq "") {
    print "<p>Empty command list or error.";
  } else {
    &UpdateLinksList($commandList, $doRC, $doText);
    print "<p>Finished command list.";
  }
  print &GetCommonFooter();
}

sub EditRecentChanges {
  my ($action, $old, $new) = @_;

  &EditRecentChangesFile($RcFile,    $action, $old, $new);
  &EditRecentChangesFile($RcOldFile, $action, $old, $new);
}

sub EditRecentChangesFile {
  my ($fname, $action, $old, $new) = @_;
  my ($status, $fileData, $errorText, $rcline, @rclist);
  my ($outrc, $ts, $page, $junk);

  ($status, $fileData) = &ReadFile($fname);
  if (!$status) {
    # Save error text if needed.
    $errorText = "<p><strong>Could not open $RCName log file:"
                 . "</strong> $fname<p>Error was:\n<pre>$!</pre>\n";
    print $errorText;   # Maybe handle differently later?
    return;
  }
  $outrc = "";
  @rclist = split(/\n/, $fileData);
  foreach $rcline (@rclist) {
    ($ts, $page, $junk) = split(/$FS3/o, $rcline);
    if ($page eq $old) {
      if ($action == 1) {  # Delete
        ; # Do nothing (don't add line to new RC)
      } elsif ($action == 2) {
        $junk = $rcline;
        $junk =~ s/^(\d+$FS3)$old($FS3)/"$1$new$2"/geo;
        $outrc .= $junk . "\n";
      }
    } else {
      $outrc .= $rcline . "\n";
    }
  }
  &WriteStringToFile($fname . ".old", $fileData);  # Backup copy
  &WriteStringToFile($fname, $outrc);
}

# Delete and rename must be done inside locks.
sub DeletePage {
  my ($page, $doRC, $doText) = @_;
  my ($fname, $status);

  $page =~ s/ /_/g;
  $page =~ s/\[+//;
  $page =~ s/\]+//;
  $status = &ValidId($page);
  if ($status ne "") {
    print "Delete-Page: page $page is invalid, error is: $status<br>\n";
    return;
  }

  $fname = &GetPageFile($page);
  unlink($fname)  if (-f $fname);
  $fname = fold_to_lowercase($KeepDir . "/" . &GetPageDirectory($page) .  "/$page.kp");
  unlink($fname)  if (-f $fname);
  unlink($IndexFile)  if ($UseIndex);
  &EditRecentChanges(1, $page, "")  if ($doRC);  # Delete page
  # Currently don't do anything with page text
}

# Given text, returns substituted text
sub SubstituteTextLinks {
  my ($old, $new, $text) = @_;

  # Much of this is taken from the common markup
  %SaveUrl = ();
  $SaveUrlIndex = 0;
  $text =~ s/$FS//g;              # Remove separators (paranoia)
  if ($RawHtml) {
    $text =~ s/(<html>((.|\n)*?)<\/html>)/&StoreRaw($1)/ige;
  }
  $text =~ s/(<pre>((.|\n)*?)<\/pre>)/&StoreRaw($1)/ige;
  $text =~ s/(<code>((.|\n)*?)<\/code>)/&StoreRaw($1)/ige;
  $text =~ s/(<perl>((.|\n)*?)<\/perl>)/&StorePerl($1)/ige;
  $text =~ s/(<boxes>((.|\n)*?)<\/boxes>)/&StoreBoxes($1)/smige;
  $text =~ s/(<tests>((.|\n)*?)<\/tests>)/&StoreTests($1)/smige;
  $text =~ s/(<projects>((.|\n)*?)<\/projects>)/&StoreProjects($1)/smige;
  $text =~ s/(<outline>((.|\n)*?)<\/outline>)/&StoreOutline($1,"bullets")/smige;
  $text =~ s/(<outline-head>((.|\n)*?)<\/outline>)/&StoreOutline($1,"headers")/smige;
  $text =~ s/(<outline-todo>((.|\n)*?)<\/outline>)/&StoreOutline($1,"todo")/smige;
  $text =~ s/(<components>((.|\n)*?)<\/components>)/&StoreComponents($1)/smige;
  $text =~ s/(<nowiki>((.|\n)*?)<\/nowiki>)/&StoreRaw($1)/ige;

  if ($FreeLinks) {
    $text =~
     s/\[\[$FreeLinkPattern\|([^\]]+)\]\]/&SubFreeLink($1,$2,$old,$new)/geo;
    $text =~ s/\[\[$FreeLinkPattern\]\]/&SubFreeLink($1,"",$old,$new)/geo;
  }
  if ($BracketText) {  # Links like [URL text of link]
    $text =~ s/(\[$UrlPattern\s+([^\]]+?)\])/&StoreRaw($1)/geo;
    $text =~ s/(\[$InterLinkPattern\s+([^\]]+?)\])/&StoreRaw($1)/geo;
  }
  $text =~ s/(\[?$UrlPattern\]?)/&StoreRaw($1)/geo;
  $text =~ s/(\[?$InterLinkPattern\]?)/&StoreRaw($1)/geo;
  if ($WikiLinks) {
    $text =~ s/$LinkPattern/&SubWikiLink($1, $old, $new)/geo;
  }

  $text =~ s/$FS(\d+)$FS/$SaveUrl{$1}/geo;  # Restore saved text
  return $text;
}

sub SubFreeLink {
  my ($link, $name, $old, $new) = @_;
  my ($oldlink);

  $oldlink = $link;
  $link =~ s/^\s+//;
  $link =~ s/\s+$//;
  if ($link eq $old) {
    $link = $new;
  } else {
    $link = $oldlink;  # Preserve spaces if no match
  }
  $link = "[[$link";
  if ($name ne "") {
    $link .= "|$name";
  }
  $link .= "]]";
  return &StoreRaw($link);
}

sub SubWikiLink {
  my ($link, $old, $new) = @_;
  my ($newBracket);

  $newBracket = 0;
  if ($link eq $old) {
    $link = $new;
    if (!($new =~ /^$LinkPattern$/o)) {
      $link = "[[$link]]";
    }
  }
  return &StoreRaw($link);
}

# Rename is mostly copied from expire
sub RenameKeepText {
  my ($page, $old, $new) = @_;
  my ($fname, $status, $data, @kplist, %tempSection, $changed);
  my ($sectName, $newText);

  $fname = fold_to_lowercase($KeepDir . "/" . &GetPageDirectory($page) .  "/$page.kp");
  return  if (!(-f $fname));
  ($status, $data) = &ReadFile($fname);
  return  if (!$status);
  @kplist = split(/$FS1/o, $data, -1);  # -1 keeps trailing null fields
  return  if (length(@kplist) < 1);  # Also empty
  shift(@kplist)  if ($kplist[0] eq "");  # First can be empty
  return  if (length(@kplist) < 1);  # Also empty
  %tempSection = split(/$FS2/o, $kplist[0], -1);
  if (!defined($tempSection{'keepts'})) {
    return;
  }

  # First pass: optimize for nothing changed
  $changed = 0;
  foreach (@kplist) {
    %tempSection = split(/$FS2/o, $_, -1);
    $sectName = $tempSection{'name'};
    if ($sectName =~ /^(text_)/) {
      %Text = split(/$FS3/o, $tempSection{'data'}, -1);
      $newText = &SubstituteTextLinks($old, $new, $Text{'text'});
      $changed = 1  if ($Text{'text'} ne $newText);
    }
    # Later add other section types? (maybe)
  }

  return  if (!$changed);  # No sections changed
  open (OUT, ">$fname") or return;
  foreach (@kplist) {
    %tempSection = split(/$FS2/o, $_, -1);
    $sectName = $tempSection{'name'};
    if ($sectName =~ /^(text_)/) {
      %Text = split(/$FS3/o, $tempSection{'data'}, -1);
      $newText = &SubstituteTextLinks($old, $new, $Text{'text'});
      $Text{'text'} = $newText;
      $tempSection{'data'} = join($FS3, %Text);
      print OUT $FS1, join($FS2, %tempSection);
    } else {
      print OUT $FS1, $_;
    }
  }
  close(OUT);
}

sub RenameTextLinks {
  my ($old, $new) = @_;
  my ($changed, $file, $page, $section, $oldText, $newText, $status);

  $old =~ s/ /_/g;
  $new =~ s/ /_/g;
  $status = &ValidId($old);
  if ($status ne "") {
    print "Rename-Text: old page $old is invalid, error is: $status<br>\n";
    return;
  }
  $status = &ValidId($new);
  if ($status ne "") {
    print "Rename-Text: new page $new is invalid, error is: $status<br>\n";
    return;
  }
  $old =~ s/_/ /g;
  $new =~ s/_/ /g;

  foreach $page (&AllPagesList()) {
    $changed = 0;
    &OpenPage($page);
    foreach $section (keys %Page) {
      if ($section =~ /^text_/) {
        &OpenSection($section);
        %Text = split(/$FS3/o, $Section{'data'}, -1);
        $oldText = $Text{'text'};
        $newText = &SubstituteTextLinks($old, $new, $oldText);
        if ($oldText ne $newText) {
          $Text{'text'} = $newText;
          $Section{'data'} = join($FS3, %Text);
          $Page{$section} = join($FS2, %Section);
          $changed = 1;
        }
      } elsif ($section =~ /^cache_diff/) {
        $oldText = $Page{$section};
        $newText = &SubstituteTextLinks($old, $new, $oldText);
        if ($oldText ne $newText) {
          $Page{$section} = $newText;
          $changed = 1;
        }
      }
      # Later: add other text-sections (categories) here
    }
    if ($changed) {
      $file = &GetPageFile($page);
      &WriteStringToFile($file, join($FS1, %Page));
    }
    &RenameKeepText($page, $old, $new);
  }
}

sub RenamePage {
  my ($old, $new, $doRC, $doText) = @_;
  my ($oldfname, $newfname, $oldkeep, $newkeep, $status);

  $old =~ s/ /_/g;
  $new =~ s/ /_/g;
  $new = ucfirst($new);
  $status = &ValidId($old);
  if ($status ne "") {
    print "Rename: old page $old is invalid, error is: $status<br>\n";
    return;
  }
  $status = &ValidId($new);
  if ($status ne "") {
    print "Rename: new page $new is invalid, error is: $status<br>\n";
    return;
  }
  $newfname = &GetPageFile($new);
  if (-f $newfname) {
    print "Rename: new page $new already exists--not renamed.<br>\n";
    return;
  }
  $oldfname = &GetPageFile($old);
  if (!(-f $oldfname)) {
    print "Rename: old page $old does not exist--nothing done.<br>\n";
    return;
  }

  &CreatePageDir($PageDir, $new);  # It might not exist yet
  rename($oldfname, $newfname);
  &CreatePageDir($KeepDir, $new);
  $oldkeep = fold_to_lowercase($KeepDir . "/" . &GetPageDirectory($old) .  "/$old.kp");
  $newkeep = fold_to_lowercase($KeepDir . "/" . &GetPageDirectory($new) .  "/$new.kp");
  unlink($newkeep)  if (-f $newkeep);  # Clean up if needed.
  rename($oldkeep,  $newkeep);
  unlink($IndexFile)  if ($UseIndex);
  &EditRecentChanges(2, $old, $new)  if ($doRC);
  &RenameTextLinks($old, $new)  if ($doText);
}
#END_OF_OTHER_CODE

&DoWikiRequest();   # Do everything.

# == End of UseModWiki script. ==========================================(duh)=
