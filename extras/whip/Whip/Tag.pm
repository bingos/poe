# $Id$

# Whip::Tag is what all the whip tag handlers inherit from.  It
# supplies basic features for parsing and rendering tags.

package Whip::Tag;

use warnings;
use strict;

use CGI qw(escape escapeHTML);

### Move the _value of a tag into an attribute named after the tag.
### This is used by tags that augment their parent structures.

sub from_value {
  my ($state, $tag) = @_;
  $state->rename_value($tag);
}

### Wiki-parse the value.

sub wiki_value {
  my ($state, $tag) = @_;

  my $input = $state->delete("_value");
  my $output = "";

  while ( length($input) and
          $input =~ s/^(.*?)\[\s*([^\]\s]+)\s*([^\]]*)\s*\]//
        ) {
    my ($prefix, $url, $text) = ($1, $2, $3);

    $text = $url unless defined $text;
    $text = escapeHTML($text);

    $prefix = "" unless defined $prefix;

    $output .=
      ( $prefix .
        "<a href='?" . escape($url) . "'>$text</a>"
      );
  }

  $output .= $input if defined $input;

  $state->store($tag => $output);
}

1;
