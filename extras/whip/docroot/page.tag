# -*- perl -*-
# $Id$

package Whip::Tag::page;
use warnings;
use strict;
use Whip::Tag qw(widget);

sub open {
  my $self = shift;

  $self->set_subtags
    ( { title => ONE,
        status => ONE,
        widget => STAR,
      },
    );
}

sub close {
  my $self = shift;

  my @widget = $self->fetch("widget");
  my $title  = $self->fetch("title", "Untitled...");
  my $status = $self->fetch("status", 200);

  use CGI qw(:standard);

  print( header(-status => $status),
         start_html($title),
         join("", @widget),
       );
}

1;
