#!/usr/bin/perl
# Hacked version of the example on http://code.google.com/p/gource/wiki/GravatarExample
# Make sure the config is correct before running this!
use strict; use warnings;

# Size, in px of the image
my $size = 80;

# Set the path to the POE git repo
my $gitpath = File::Spec->catdir( $ENV{HOME}, 'othergit', 'poe' );

# store the mapping between committer => PAUSE id for gravatar lookup
# http://poe.dyndns.org/~troc/notes/authors.txt # for the info :)
# This is up-to-date as of March 16, 2010
my %author_to_pauseid = (
	'dhoss'		=> 'DHOSS',
	'immute'	=> 'IMMUTE',
	'bingosnet'	=> 'BINGOS',
	'teknikill'	=> 'XANTUS',
	'nothingmuch'	=> 'NUFFIN',
	'sungo'		=> 'SUNGO',
	'cfedde'	=> 'CFEDDE',
	'lotr'		=> 'MARTIJN',
	'root'		=> 'RCAPUTO',
	'tarrantsun'	=> undef,	# http://twitter.com/dscouch - I should add code to extract the profile pic from there, blah...
	'hachi'		=> 'HACHI',
	'bsmith'	=> 'BSMITH',
	'rcaputo'	=> 'RCAPUTO',
	'gwyn17'	=> 'GWYN',
	'troc'		=> 'RCAPUTO',
	'apocal'	=> 'APOCAL',
	'adamkennedy'	=> 'ADAMK',
	'(no author)'	=> 'RCAPUTO',
	'cwest'		=> 'CTWETEN',
);

# END OF CONFIG

use LWP::Simple qw( getstore get );
use File::Spec;

my $output_dir = File::Spec->catdir( $gitpath, 'extras', 'gource', 'avatars' );

# First of all, we move to the git path
chdir( $gitpath ) or die "Unable to chdir to '$gitpath': $!\n";
if ( ! -d $output_dir ) {
	mkdir( $output_dir ) or die "Unable to mkdir '$output_dir': $!\n";
}

# Process the git log!
open( my $gitlog, q/git log --pretty=format:"%an" |/ ) or die "Unable to read git-log: $!\n";
my %authors;

while( <$gitlog> ) {
	chomp;
	my $author = $_;
	next if $authors{$author}++;

	# skip images we have
	my $author_image_file = File::Spec->catfile( $output_dir, $author . '.png' );
	next if -e $author_image_file;

	# Look up the email address of the PAUSE id, if any?
	my $gravatar;
	if ( exists $author_to_pauseid{ $author } ) {
		# Some authors don't have a PAUSE id...
		next if ! defined $author_to_pauseid{ $author };

		# get it!
		# I hate this crap code but URI::Find::Rule seems to bomb out trying to find the gravatar URL...
		my $content = get( 'http://search.cpan.org/~' . $author_to_pauseid{ $author } );
		if ( defined $content and $content =~ m|\<img\s+src\=\"http\://www\.gravatar\.com/avatar\.php\?gravatar_id\=([^\&]+)\&| ) {
			$gravatar = $1;
		} else {
			warn "Unable to parse search.cpan.org for gravatar URL for '$author' PAUSEid: $author_to_pauseid{ $author }\n";
			next;
		}
	} else {
		warn "New committer to POE detected! Please update the mapping in this script for '$author'\n";
		next;
	}

	# Fetch the image!
	my $grav_url = "http://www.gravatar.com/avatar.php?gravatar_id=$gravatar&d=404&size=" . $size;
	warn "Fetching image for '$author' ($grav_url)...\n";
	my $rc = getstore( $grav_url, $author_image_file );

	# Anything other than a 200 meant we didn't get the image
	if ( $rc != 200 ) {
		warn "PAUSE id '" . $author_to_pauseid{ $author } . "' for committer '$author' does not have a gravatar!\n";

		if ( -e $author_image_file ) {
			unlink( $author_image_file ) or die "Unable to remove '$author_image_file': $!\n";
		}
	}

	# Give our internets some rest!
	sleep 1;
}

# All done!
close $gitlog or die "Unable to close git-log: $!\n";
