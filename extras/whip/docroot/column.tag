# -*- perl -*-
# $Id$

package Whip::Tag::column;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub open {
  my $self = shift;

  $self->set_subtags
    ( { widget => STAR,
      },
    );
}

sub close {
  my $self = shift;
  my @widgets = $self->fetch("widget", "");
  $self->replace_contents("column", join("<br>", @widgets));
}

1;
