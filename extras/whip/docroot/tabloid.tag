# -*- perl -*-
# $Id$

# Render a tabloid layout, which consists of one or more columns
# containing one or more panes.  See whip.pane for that renderer.

package Whip::Tag::tabloid;

use warnings;
use strict;

sub build_column_from_things {
  my $state = shift;
  $state->delete("column");
  $state->store(column => join("<br>", $state->fetch("_thing")));
}

my %tags =
  ( column => \&build_column_from_things,
  );

sub run {
  my ($pkg, $state) = @_;

  my $new_state = main::render_thing($state, "whip.tabloid", \%tags);

  my @columns = $new_state->fetch("column");
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

  $state->store(_output => $tabloid);
  return $state;
}

1;
