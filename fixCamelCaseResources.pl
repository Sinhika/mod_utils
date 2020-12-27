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

my $input_file = $ARGV[1];
open(my $fh, "<", $input_file) or die "Can't open ${input_file}: $!";

while <$fh>
{
    # tab group
    if (/itemGroup\.(\w*[A-Z]\w*+)=(.+)/) 
    {
        my $tok = $1;
        my $rest = $2;
        $tok =~ s/([A-Z])/'_' . lc($1)/ge;
        print "itemGroup.${tok}=${rest}\n";
    }

} ## end-while

close $fh;
