# -*- perl -*-
# $Id$

package Whip::Tag::pane;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub get_syntax {
  ( title => [ SCALAR, "Untitled" ],
    color => [ SCALAR, "#008000" ],
    item  => LIST,
  )
}

sub close {
  my ($self, $title, $color, $items) = @_;

  $self->emit
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
        join("<br>", @$items) .
        "</td>" .
        "</tr>" .
        "</tbody>" .
        "</table>"
      )
    );
}

1;
