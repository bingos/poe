# -*- perl -*-
# $Id$

package Whip::Tag::tabloid;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub get_syntax {
  ( column => LIST | REQ,
  )
}

sub close {
  my ($self, $columns) = @_;

  my $col_percent = int(100 / @$columns);

  my $tabloid =
    ( "<table cellpadding='0' cellspacing='8' border='0' width='100%'>" .
      "<tbody>" .
      "<tr>"
    );

  foreach (@$columns) {
    $tabloid .= "<td valign='top' width='$col_percent%'>$_</td>";
  }

  $tabloid .=
    ( "</td>" .
      "</tr>" .
      "<tr>" .
      "</tbody>" .
      "</table>"
    );

  $self->emit(widget => $tabloid);
}

1;
