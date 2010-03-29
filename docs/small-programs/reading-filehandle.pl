use strict;
use warnings;
use POE qw[Wheel::ReadWrite];

$|=1;

my $file = shift or die "Please specify a file to read\n";

POE::Session->create(
  package_states => [
    'main' => [qw(_start _input _error)],
  ],
);

$poe_kernel->run();
exit 0;

sub _start {
  open my $fh, '<', $file or die "$!\n";
  $_[HEAP]->{file} = POE::Wheel::ReadWrite->new(
    Handle => $fh,
    InputEvent => '_input',
    ErrorEvent => '_error',
  );
  return;
}

sub _input {
  my ($heap, $input, $wheel_id) = @_[HEAP, ARG0, ARG1];
  print "$input\n";
  return;
}

sub _error {
  my ($operation, $errnum, $errstr, $id) = @_[ARG0..ARG3];
  warn "Wheel $id encountered $operation error $errnum: $errstr\n";
  delete $_[HEAP]{file}; # shut down that wheel
  return;
}
