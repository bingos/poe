# $Id$
# Copyrights and documentation are at the end.

package POE::Queue;

use strict;

# This is an abstract virtual base class for POE queue objects It
# choses implmentation at runtime

sub new {
  my ($class, $implementation) = @_;

  no strict 'refs';
  $class = "${class}::$implementation";
  eval "use $class";
  die if $@;

  return $class->new();
}

1;

__END__

=head1 NAME

POE::Queue - a virtual base class for POE queue objects

=head1 SYNOPSIS

To do.

=head1 DESCRIPTION

To do.

=head1 SEE ALSO

To do.

=head1 BUGS

To do.

=head1 AUTHORS & COPYRIGHT

POE::Queue is contributed by Artur Bergman.

Please see L<POE> for more information about authors and contributors.

=cut
