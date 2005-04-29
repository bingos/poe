#!/usr/bin/perl
# $Header$

=head1 NAME

index.cgi - POE test server framework

=head1 AUTHOR

Matt Cashner (sungo+poe@eekeek.org)

=head1 DATE 

$Date$

=head1 REVISION

$Revision$

=head1 DESCRIPTION

POE ships with a set of scripts to generate XML reports from the output
of the test suite. This server framework displays various reports from
that data.  

All the data is uploaded through this CGI and dumped in a local folder.
At startup, this data is read in and parsed so reports can be generated.
If the XML is invalid, the report is deleted.

=head1 ACTIONS

=cut

use warnings;
use strict;

use lib qw(/home/sungo/perl5/local/share/perl/5.6.1);
use XML::Simple;
use CGI_Lite;
my (%tests,%poe);
my $cgi = CGI_Lite->new();

# Correct line feed for unix and give us the file data as a filehandle
$cgi->set_platform('unix');
$cgi->set_file_type('handle');

# set up the location of the test result files. 
# This path should probably not be in a place that's generally
# accessible to your apache instance.
my $test_dir = '/home/sungo/eekeek.org/poe-tests/';

unless(-d $test_dir) {
    die "$test_dir does not exist or is not a directory";
}

# Test report parsing {{{

local $/;
foreach my $test (sort <$test_dir/*.xml>) {
    open IN, $test;
    my $xml = <IN>;
    close IN;

    my ($name) = $test =~ m#^$test_dir/(.+?)$#;
    eval {
        $tests{$name} = XMLin($xml);
    };
    if($@) {
        warn "BAD TEST REPORT ($test): $@";
        unlink $test;
    } else {
        $tests{$name}->{uniquename} = $name;
        push (@{ $poe{ $tests{$name}{system}{perl_modules}{poe}{version} } }, $tests{$name});
    }
}
# }}}

# Check which action to perform - otherwise do the default {{{

my %actions = (
    default => \&summary,
    summary => \&summary,
    detail => \&detail,
    upload => \&upload,
    view => \&view,
);


print "Content-type: text/html\n\n";
my $form = $cgi->parse_form_data;
if(defined $form->{action}) {
    if(defined($actions{$form->{action}})) {
        print $actions{$form->{action}}->();
    } else {
        print $actions{default}->();
    }
} else {
    print $actions{default}->();
}
# }}} 

#####################################################

# view() - view an individual test report {{{ 

=head2 view

View an individual test report. Takes one form parameter, C<name> which
is the name of an individual unique test. Unexpected or missing input
will merely dump out the default view.

=cut

sub view {
    my $html;
    if($form->{name}) { 
        if(defined $tests{$form->{name}}) {
            $html .= q|
<html>
    <head><title>POE Tests</title></head>
    <body>
|;
            $html .= _generate_ind_test($tests{$form->{name}});
            $html .= '</body></html>';
            return $html;
        } else {
            return $actions{default}->();
        }
    } else {
        return $actions{default}->();
    }

}
#}}}

# _generate_ind_test() - generate the html for an individual test report {{{

sub _generate_ind_test ($) {
    my $test = shift;
    my $html;
    $html .= qq|
            <table width='100%' border='1' cellpadding='2' cellspacing='0'>
                <tr>
                    <th align="center" colspan="2" bgcolor="#ADADAD">$test->{generatedby}{hostname} - $test->{generatedby}->{username} - $test->{generatedby}->{time}</th>
                </tr>
                <tr>
                    <th align="center" colspan="2" bgcolor="#CFCFCF">$test->{system}->{machine}->{sysname} : $test->{system}->{machine}->{release} : $test->{system}->{machine}->{machine}</th>
                </tr>
                <tr>
                    <th align="center" bgcolor="#e1e1e1">Test Data</th>
                    <th align="center" bgcolor="#e1e1e1">Perl Data</th>
                </tr>
                <tr>
                    <td width="75%" valign="top"><font size="-1">
    |; 
        
    my $testcount = scalar @{$test->{tests}{test}};
    foreach my $report (@{$test->{tests}{test}}) {
        $report->{skip} ||=0;
        $report->{todo} ||=0;
        $report->{ok} ||=0; 
        $report->{expected} ||= 0;
        if(($report->{ok} - $report->{skip} - $report->{todo}) == $report->{expected}) {
            $testcount--;
        } else {
            $html .= "<b>$report->{filename}</b><ul>";
            if(defined $report->{skip_all}) {
                $html .= "<li>SKIPPED - $report->{skip_all}</li>";
            } else {   
                if($report->{todo}) {
                    $html .= "<li>Todo: $report->{todo}</li>";
                }
                my $fail = $report->{expected}-$report->{ok};
                if($fail && defined $report->{failing}) {
                    $html .= "<li><font color='red'>Failing:</font><ul>";
                    if(ref $report->{failing}{test} eq 'ARRAY') {
                        foreach my $fail (@{$report->{failing}{test}}) {
                            $html .= "<li>#$fail->{num}";
                            $html .= " - $fail->{reason}" if $fail->{reason};
                            $html .= "</li>";
                        }
                    } else {
                        $html .= "<li>#$report->{failing}{test}{num}";
                        $html .= " - $report->{failing}{test}{reason}" if $report->{failing}{test}{reason};
                        $html .= "</li>";
                    }
                    $html .= "</ul></li>";
                }
            }
            if($report->{skipped}{test}) {
                $html .= "<li><i>Skipped:</i><ul>";
                if(ref $report->{skipped}{test} eq 'ARRAY') {
                    foreach my $skipped (@{$report->{skipped}{test}}) {
                        $html .= "<li>#$skipped->{num}";
                        $html .= " - $skipped->{reason}" if $skipped->{reason};
                        $html .= "</li>";
                    }
                } elsif($report->{skipped}{test}) {
                    $html .= "<li>#$report->{skipped}{test}{num}";
                    $html .= " - $report->{skipped}{test}{reason}" if $report->{skipped}{test}{reason};
                    $html .= "</li>";
                }
                $html .= "</ul></li>";
            } elsif ($report->{skip}) {
                $html .= "<li><i>Skipped: $report->{skip}</i></li>";
            }
            $html .= "</ul></li>";
        }
    }
    if($testcount == 0) {
        $html .= "<b>All Tests Passed</b>";
    }
    $html .= "</font></td><td width='25%' valign='top'><font size='-1'>";
    $html .= "<table border='0' cellspacing='0' cellpadding='0' width='100%'><tr><td><b>Event</b></td><td>";
    $html .= ($test->{system}{perl_modules}{event}{version} || 'N/A')."</td></tr><tr><td><b>Gtk</b></td><td>";
    $html .= ($test->{system}{perl_modules}{gtk}{version} || 'N/A')."</td></tr><tr><td><b>IO::Pty</b></td><td>";
    $html .= ($test->{system}{perl_modules}{iotty}{version} || 'N/A')."</td></tr><tr><td><b>Perl</b></td><td>";
    $html .= "$test->{system}{perl_modules}{perl}{version}</td></tr><tr><td><b>Tk</b></td><td>";
    $html .= ($test->{system}{perl_modules}{tk}{version} || 'N/A')."</td></tr>";
    $html .= "</table>";

    $html .= "</font></td></tr></table><br><br>";

    return $html;
}
# }}}

# upload() - upload a test report [ both from the form and via the nifty upload script ] {{{

=head2 upload

Upload a test report. Takes one form parameter, C<reportfile>, which is
the multipart/form-data of the XML report file. A unique descriptor is
generated based off the system name and type as well as the versions of
various important perl modules found on the system. If a test matching
this descriptor already exists, the old test is overwritten with the new
one.  If the incoming file does not parse as valid XML or is missing
information, it is rejected.

=cut
    
sub upload {
    my $file_handle = $form->{reportfile};
    unless($file_handle) {
        warn "no filehandle";
        return $actions{default}->();
    }
    local $/;
    my $data = <$file_handle>;
    $cgi->close_all_files;
    unless($data) {
        warn "no data";
        return $actions{default}->() 
    };

    my $struct;
    eval { $struct = XMLin($data); };
    if($@) { warn "Error parsing incoming data: $@"; return $actions{default}->() }
    
    my $key = $struct->{system}{machine}{sysname} .
                $struct->{system}{machine}{release} .
                $struct->{system}{machine}{machine} .
                $struct->{system}{perl_modules}{perl}{version} .
                $struct->{system}{perl_modules}{poe}{version} .
                ($struct->{system}{perl_modules}{gtk}{version} || 0) .
                ($struct->{system}{perl_modules}{tk}{version} || 0) .
                ($struct->{system}{perl_modules}{event}{version} || 0) .
                ($struct->{system}{perl_modules}{iotty}{version} || 0);
    $key = lc($key);
    $key =~ s#[\s\./\;]*##gs;

    open OUT,"+>$test_dir/$key.xml";
    print OUT $data;
    close OUT;

    my $html = <<EOF;
<html>
    <head><title>POE Tests</title></head>
    <body>
        <h1>Test Submission</h1>
        <p>Thank you for your submission.</p>
        <p>Only one test report from each unique system type is kept. Older reports are dropped in favor of newer reports. Uniqueness is determined from operating system type, version, and architecture as well as the version of perl run and the versions of the various modules the tests depend on.</p>
        <p>Click <a href="?action=summary">here</a> to return to test summaries.</p>
    </body>
</html>
EOF
    return $html;
}
# }}}

# detail() - show the detailed results for a specific version of POE {{{

=head2 detail

Show the detailed results for a specific version of POE. Takes one form
parameter, C<version> which is the version of POE to display the results
for. Unexpected or missing data causes the default action to be used.

=cut
    
sub detail {
    unless(defined $form->{version}) {
        return $actions{default}->();
    }
    my $html = <<EOF;
<html>
    <head><title>POE Tests</title></head>
    <body>
        <h1>Detailed Results for POE v$form->{version}</h1>
        <ul>
EOF

    foreach my $test (@{ $poe{ $form->{version} } }) { # spacing necessary to trick out the code fold mojo
        $html .= _generate_ind_test($test);
    }
    $html .= "</body></html>";
    return $html;
}
# }}}

# summary() - display the summarized results of all the tests for all the versions {{{

=head2 summary

Display the summarized results of all the tests for all the versions of
POE. Takes no form parameters. This is the default action.

=cut
    
sub summary {
    my $html = <<EOF;
<html>
    <head><title>POE Tests</title></head>
    <body>
        <h1>POE Test Results</h1>
        <p><form method="POST" action="#" enctype="multipart/form-data"><input type="hidden" name="action" value="upload">Upload Test Report <input size="30" name="reportfile" type="file"><input type="Submit" value="Send"></form></p>
EOF
    foreach my $poever (sort { $b cmp $a } keys %poe) {
    $html .= qq|
    <p>
        <table width="100%" border="1" cellspacing="0" cellpadding="2">
        <tr>
        <th align="center" colspan="7" bgcolor="#ADADAD">Test Results For $poever [ <a href="?action=detail&version=$poever">detail</a> ]</th>
        </tr>
        <tr>
            <th align="center" colspan="3" bgcolor="#cfcfcf">System Type</th>
            <th align="center" rowspan="2" bgcolor="#cfcfcf">Perl Version</th>
            <th align="center" rowspan="2" bgcolor="#cfcfcf">Passed</th>
            <th align="center" rowspan="2" bgcolor="#cfcfcf">Failed</th>
            <th align="center" rowspan="2" bgcolor="#cfcfcf">Skipped</th>
        </tr>
        <tr>
            <th align="center" bgcolor="#e1e1e1">Name</th>
            <th align="center" bgcolor="#e1e1e1">Release</th>
            <th align="center" bgcolor="#e1e1e1">Machine</th>
        </tr>
    |;

        foreach my $test (@{$poe{$poever}}) {
            $html .= "<tr>";
            $html .= "<td><a href='?action=view&name=$test->{uniquename}'>$test->{system}{machine}{sysname}</a></td>";
            $html .= "<td>$test->{system}{machine}{release}</td>";
            $html .= "<td>$test->{system}{machine}{machine}</td>";
            $html .= "<td>$test->{system}{perl_modules}{perl}{version}</td>";

            my ($run, $failed, $skip);
            foreach my $indtest (@{$test->{tests}{test}}) {
                $run += $indtest->{seen} if $indtest->{seen};
                $skip += $indtest->{skip} if $indtest->{skip}; 
                if($indtest->{failing}{test}) {
                    if(ref $indtest->{failing}{test} eq 'ARRAY') {
                        $failed += scalar @{$indtest->{failing}{test}};
                    } elsif (ref $indtest->{failing}{test}) {
                        next;
                    } else { 
                        $failed += 1;
                    }
                }
            }
            $skip ||= 0;
            $failed ||= 0;
            my ($fail_color, $skip_color) = ('#ccffcc','#ccffcc');
            $fail_color = '#ffcccc' if $failed;
            $skip_color = '#ffffcc' if $skip;
            $html .= "<td bgcolor='#ccffcc'>$run</td><td bgcolor='$fail_color'>$failed</td><td bgcolor='$skip_color'>$skip</td>";
            $html .= "</tr>";
        }
        $html .= "</table><br><br><br>"
    }

    $html .="</body></html>";
    return $html;
}
# }}}

=head1 LICENSE

Copyright (c) 2002, Matt Cashner 

Permission is hereby granted, free of charge, to any person obtaining 
a copy of this software and associated documentation files (the 
"Software"), to deal in the Software without restriction, including 
without limitation the rights to use, copy, modify, merge, publish, 
distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject 
to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=cut
