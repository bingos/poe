#!/usr/bin/perl

use strict;
use XML::Simple;
use LWP::Simple qw(get);

my $url = 'http://search.cpan.org/search?mode=dist&format=xml&query=POE%3A%3AComponent';
my $xml = get($url);
my $tree = XMLin($xml);

foreach my $dist (sort keys %{$tree->{dist}}) {
    next unless $dist =~ /POE-Component/;
    my $info = $tree->{dist}->{$dist};
    print "Component: $dist (v$info->{version})\n";
    print "\tAuthor: $info->{author}->{link}\n";
    print "\tURL: $info->{link}\n";
    print "\tReleased on: $info->{released}\n";
    print "\tDescription: $info->{description}\n";
    print "\n";
}
