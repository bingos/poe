# -*- perl -*-
# $Id$

# Render a pane (sort of like a window).  See whip.tabloid for the
# framework panes are kept in.

package Whip::Tag::pane;

use warnings;
use strict;

my %tags =
  ( title => \&Whip::Tag::from_value,
    color => \&Whip::Tag::from_value,
    item  => \&Whip::Tag::wiki_value,
  );

sub run {
  my ($pkg, $state) = @_;

  my $new_state = main::render_thing($state, "whip.pane", \%tags);

  my $color = $new_state->fetch("color", "#666666");
  my $title = $new_state->fetch("title", "Untitled");
  my @items = $new_state->fetch("item");

  $state->store
    ( _thing =>
      ( "<table cellpadding='2' cellspacing='3' border='0' width='100%' " .
        "bgcolor='$color'>" .
        "<tbody>" .
        "<tr>" .
        "<td valign='top'><font color='#ffffff'><b>$title</b></font><br> " .
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

  return $state;
}

1;
