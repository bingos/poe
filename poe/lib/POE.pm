# $Id$

# Copyright 1998 Rocco Caputo <troc@netrus.net>.  All rights reserved.
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Perl itself.

# Contributed portions of POE may be copyright by their respective
# contributors.  Please see `POE.pod`, `perldoc POE`, or `man POE` for
# real documentation.

package POE;

use vars qw($VERSION);

$VERSION = "0.05_03";

use strict;
use Carp;

sub import {
  my $self = shift;
  my @modules = grep(!/^(Kernel|Session)$/, @_);
  unshift @modules, qw(Kernel Session);

  my @failed;
  foreach my $module (@modules) {
    unless (eval("require POE::$module")) {
      warn $@;
      push(@failed, $module);
    }
  }

  @failed and croak "could not import qw(" . join(' ', @failed) . ")";
}

#------------------------------------------------------------------------------

sub new {
  my $type = shift;
  croak "$type is not meant to be used directly";
}

#------------------------------------------------------------------------------
1;
