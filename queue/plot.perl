#!/usr/bin/perl

use warnings;
use strict;

use Imager;
use Imager::Color;
use Imager::Plot;

open(DATA, "<benchmark.out") or die $!;

my $lo_index = ~0;
my $hi_index = 0;

my %raw_data;

while (<DATA>) {
  chomp;
  my ($index, $queue, $function, $time) = split /\t/;

  $lo_index = $index if $lo_index < $index;
  $hi_index = $index if $index > $hi_index;

  $raw_data{$function}->{$queue}->[$index] = $time;
}

my %colors = (Array => "red", PriorityHeap => "blue");
my $colors = join("; ", map { "$_=$colors{$_}" } sort(keys %colors));

foreach my $magnitude ($hi_index) {
  my @x = $lo_index .. $magnitude-1;

  foreach my $function (keys %raw_data) {

    my $plot = Imager::Plot->new
      ( Width      => 1024-40,
        Height     => 768-80,
        GlobalFont => 'gara.ttf'
      );

    $plot->{Ylabel} = 'time per operation';
    $plot->{Xlabel} = 'queue priorities';
    $plot->{Title}  = "Benchmark for `$function' ($colors)";

    foreach my $queue (keys %{$raw_data{$function}}) {
      my @y = @{$raw_data{$function}{$queue}};
      $plot->AddDataSet( X     => \@x,
                         Y     => \@y,
                         style => { line=> { color => $colors{$queue} } },
                       );
    }

    my $img = Imager->new( xsize => 1024,
                           ysize =>  768,
                         );
    $img->box( filled => 1,
               color  => 'white'
             );
    $plot->Render( Image => $img,
                   Xoff  => 40/2,
                   Yoff  => (768-80/2),
                 );

    my $filename = "$function-$magnitude.png";
    $filename =~ tr[ ][_];
    $img->write(file => $filename);
  }
}
