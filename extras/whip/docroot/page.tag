# -*- perl -*-
# $Id$

package Whip::Tag::page;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub get_syntax {
  ( title  => [ SCALAR, "Untitled" ],
    status => [ SCALAR, 200 ],
    widget => [ LIST, "<h1>Empty</h1><p>This page is empty.</p>" ],
  )
}

sub close {
  my ($self, $title, $status, $widget) = @_;

  $self->emit_document
    ( status => $status,
      title  => $title,
      body   => join("", @$widget)
    );
}

1;
