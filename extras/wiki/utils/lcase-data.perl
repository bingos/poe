#!/usr/bin/perl -w
# $Id$

# Converts page files to lowercase so that the $ForceLcaseFiles option
# works better.

use strict;
use File::Find;

# The directory where data files reside has been hardcoded to an
# inappropriate value.  Since this is a one-time program, I haven't
# bothered to make it an option.  Usage: fix it and remove the die.

my $data_dir = "/home/troc/www/htdocs/data";
die "data directory is hardcoded to $data_dir\n";

# Must be a data directory.  Try to keep people from lowercasing huge
# tracts of incorrect files.

die "directory must end in /data: $data_dir"
  unless $data_dir =~ m{/data$};

# Find by depth so that parent directories do not get renamed and
# possibly break the traversal.

finddepth( \&lowercase_files, "$data_dir/page" );
finddepth( \&lowercase_files, "$data_dir/keep" );

sub lowercase_files {

  # Skip single-character filenames.  This is not the best way to skip
  # the top-level "bucket" directories.
  return if /^.$/;

  # Don't bother if the filename already is lowercase.
  my $lcase = lc($_);
  return if $lcase eq $_;
warn $lcase;
  # If the lowercase version already exists, then there's a clash that
  # must be manually fixed.
  if (-e $lcase) {
    warn( "Mixed/lowercase filename clash needs to be fixed manually:\n",
          "\t$lcase\n",
          "\t$File::Find::fullname\n"
        );
    return;
  }

  rename($_, lc($_)) or
    warn( "Could not lowercase this file ($!):\n",
          "\t$File::Find::fullname\n"
        );
}
