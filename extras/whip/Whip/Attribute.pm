# $Id$

# Whip::Attribute is a name/value pair.  It could be a hash, but we
# store them in lists because there are potentially duplicates.

package Whip::Attribute;

use warnings;
use strict;

sub ATT_NAME () { 0 }
sub ATT_VAL  () { 1 }

sub new {
  my $package = shift;
  my ($name, $value) = @_;
  my $self = bless { $name, $value }, $package;
  return $self;
}

sub name {
  my $self = shift;
  return (keys %$self)[0];
}

sub value {
  my $self = shift;
  return (values %$self)[0];
}

1;
