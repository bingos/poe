# -*- perl -*-
# $Id$

package Whip::Tag::simple;
use warnings;
use strict;
use Whip::Tag;
use base qw(Whip::Tag);

sub get_syntax {
  ( text => LIST | REQ,
  )
}

sub close {
  my ($self, $text) = @_;
  $self->emit($self->name(), join(" ", @$text));
}

1;
