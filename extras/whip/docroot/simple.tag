# -*- perl -*-
# $Id$

package Whip::Tag::simple;
use warnings;
use strict;
use Whip::Tag;
use base qw(Whip::Tag);

sub open {
  my $self = shift;
  $self->set_subtags
    ( { text => STAR,
      }
    );
}

sub close {
  my $self = shift;
  my @text = $self->fetch("text", "");
  $self->replace_contents($self->name(), join(" ", @text));
}

1;
