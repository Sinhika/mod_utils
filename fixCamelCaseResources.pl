#!/usr/bin/perl

=head1 NAME

fixCamelCaseResources.pl - fix camelcase names in old lang files.

=head1 SYNOPSIS

fixCamelCaseResources.pl  I<input_file>

=head1 DESCRIPTION

Change camelcase resource names to snake_case in old lang files before
using tterag's web converter to convert to JSON lang files. Writes to
stdout.

=head1 METADATA

 Revision: $Id$
 Created: 2020-Dec-27
 Programmer: Sinhika

=cut

use strict;
use warnings;

#global variables
my $VERSION = "1.0.0";

my $input_file = $ARGV[0];
open(my $fh, "<", $input_file) or die "Can't open ${input_file}: $!";

my ($prefix, $tok, $rest);

while (<$fh>)
{
    chomp;

    # tab group
    if (/itemGroup\.(\w*[A-Z]\w*+)=(.+)/) 
    {
        $tok = $1;
        $rest = $2;
        $tok =~ s/([A-Z])/'_' . lc($1)/ge;
        print "itemGroup.${tok}=${rest}\n";
    }
    elsif (/(\w+?)\.(\w*[A-Z]\w*)\.name=(.+)/)
    {
        $prefix = $1;
        $tok = $2;
        $rest = $3;
        $tok =~ s/([A-Z])/'_' . lc($1)/ge;
        print "${prefix}.${tok}.name=${rest}\n";
    }
    else {
        print $_, "\n";
    }
} ## end-while

close $fh;
