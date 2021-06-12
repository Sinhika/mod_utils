#!/usr/bin/perl

=head1 NAME

fixCamelCaseFiles.pl - fix camelcase file names in a directory.

=head1 SYNOPSIS

fixCamelCaseFiles.pl  I<directory>

=head1 DESCRIPTION

Rename camelcase filenames to snake_case filenames in I<directory>.

=head1 METADATA

 Revision: $Id$
 Created: 2021-Jun-12
 Programmer: Sinhika

=cut

use strict;
use warnings;
use File::Spec;

#global variables
my $VERSION = "1.0.0";

my $directory = $ARGV[0];

die "${directory} is not a valid directory!" if ! -d $directory;

opendir my $dh, $directory or die "Couldn't open ${directory}: $!";
my @files = grep { /^[^.]/ && -f File::Spec->catfile($directory, $_) } 
                readdir($dh);
closedir $dh;

chdir $directory;
foreach my $fname (@files)
{
    if ($fname =~ /(\w*[A-Z]\w*)/)
    {
        my $new_name = $fname;
        $new_name =~ s/([A-Z])/'_' .lc($1)/ge;
        print "Renaming ${fname} => ${new_name}\n";
        rename $fname, $new_name;
    }
} ## end-foreach
