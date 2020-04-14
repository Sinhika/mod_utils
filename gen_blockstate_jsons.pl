#!/usr/bin/perl

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
make_path($BLOCKSTATE_PATH);

# go there
chdir $TOP_LEVEL or die "Unable to change to ${TOP_LEVEL}: $!\n";

my $resp;
my $block_subtype = 0;
my $bs_template;
my $block_template;
my $not_done = 1;

while ($not_done)
{
    print "Generic simple block (G;default), ",
        "crop block [has growth stages] (C), ",
        "Simple block with facing [like oak_log] (F), ",
        "Bars [like iron_bars] (B), Doors (D), ", 
        "Thin pane [like glass] (T), Stairs (S), Other (O) ? ";
    $resp = <STDIN>;
    $block_subtype = ($resp =~ /^[GCFBTSDO]/i) ? uc(substr($resp,0,1)) : 'G';

    if ($verbose) {
        print "\$block_subtype = ", $block_subtype, "\n";
    }

    get_block_info($block_subtype);
    $not_done = check_repeat("Create another blockstate [Y/N]? ");
} ## end-while not_done

exit;

=head1 FUNCTIONS

=over

=item B<get_block_info>

Actually does most of the work of this script. 
=cut

sub get_block_info
{
    my $block_type = $_[0];
    my $prompt;
    my $templ_model_stem;
    my $not_done = 1;
    
    if ($block_type eq 'G')  # simple generic cube block
    {
        my @out_jsons;
        while ($not_done)
        {
            $prompt = "Name of block to create blockstate for (e.g. foo_block): ";
            @out_jsons = get_simple_json_path($prompt, $BLOCKSTATE_PATH);
            write_cubeall_blockstate($MODID, @out_jsons);
            $not_done = check_repeat("Create another simple cube [Y/N]? ");
        } ## end while not_done 
    } ## end-if simple cube
    elsif ($block_type eq 'F')  # simple block with horizontal facing
    {
        make_blockstate_prompts('oak_log');
    } ## end-elsif 'F'            
    elsif ($block_type eq 'C') # crop block (has growth stages).
    {
        make_blockstate_prompts('carrots');
    }
    elsif ($block_type eq 'B') # metal bars
    {
        make_blockstate_prompts('iron_bars');
    }
    elsif ($block_type eq 'S') # stairs
    {
        make_blockstate_prompts('oak_stairs');
    }
    elsif ($block_type eq 'D') #doors
    {
        make_blockstate_prompts('oak_door');
    }
    elsif ($block_type eq 'T') #thin pane
    {
        make_blockstate_prompts('glass_pane');
    }
    else # not a simple anything 
    {
        $prompt = "Vanilla block to use as template (e.g. acacia_fence): ";
        my $block_stem = get_response($prompt);
        make_blockstate_prompts($block_stem);
    } ## end-else not a simple cube
} ## end sub get_block_info


=item B<make_blockstate_prompts>

Bundles up a bunch of repetitive, common code for making blockstates.

=cut

sub make_blockstate_prompts
{
    my ($block_stem, ) = @_;

    my $not_done = 1;
    my $template_json = get_template($block_stem, $MC_BLOCKSTATE_PATH);
    die if ! defined $template_json;
    print("Source blockstate: ", $template_json, "\n") if $verbose;
    while ($not_done)
    {
        my $prompt = "Name of block to create files for (e.g. foo_gourd): ";
        my @out_jsons = get_simple_json_path($prompt, $BLOCKSTATE_PATH);
        print("Target blockstate: ", $out_jsons[1], "\n") if $verbose;
        my $out_model_stem = $out_jsons[0];
        printf("Target block stem to replace %s with: %s\n", 
                $block_stem, $out_model_stem) if $verbose;

        # write blockstate file
        copy_blockstate($template_json, $block_stem, $out_jsons[1],
                        $out_model_stem);
        # repeat?
        $not_done = check_repeat(
                    "Create another block from the same template [Y/N]? ");
    } ## end while not_done 

} ## end sub make_blockstate_prompts


=item B<write_cubeall_blockstate>

write a standard Forge blockstate for a stock model block.

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


=item B<copy_blockstate>

Copies from one blockstate to another, substituting the block name
stem C<$out_mstem> for C<$in_mstem>, and prefixing the modid.

Parameters:
    
    $in_json - full path to source blockstate json.
    $in_mstem - block name stem to be replaced.
    $out_json - full path to target blockstate json.
    out_mstem - block name stem to replace $in_mstem with.

=cut

sub copy_blockstate
{
    my ($in_json, $in_mstem, $out_json, $out_mstem ) = @_;
    open (my $fh, "<", $in_json) or die "Unable to open ${in_json}: $!";
    open (my $fh2, ">", $out_json) or die "Unable to open ${out_json}: $!";
    while (my $line = <$fh>)
    {
        $line =~ s/block\/${in_mstem}/${MODID}:block\/${out_mstem}/;
        print $fh2 $line;
    }
    close $fh;
    close $fh2;
} ## end copy_blockstate()


=back

=head1 HISTORY

=cut

