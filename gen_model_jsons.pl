#!/usr/bin/perl

=head1 NAME

gen_model_jsons.pl - create sets of model jsons

=head1 SYNOPSIS

gen_model_jsons.pl [B<-option1>|B<-option2>] I<arguments>

=head1 DESCRIPTION

Command-line script with prompts to create model jsons for B<modid>, 
a Minecraft 1.15 mod. Split out from the old build_graphic_jsons.pl
script and updated.

See below for options descriptions.

=head1 METADATA

 Revision: $Id$
 Created: 2020-Apr-14
 Programmer: Sinhika

=head1 OPTIONS

=over

=item modid

    mandatory modid tag; to be prefixed to various entries.

=item topdir

    Optional root directory for output jsons-usually the assets/modid/ 
    directory. Uses current working directory if not specified.

=back

=cut

use strict;
use warnings;

use Cwd;
use File::Spec;
use File::Copy;
use File::Path qw(make_path);
use FindBin;
use lib "$FindBin::Bin";
use generator;


#forward declarations

#global variables
my $VERSION = "1.0.0";

# output directory is...
my $TOP_LEVEL = defined($ARGV[1]) ? $ARGV[1] : getcwd();
my $BLOCK_MODEL_PATH = "${TOP_LEVEL}/models/block";
my $ITEM_MODEL_PATH = "${TOP_LEVEL}/models/item";

my $MODID = $ARGV[0];

my $verbose = 1;
die "modid is required!" if ! defined($MODID);

# create if they do not exist.
make_path($BLOCK_MODEL_PATH, $ITEM_MODEL_PATH);

# go there
chdir $TOP_LEVEL or die "Unable to change to ${TOP_LEVEL}: $!\n";

my $resp;
my $block_or_item = 0;
my $block_subtype = 0;
my $item_subtype = 0;
my $bs_template;
my $block_template;
my $not_done = 1;

while ($not_done) 
{
    # block or item?
    print "Block (B) or Item (I) model? ";
    $resp = <STDIN>;
    if ($resp =~ /^B/i) {
        $block_or_item = 'B';
    }
    elsif ($resp =~ /^I/i) {
        $block_or_item = 'I';
    }

    if ($block_or_item eq 'B')
    {
        print "Generic block (G;default), crop block (C), ",
            "Face block [like jack_o_lantern] (F), pillar/log block (P), ",
            "Machine [like furnace] (M), Bars [like iron_bars] (B), ",
            "Doors (D), Thin pane [like glass] (T), Stairs (S) ? ";
        $resp = <STDIN>;
        $block_subtype = ($resp =~ /^[GCFPMBTSD]/i) 
                        ? uc(substr($resp,0,1)) 
                        : 'G';
    } ## end-if block
    else {
        print "Generic inventory item (G;default),",
            "item-of-block (B), bow (W), armor set (A), tool set (T) ? ";
        $resp = <STDIN>;
        $item_subtype = ($resp =~ /^[GBAWT]/i) ?  uc(substr($resp,0,1)) : 'G';
    } ## end-else item

    if ($verbose) {
        print "\$block_or_item = ", $block_or_item, "\n";
        print "\$block_subtype = ", $block_subtype, "\n";
        print "\$item_subtype = ", $item_subtype, "\n";
    }

    if ($block_or_item eq 'B')
    {
        get_block_info($block_subtype);
    }
    else {
        get_item_info($item_subtype);
    }

    $not_done = check_repeat("Create another model [Y/N]? ");
} ## end-while not_done

exit;


=head1 SUBROUTINES

=over

=item B<get_item_info>

Summary of subroutine

Params: $item_subtype

=cut

sub get_item_info
{
    my $item_type = $_[0];
    my $resp;
    my $prompt;
    my ($item_template, $item_stem);
    my @item_textures;
    my @out_jsons;
    my $found = 0;
    my $not_done = 1;

    if ($item_type eq 'B') # item-of-block (B)
    {
        while ($not_done)
        {
            $prompt = "Name of block to create itemblock model for (e.g. foo_block): ";
            @out_jsons = get_simple_json_path($prompt, $ITEM_MODEL_PATH);
            write_item_of_block(@out_jsons);
            $not_done = check_repeat(
                        "Create another item-of-block [Y/N]? ");
        } ## end while not_done 
    }
    elsif ($item_type eq 'G') #  Generic inventory item (G;default)",
    {
        make_model_prompts(['baked_potato',], 'baked_potato', ['baked_potato',],
            $MC_ITEM_MODEL_PATH, $ITEM_MODEL_PATH);
    }
    elsif ($item_type eq 'W') # bow (W)
    {
        make_model_prompts(['bow','bow_pulling_0', 'bow_pulling_1',
            'bow_pulling_2'], 'bow', ['bow',], 
            $MC_ITEM_MODEL_PATH, $ITEM_MODEL_PATH);
    }
    elsif ($item_type eq 'A') # armor set (A)
    {
        make_model_prompts(['iron_boots', 'iron_chestplate', 'iron_helmet',
                'iron_leggings'], 'iron', ['iron',],
            $MC_ITEM_MODEL_PATH, $ITEM_MODEL_PATH);
    }
    elsif ($item_type eq 'T') # tool set (T) 
    {
        make_model_prompts(['iron_axe', 'iron_hoe', 'iron_pickaxe', 
            'iron_shovel', 'iron_sword'], 'iron', ['iron',],
            $MC_ITEM_MODEL_PATH, $ITEM_MODEL_PATH);
    }
} ## end sub get_item_info


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

    if ($block_type eq 'G' )  # generic simple block
    {
        while ($not_done)
        {
            $prompt = "Name of block to create files for (e.g. foo_block): ";
            @out_jsons = get_simple_json_path($prompt, $BLOCK_MODEL_PATH);
            $prompt = "Target texture to use: ";
            $out_texture = get_response($prompt);
            write_cubeall_model($out_jsons[1], $out_texture);
            
            $not_done = check_repeat(
                        "Create another simple cube [Y/N]? ");
        } ## end while not_done 
    }
    elsif ($block_type eq 'C')  # crop block
    {
        make_model_prompts(['wheat_stage0', 'wheat_stage1', 'wheat_stage2',
            'wheat_stage3', 'wheat_stage4', 'wheat_stage5', 'wheat_stage6', 
            'wheat_stage7'], 'wheat', ['wheat',], 
            $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
    }
    elsif ($block_type eq 'P')  # pillar/log block
    {
        make_model_prompts(['oak_log',], 'oak_log', ['oak_log_top', 'oak_log'],
                $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
    } ## end-elsif P
    elsif ($block_type eq 'F')  # block with facing
    {
        # 1 = furnace, 2 = smoker
        $prompt = "Pick one: (1) front, top & sides different, or "
            . "(2) front, top, sides & bottom different: ";
        my $choice = get_response($prompt);
        if ($choice eq '1') 
        {
            make_model_prompts(['furnace',], 'furnace', 
                ['furnace_top', 'furnace_front', 'furnace_side'], 
                $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
        }
        elsif ($choice eq '2')
        {
            make_model_prompts(['smoker',], 'smoker', 
                ['smoker_bottom', 'smoker_top', 'smoker_front', 'smoker_side'], 
                $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
        }
    } ## end-elsif F
    elsif ($block_type eq 'M') # furnace-like machine
    {
        make_model_prompts(['furnace', 'furnace_on'], 'furnace',
                ['furnace_top', 'furnace_front', 'furnace_front_on',
                  'furnace_side'], $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
    } ## end-elsif M
    elsif ($block_type eq 'B') # Bars [like iron_bars] (B)
    {
        make_model_prompts(['iron_bars_cap_alt', 'iron_bars_cap',
            'iron_bars_post_ends', 'iron_bars_post', 'iron_bars_side_alt',
            'iron_bars_side'], 'iron_bars', ['iron_bars',], 
            $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
    } ## end elsif B
    elsif ($block_type eq 'D') # Doors (D)
    {
        make_model_prompts(['oak_door_bottom_hinge', 'oak_door_bottom',
            'oak_door_top_hinge', 'oak_door_top'], 'oak_door', 
            ['oak_door_bottom', 'oak_door_top'],
            $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
    }
    elsif ($block_type eq 'T') # Thin pane [like glass] (T)
    {
        make_model_prompts(['glass_pane_noside_alt', 'glass_pane_noside',
            'glass_pane_post', 'glass_pane_side', 'glass_pane_side_alt'],
            'glass_pane', ['glass_pane_top', 'glass'],
            $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
    }
    elsif ($block_type eq 'S') # Stairs (S) 
    {
        make_model_prompts(['oak_stairs', 'oak_stairs_inner', 
            'oak_stairs_outer'], 'oak_stairs', ['oak_planks',],
            $MC_BLOCK_MODEL_PATH, $BLOCK_MODEL_PATH);
    }
} ## end-get_block_info


=item B<make_model_prompts>

Bundles up a bunch of repetitive, common code for making models.

=cut

sub make_model_prompts
{
    my ($ref_models, $mc_stem, $ref_mc_textures, $mc_path, $mod_path) = @_;
    my $prompt = 
        "Common stem name of models to create files for (e.g. foocrop): ";
    my $new_modstem = get_response($prompt);
    my %texture_hash;
    foreach my $mc_texture (@$ref_mc_textures) 
    {
        $prompt = "Stem name of replacement texture for ${mc_texture}: ";
        my $new_texture = get_response($prompt);
        $texture_hash{$mc_texture} = $new_texture;
    }
    copy_models($mc_path, $mod_path, $mc_stem, $new_modstem, \%texture_hash,
                $ref_models);
} ## end sub make_model_prompts


=item B<write_cubeall_model>

write a simple cubic block model.

=cut

sub write_cubeall_model
{
    my ($out_json, $texture) = @_;
    open (my $fh, ">", $out_json) or die "Unable to open ${out_json}: $!";
    print $fh "{\n";
    print $fh "\t\"parent\": \"block/cube_all\",\n";
    print $fh "\t\"textures\": {\n";
    print $fh "\t\t\"all\": \"${MODID}:block/${texture}\"\n";
    print $fh "\t}\n";
    print $fh "}\n";
    close $fh;
} ## end sub write_cubeall_model


=item B<write_item_of_block>

Write the item-of-block model--very simple model.

=cut

sub write_item_of_block
{
    my ($parent, $out_json) = @_;
    open (my $fh, ">", $out_json) or die "Unable to open ${out_json}: $!";
    print $fh "{\n";
    print $fh "\t\"parent\": \"block/${MODID}:${parent}\"\n";
    print $fh "}\n";
    close $fh;
} ## end sub write_item_of_block


=item B<copy_models>

copy one or more simple models that have one texture.

=cut

sub copy_models
{
    my ($mc_path, $mod_path, $in_mstem, $out_mstem, 
        $href_textures, $model_list) = @_;
    my ($in_model_path, $out_model_path, $out_model);

    foreach my $model (@$model_list)
    {
        $in_model_path = File::Spec->catfile($mc_path, "${model}.json");
        $out_model = $model;
        $out_model =~ s/${in_mstem}/${out_mstem}/;
        $out_model = $out_model . ".json";
        $out_model_path = File::Spec->catfile($mod_path, $out_model);
        open (my $fh, "<", $in_model_path) 
            or die "Unable to open ${in_model_path}: $!";
        open (my $fh2, ">", $out_model_path) 
            or die "Unable to open ${out_model_path}: $!";

        while (my $line = <$fh>)
        {
            foreach my $old_texture (keys(%$href_textures))
            {
                my $new_texture = $href_textures->{$old_texture};
                $line =~ s/${old_texture}/${new_texture}/;
                $line =~ s/block\/(${new_texture})/${MODID}:block\/$1/;
                $line =~ s/item\/(${new_texture})/${MODID}:item\/$1/;
            }
            print $fh2 $line;
        } ## end-while
        close $fh2;
        close $fh;
    } ## end-foreach
} ## end copy_models()

__END__

=back

