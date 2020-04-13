#!/usr/bin/perl
#
=head1 NAME
    
gen_blockstate_jsons.pl - create a blockstate json.

=head1 SYNOPSIS

gen_blockstate_jsons.pl modid [topdir]

=over

=item modid

mandatory modid tag; to be prefixed to various entries.

=item topdir

Optional root directory for output jsons-usually the assets/modid/ 
directory. Uses current working directory if not specified.

=back

=head1 DESCRIPTION

Create a blockstate json for B<modid> by following a set of prompts
for name, type, etc.  Split out from the old build_graphic_jsons.pl
script and updated.

=cut

use strict;
use warnings;

use Cwd;
use File::Spec;
use File::Copy;
use File::Path qw(make_path);
use List::MoreUtils qw(uniq);

use FindBin;
use lib "$FindBin::Bin";
use generator;

# output directory is...
my $TOP_LEVEL = defined($ARGV[1]) ? $ARGV[1] : getcwd();
my $BLOCKSTATE_PATH = "${TOP_LEVEL}/blockstates";
my $BLOCK_MODEL_PATH = "${TOP_LEVEL}/models/block";
my $ITEM_MODEL_PATH = "${TOP_LEVEL}/models/item";

my $MODID = $ARGV[0];

my $verbose = 1;

die "modid is required!" if ! defined($MODID);

# create if they do not exist.
make_path($BLOCKSTATE_PATH, $BLOCK_MODEL_PATH, $ITEM_MODEL_PATH);

# go there
chdir $TOP_LEVEL or die "Unable to change to ${TOP_LEVEL}: $!\n";

my $resp;
my $block_subtype = 0;
my $bs_template;
my $block_template;

print "Generic block (G;default), crop block (C), ",
        "Face block [like pumpkin] (F), pillar/log block (P), ",
        "Bars [like iron_bars] (B), Doors (D), ", 
        "Thin pane [like glass] (T), Stairs (S) ? ";
$resp = <STDIN>;
$block_subtype = ($resp =~ /^[GCFPBTSD]/i) ? uc(substr($resp,0,1)) : 'G'

if ($verbose) {
    print "\$block_subtype = ", $block_subtype, "\n";
}

get_block_info($block_subtype);

exit;

=head1 FUNCTIONS

=over

=item get_block_info

=cut

sub get_block_info
{
    my $block_type = $_[0];
    my $resp;
    my $prompt;
    my $block_stem;
    my ($template_json, $template_model, $template_texture);
    my $templ_model_stem;
    my @out_jsons;
    my ($out_model_stem, $out_texture);
    my $not_done = 1;
    
    if ($block_type eq 'G')  # generic cube block
    {
        while ($not_done)
        {
            $prompt = "Name of block to create blockstate for (e.g. foo_block): ";
            @out_jsons = get_simple_json_path($prompt, $BLOCKSTATE_PATH);
            write_cubeall_blockstate($MODID, @out_jsons);
            $not_done = check_repeat("Create another simple cube [Y/N]? ");
        } ## end while not_done 
    } 
    else 
    {
        ## TODO
    }
} ## end sub get_block_info


=item write_cubeall_blockstate

write a standard Forge blockstate for a stock cube_all model block.

=cut

sub write_cubeall_blockstate
{
    my ($modid, $name, $out_json) = @_;
    open (my $fh, ">", $out_json) or die "Unable to open ${out_json}: $!";
    print $fh "{\n";
    print $fh "\t\"variants\": {\n";
    print $fh "\t\t\"\": { \"model\": \"${modid}:block/${name}\" }\n";
    print $fh "\t}\n";
    print $fh "}\n";
    close $fh;
} ## end write_cubeall_blockstate()


=back

=head1 HISTORY

=cut

