# -*- perl -*-
# $Id$

package Whip::Tag::pane;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub open {
  my $self = shift;

  $self->set_subtags
    ( { title => ONE,
        color => ONE,
        item  => STAR,
      },
    );
}

sub close {
  my $self = shift;

  my $color = $self->fetch("color", "#666666");
  my $title = $self->fetch("title", "Untitled");
  my @items = $self->fetch("item");

  $self->replace_contents
    ( widget =>
      ( "<table cellpadding='2' cellspacing='3' border='0' width='100%' " .
        "bgcolor='$color'>" .
        "<tbody>" .
        "<tr>" .
        "<td valign='top'><font color='#ffffff'><b>$title</b></font>" .
        "</td>" .
        "</tr>" .
        "<tr>" .
        "<td valign='top' bgcolor='#ffffff'>" .
        join("<br>", @items) .
        "</td>" .
        "</tr>" .
        "</tbody>" .
        "</table>"
      )
    );
}

1;
