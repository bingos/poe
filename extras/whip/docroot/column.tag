# -*- perl -*-
# $Id$

package Whip::Tag::column;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub get_syntax {
  ( widget => [ LIST, "This column is empty." ],
  )
}

sub close {
  my ($self, $widgets) = @_;
  $self->emit(column => join("<br>", @$widgets));
}

1;
