# -*- perl -*-
# $Id$

package Whip::Tag::tabloid;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub open {
  my ($self, $whip) = @_;

  $self->set_subtags
    ( { column => PLUS,
      },
    );
}

sub close {
  my $self = shift;
  my @columns = $self->fetch("column");

  my $col_percent = int(100 / @columns);

  my $tabloid =
    ( "<table cellpadding='0' cellspacing='8' border='0' width='100%'>" .
      "<tbody>" .
      "<tr>"
    );

  foreach (@columns) {
    $tabloid .=  "<td valign='top' width='$col_percent%'>$_</td>";
  }

  $tabloid .=
    ( "</td>" .
      "</tr>" .
      "<tr>" .
      "</tbody>" .
      "</table>"
    );

  $self->replace_contents("widget", $tabloid);
}

1;
