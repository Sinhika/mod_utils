#!/usr/bin/perl
#
=head1 NAME
    
    build_graphic_jsons.pl - create a set of blockstate/model/etc jsons.

=head1 SYNOPSIS

    build_graphic_jsons.pl modid [topdir]

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
use List::MoreUtils qw(uniq);

# constants to be re-defined when necessary
# where are the vamilla assets?
my $MC_ASSETS = File::Spec->catdir($ENV{HOME},
                        "/Projects/Minecraft_1.10/vanilla/assets/minecraft");
my $MC_BLOCKSTATE_PATH = "${MC_ASSETS}/blockstates";
my $MC_BLOCK_MODEL_PATH = "${MC_ASSETS}/models/block";
my $MC_ITEM_MODEL_PATH = "${MC_ASSETS}/models/item";

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
my $block_or_item = 0;
my $block_subtype = 0;
my $item_subtype = 0;
my $bs_template;
my $block_template;

# block or item?
while (! $block_or_item) {
    print "Block (B) or Item (I) ? ";
    $resp = <STDIN>;
    if ($resp =~ /^B/i) {
        $block_or_item = 'B';
    }
    elsif ($resp =~ /^I/i) {
        $block_or_item = 'I';
    }
}

if ($block_or_item eq 'B')
{
    print "Generic block (G;default), crop block (C), ",
           "Face block [like pumpkin] (F), pillar/log block (P), ",
           "Bars [like iron_bars] (B), ",
           "Thin pane [like glass] (T), Special case (S) ? ";
    $resp = <STDIN>;
    $block_subtype = ($resp =~ /^[GCFPBTS]/i) ? uc(substr($resp,0,1)) : 'G';
}
else {
    print "Generic inventory item (G;default), item-of-block (B), bow (W),",
        " armor set (A), tool set (T) ? ";
    $resp = <STDIN>;
    $item_subtype = ($resp =~ /^[GBAWT]/i) ?  uc(substr($resp,0,1)) : 'G';
}

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

exit;
 
=head1 FUNCTIONS

=over

=item get_response

=cut

sub get_response
{
    my $prompt = $_[0];
    my $resp;

    print $prompt;
    $resp = <STDIN>;
    chomp($resp);
    return $resp; 
}

=item check_repeat

=cut

sub check_repeat
{
    my $resp = get_response($_[0]);
    if ((length($resp) == 0) or (uc(substr($resp,0,1)) eq 'Y')) {
        return 1;
    }
    else {
        return 0;
    }
} ## end check_repeat()

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

    if ($block_type eq 'G' or $block_type eq 'C')  # generic or crop block
    {
        $prompt = "Is this a simple cube-type block [Y/N]? ";
        # write Forge-type blockstate for cube_all...
        if (check_repeat($prompt)) 
        {
            while ($not_done)
            {
                $prompt = "Name of block to create files for (e.g. foo_block): ";
                @out_jsons = get_simple_item_json($prompt, $BLOCKSTATE_PATH);
                $prompt = "Target texture to use: ";
                $out_texture = get_response($prompt);
                ## TODO
                write_cubeall_blockstate($out_jsons[1], $out_texture);
                $not_done = check_repeat(
                            "Create another simple cube [Y/N]? ");
            } ## end while not_done 
        }
        else 
        {
            $prompt = "Vanilla block to use as template (e.g. cobblestone): ";
            ($block_stem, $template_json) =
                get_template($prompt, $MC_BLOCKSTATE_PATH);
            while ($not_done)
            {
                $prompt = "Name of block to create files for (e.g. foo_block): ";
                @out_jsons = get_simple_item_json($prompt, $BLOCKSTATE_PATH);
                my @models = find_model_variants($template_json);

                print "Source blockstate: ", $template_json, "\n";
                print " models to copy: ";
                map {print "\t${_}\n" } @models;
                print "Target blockstate: ", $out_jsons[1], "\n";
                $prompt = "Source modelname stem to replace: ";
                $templ_model_stem = get_response($prompt);
                $prompt = "Target modelname stem to replace it with: ";
                $out_model_stem = get_response($prompt);
                $prompt = "Target texture to use: ";
                $out_texture = get_response($prompt);

                copy_blockstate($template_json, $templ_model_stem, $out_jsons[1],
                                $out_model_stem);
                            
                copy_models($templ_model_stem, $out_model_stem, $out_texture, 
                            \@models);

                $not_done = check_repeat(
                            "Create another block from the same template [Y/N]? ");
            } ## end while not_done 
        } ## end-else not a simple cube
    }
    elsif ($block_type eq 'F')  # 'face' block
    {
        $prompt = "Vanilla block to use as template (e.g. pumpkin): ";
        ($block_stem, $template_json) =
            get_template($prompt, $MC_BLOCKSTATE_PATH);
        while ($not_done)
        {
            $prompt = "Name of block to create files for (e.g. foo_gourd): ";
            @out_jsons = get_simple_item_json($prompt, $BLOCKSTATE_PATH);
            my @models = find_facing_variants($template_json);

            print "Source blockstate: ", $template_json, "\n";
            for (my $i=0; ($i+2) <= $#models; $i += 3)
            {
                printf "Variant: %s, model: %s, rest: %s\n", $models[$i],
                        $models[$i+1], $models[$i+2];
            }
            print "Target blockstate: ", $out_jsons[1], "\n";

            $prompt = "Source modelname stem to replace: ";
            $templ_model_stem = get_response($prompt);
            $prompt = "Target modelname stem to replace it with: ";
            $out_model_stem = get_response($prompt);

            # write blockstate file
            copy_blockstate($template_json, $templ_model_stem, $out_jsons[1],
                            $out_model_stem);
                        
            $prompt = "source texture stem to use (e.g. pumpkin): ";
            $template_texture = get_response($prompt);

            $prompt = "Target texture stem to use (e.g. foo_gourd): ";
            $out_texture = get_response($prompt);

            # write model files 
            copy_model_with_variants($templ_model_stem, $out_model_stem, 
                                     $template_texture, $out_texture, 
                                     $models[1]);
            
            # repeat?
            $not_done = check_repeat(
                        "Create another block from the same template [Y/N]? ");
        } ## end while not_done
    } ## end-elsif 'face' block
    elsif ($block_type eq 'P')   # pillar/log-type block
    {
        $prompt = "Vanilla block to use as template (e.g. acacia_log): ";
        ($block_stem, $template_json) =
            get_template($prompt, $MC_BLOCKSTATE_PATH);
        while ($not_done)
        {
            $prompt = "Name of block to create files for (e.g. foo_log): ";
            @out_jsons = get_simple_item_json($prompt, $BLOCKSTATE_PATH);
            my @models = find_facing_variants($template_json);

            print "Source blockstate: ", $template_json, "\n";
            for (my $i=0; ($i+2) <= $#models; $i += 3)
            {
                printf "Variant: %s, model: %s, rest: %s\n", $models[$i],
                        $models[$i+1], $models[$i+2];
            }
            print "Target blockstate: ", $out_jsons[1], "\n";

            $prompt = "Source modelname stem to replace: ";
            $templ_model_stem = get_response($prompt);
            $prompt = "Target modelname stem to replace it with: ";
            $out_model_stem = get_response($prompt);

            # write blockstate file
            copy_blockstate($template_json, $templ_model_stem, $out_jsons[1],
                            $out_model_stem);
                        
            $prompt = "source texture stem to use (e.g. log_acacia): ";
            $template_texture = get_response($prompt);

            $prompt = "Target texture stem to use (e.g. log_foo): ";
            $out_texture = get_response($prompt);

            # write model files 
            copy_more_models_with_var($templ_model_stem, $out_model_stem, 
                                     $template_texture, $out_texture, 
                                     \@models);

            # repeat?
            $not_done = check_repeat(
                "Create another block from the same template [Y/N]? ");
        } ## end while not_done
    } ## end-elsif pillars
    elsif ($block_type eq 'B')
    {
        # there is only one template for bars...
        $block_stem = "iron_bars";
        $template_json = File::Spec->catfile($MC_BLOCKSTATE_PATH, $block_stem);
        $template_json .= ".json";
        while ($not_done)
        {
            $prompt = "Name of block to create files for (e.g. foo_bars): ";
            @out_jsons = get_simple_item_json($prompt, $BLOCKSTATE_PATH);
            my $out_stem = $out_jsons[0];
            my $block_json = $out_jsons[1];

            # write blockstate file
            copy_blockstate($template_json,'iron_bars',$block_json, $out_stem);

            $template_texture = 'iron_bars';
            $prompt = "Target texture stem to use (e.g. foo_bars): ";
            $out_texture = get_response($prompt);
                 
            my @models = ("${out_stem}_post_ends", "${out_stem}_post",
                    "${out_stem}_cap", "${out_stem}_cap_alt", 
                    "${out_stem}_side", "${out_stem}_side_alt");
            copy_multiple_models($out_texture, \@models);
            # repeat?
            $not_done = check_repeat(
                "Create another block from the same template [Y/N]? ");
        } ## end while not_done
        
    } ## end-elsif bars
    else {
        print "block_type ${block_type} not yet implemented.\n";

    }
} ## end-get_block_info


=item copy_multiple_models

=cut

sub copy_multiple_models
{
    my $new_texture = $_[0];
    my $models_ref = $_[1];
    my $old_texture = 'blocks/iron_bars';

    my @src_models = ("iron_bars_post_ends", "iron_bars_post",
        "iron_bars_cap", "iron_bars_cap_alt", "iron_bars_side",
        "iron_bars_side_alt");

    my ($in_model_path, $out_model_path, $out_model);
    for (my $ii=0; $ii < scalar(@$models_ref); $ii++)
    {
        my $tmpl_model = $src_models[$ii];
        $in_model_path = File::Spec->catfile($MC_BLOCK_MODEL_PATH,
                                             "${tmpl_model}.json");
        my $out_model = $$models_ref[$ii] . '.json';
        $out_model_path = File::Spec->catfile($BLOCK_MODEL_PATH, $out_model);

        open (my $fh, "<", $in_model_path) 
            or die "Unable to open ${in_model_path}: $!";
        open (my $fh2, ">", $out_model_path) 
            or die "Unable to open ${out_model_path}: $!";
        while (my $line = <$fh>)
        {
            $line =~ s/${old_texture}/${MODID}:blocks\/${new_texture}/;
            print $fh2 $line;
        } ## end-while
        close $fh2;
        close $fh;
    } ## end-for

} ## end sub 


=item copy_more_models_with_var

=cut

sub copy_more_models_with_var
{
    my ($in_mstem, $out_mstem, $old_texture, $new_texture, $model_list) = @_;
    my ($in_model_path, $out_model_path, $out_model);

    #foreach my $model (@$model_list)
    for (my $i=0; ($i+2) <= scalar @$model_list;  $i += 3)
    {
        my $model = $model_list->[1];
        my $texfound = 0;
        $in_model_path = File::Spec->catfile($MC_BLOCK_MODEL_PATH,
                                             "${model}.json");
        $model =~ s/${in_mstem}/${out_mstem}/;
        $out_model = $model . ".json";
        $out_model_path = File::Spec->catfile($BLOCK_MODEL_PATH, $out_model);
        open (my $fh, "<", $in_model_path) 
            or die "Unable to open ${in_model_path}: $!";
        open (my $fh2, ">", $out_model_path) 
            or die "Unable to open ${out_model_path}: $!";

        while (my $line = <$fh>)
        {
            $texfound = 1 if ($line =~ /"textures"/ );
            if ($texfound) {
                $line =~ 
   s/^(\s*".*?":\s*")blocks\/${old_texture}/$1${MODID}:blocks\/${new_texture}/;
            }
            print $fh2 $line;
        } ## end-while
        close $fh2;
        close $fh;
    } ## end-foreach
} ## end ()

=item copy_models

=cut

sub copy_models
{
    my ($in_mstem, $out_mstem, $new_texture, $model_list) = @_;
    my ($in_model_path, $out_model_path, $out_model);

    foreach my $model (@$model_list)
    {
        $in_model_path = File::Spec->catfile($MC_BLOCK_MODEL_PATH,
                                             "${model}.json");
        $model =~ s/${in_mstem}/${out_mstem}/;
        $out_model = $model . ".json";
        $out_model_path = File::Spec->catfile($BLOCK_MODEL_PATH, $out_model);
        open (my $fh, "<", $in_model_path) 
            or die "Unable to open ${in_model_path}: $!";
        open (my $fh2, ">", $out_model_path) 
            or die "Unable to open ${out_model_path}: $!";

        while (my $line = <$fh>)
        {
            $line =~ s/"texture":\s*"(.*?)"/"texture": "${new_texture}"/;
            $line =~ s/"all":\s*"(.*?)"/"all": "${new_texture}"/;
            print $fh2 $line;
        } ## end-while
        close $fh2;
        close $fh;
    } ## end-foreach
} ## end copy_models()


=item copy_model_with_variants

=cut

sub copy_model_with_variants
{
    my ($in_mstem, $out_mstem, $old_texture, $new_texture, $model_stem) = @_;
    my ($in_model_path, $out_model_path, $out_model);
    my $texfound = 0;

    # for this type, there is one model file, but variant textures.
    $in_model_path = File::Spec->catfile($MC_BLOCK_MODEL_PATH,
                                            "${in_mstem}.json");
    $out_model = $out_mstem . ".json";
    $out_model_path = File::Spec->catfile($BLOCK_MODEL_PATH, $out_model);

    open (my $fh, "<", $in_model_path) 
        or die "Unable to open ${in_model_path}: $!";
    open (my $fh2, ">", $out_model_path) 
        or die "Unable to open ${out_model_path}: $!";

    while (my $line = <$fh>)
    {
        $texfound = 1 if ($line =~ /"textures"/ );
        if ($texfound) {
$line =~ s/^(\s*".*?":\s*")blocks\/${old_texture}/$1${MODID}:blocks\/${new_texture}/;
        }
        print $fh2 $line;
    } ## end-while
    close $fh2;
    close $fh;
} ## end copy_model_with_variants()


=item copy_blockstate

=cut

sub copy_blockstate
{
    my ($in_json, $in_mstem, $out_json, $out_mstem) = @_;
    open (my $fh, "<", $in_json) or die "Unable to open ${in_json}: $!";
    open (my $fh2, ">", $out_json) or die "Unable to open ${out_json}: $!";
    while (my $line = <$fh>)
    {
        $line =~ s/$in_mstem/$MODID:$out_mstem/;
        print $fh2 $line;
    }
    close $fh;
    close $fh2;
} ## end copy_blockstate()


=item write_cubeall_blockstate

write a standard Forge blockstate for a stock cube_all model block.

=cut

sub write_cubeall_blockstate
{
    my ($out_json, $texture) = @_;
    open (my $fh, ">", $out_json) or die "Unable to open ${out_json}: $!";
    print $fh "{\n";
    print $fh "\t\"forge_marker\" : 1,\n";
    print $fh "\t\"defaults\": {\n";
    print $fh "\t\t\"textures\": { \"all\": \"${texture}\" }\n";
    print $fh "\t},\n";
    print $fh "\t\"variants\": {\n";
    print $fh "\t\t\"normal\": { \"model\" : \"cube_all\" },\n";
    print $fh "\t\t\"inventory\": { \"model\" : \"cube_all\" }\n";
    print $fh "\t}\n";
    print $fh "}";
    close $fh;
} ## end write_cubeall_blockstate()


=item get_item_info

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

    if ($item_type eq 'G')  # generic inventory item
    {
        $prompt = "Vanilla item to use as template (e.g. wheat_seeds): ";
        ($item_stem, $item_template) 
            = get_template($prompt, $MC_ITEM_MODEL_PATH);
        while ($not_done)
        {
            $prompt = "Name of item to create files for (e.g. foo_seeds): ";
            @out_jsons = get_simple_item_json($prompt, $ITEM_MODEL_PATH);
            print "Source template: ", $item_template, "\n";
            print "Target template: ", $out_jsons[1], "\n";
            print "Replace texture ", $item_stem, " with ${MODID}:${out_jsons[0]}\n";
            $found = copy_item_models($item_template, $item_stem, \@out_jsons);
            if (! $found) {
                print "Unable to find texture name ${item_stem} in ",
                    "${item_template}; you need to change it manually in ",
                    $out_jsons[1],".\n";
            }

            $not_done = check_repeat(
                "Create another item from the same template [Y/N]? ");
        } ## end while not_done
    } ## end if 'G'
    elsif ($item_type eq 'B')  # item-of-block
    {
        $prompt = "Vanilla item-of-block to use as template (e.g. iron_block): ";
        ($item_stem, $item_template) 
            = get_template($prompt, $MC_ITEM_MODEL_PATH);
        while ($not_done)
        {
            $prompt = "Name of item to create files for (e.g. fooblock): ";
            @out_jsons = get_item_of_block_json($prompt, $ITEM_MODEL_PATH);
            print "Source template: ", $item_template, "\n";
            print "Target template: ", $out_jsons[2], "\n";
            print "Replace texture ", $item_stem, " with ${MODID}:blocks/${out_jsons[1]}\n";
            $found = copy_itemofblock_models($item_template, $item_stem, \@out_jsons);
            if (! $found) {
                print "Unable to find parent reference ${item_stem} in ",
                    "${item_template}; you need to change it manually in ",
                    $out_jsons[2],".\n";
            }

            $not_done = check_repeat( 
                "Create another item from the same template [Y/N]? ");
        } ## end while not_done
    }
    elsif ($item_type eq 'W')  # boW
    {
      
        # vanilla bow templates 
        my @template_bows = ("bow", "bow_pulling_0", "bow_pulling_1", 
                          "bow_pulling_2");
        
        while ($not_done)
        {
            $prompt = "Name of bow to create files for (e.g. foo_bow): ";
            my $out_bow_stem = get_response($prompt);
            foreach my $templ_bow (@template_bows)
            { 
                ($item_stem, $item_template) =
                   ($templ_bow, 
                    File::Spec->catfile($MC_ITEM_MODEL_PATH,
                                         "${templ_bow}.json"));
                $out_jsons[0] = $item_stem;
                $out_jsons[0] =~ s/bow/${out_bow_stem}/;
                $out_jsons[1] = File::Spec->catfile($ITEM_MODEL_PATH,
                                                    "${out_jsons[0]}.json");

                print "Source template: ", $item_template, "\n";
                print "Target template: ", $out_jsons[1], "\n";
                print "Replace texture ", $item_stem, " with ${MODID}:${out_jsons[0]}\n";
                
                $found = copy_item_models($item_template, $item_stem, 
                                           \@out_jsons);
                if (! $found) {
                    print "Unable to find texture name ${item_stem} in ",
                        "${item_template}; you need to change it manually in ",
                        $out_jsons[1],".\n";
                }
            } ## end foreach 
            $not_done = check_repeat( "Create another bow [Y/N]? ");
        } ## end while not_done
    }
    elsif ($item_type eq 'A') # armor sets
    {
        # vanilla metal armor templates (ignoring leather right now)
        my @template_armor = ("iron_helmet", "iron_boots", "iron_chestplate",
                              "iron_leggings" );

        while ($not_done)
        {
            $prompt = "Armor material to create files for (e.g. fooite): ";
            my $out_mat_stem = get_response($prompt);
            foreach my $templ_armor (@template_armor)
            { 
                ($item_stem, $item_template) =
                   ($templ_armor, 
                    File::Spec->catfile($MC_ITEM_MODEL_PATH,
                                         "${templ_armor}.json"));
                $out_jsons[0] = $item_stem;
                $out_jsons[0] =~ s/iron/${out_mat_stem}/;
                $out_jsons[1] = File::Spec->catfile($ITEM_MODEL_PATH,
                                                    "${out_jsons[0]}.json");

                print "Source template: ", $item_template, "\n";
                print "Target template: ", $out_jsons[1], "\n";
                print "Replace texture ", $item_stem, " with ${MODID}:${out_jsons[0]}\n";
                $found = copy_item_models($item_template, $item_stem, 
                                           \@out_jsons);
                if (! $found) {
                    print "Unable to find texture name ${item_stem} in ",
                        "${item_template}; you need to change it manually in ",
                        $out_jsons[1],".\n";
                }
            }   
            $not_done = check_repeat( "Create another armor set [Y/N]? ");
        } ## end-while not_done
    }
    elsif ($item_type eq 'T') # tool sets
    {
        # vanilla metal tool set:
        my @template_tools = (
            "iron_axe", "iron_hoe", "iron_pickaxe", "iron_shovel", 
            "iron_sword");
        
        while ($not_done)
        {
            $prompt = "Weapon material to create files for (e.g. fooite): ";
            my $out_mat_stem = get_response($prompt);
            foreach my $templ_tool (@template_tools)
            { 
                ($item_stem, $item_template) =
                   ($templ_tool, 
                    File::Spec->catfile($MC_ITEM_MODEL_PATH,
                                         "${templ_tool}.json"));
                $out_jsons[0] = $item_stem;
                $out_jsons[0] =~ s/iron/${out_mat_stem}/;
                $out_jsons[1] = File::Spec->catfile($ITEM_MODEL_PATH,
                                                    "${out_jsons[0]}.json");

                print "Source template: ", $item_template, "\n";
                print "Target template: ", $out_jsons[1], "\n";
                print "Replace texture ", $item_stem, " with ${MODID}:${out_jsons[0]}\n";
                $found = copy_item_models($item_template, $item_stem, 
                                           \@out_jsons);
                if (! $found) {
                    print "Unable to find texture name ${item_stem} in ",
                        "${item_template}; you need to change it manually in ",
                        $out_jsons[1],".\n";
                }
            }   
            $not_done = check_repeat( "Create another tool set [Y/N]? ");
        } ## end-while not_done
    }
    else {
        print "item_type ${item_type}  not yet implemented.\n";
        return;
    }
} ## end get_item_info()

=item copy_itemofblock_models

=cut

sub copy_itemofblock_models
{
    my ($item_template, $item_stem, $out_jsons) = @_;
    my $parent = $out_jsons->[1]; 
    my $found = 0;

    open(my $fh, "<", $item_template) 
        or die "Cannot open < ${item_template}: $!";
    open(my $fh2, ">", $out_jsons->[2])
        or die "Cannot open < " . $out_jsons->[2] . ": $!";
    
    while (my $line = <$fh>)
    {
        if ($line =~ s/\"parent\": \"block\/${item_stem}\"/\"parent\": \"${MODID}:block\/${parent}\"/)
        {
            $found = 1;
        }
        print $fh2 $line;
    } ## end-while
    close $fh;
    close $fh2;
    return $found;

} ## end sub

=item copy_item_models

=cut

sub copy_item_models
{
    my ($item_template, $item_stem, $out_jsons) = @_;
    my $texture = $out_jsons->[0];
    my $found = 0;

    open(my $fh, "<", $item_template) 
        or die "Cannot open < ${item_template}: $!";
    open(my $fh2, ">", $out_jsons->[1])
        or die "Cannot open < " . $out_jsons->[1] . ": $!";
    
    while (my $line = <$fh>)
    {
        if ($line =~ 
  s/\"layer0\": \"items\/${item_stem}/\"layer0\": \"${MODID}:items\/${texture}/)
        {
            $found = 1;
        }
        elsif ($line =~
  s/\"layer0\": \"blocks\/${item_stem}/\"layer0\": \"${MODID}:blocks\/${texture}/)
        {
            $found = 1;
        }
        print $fh2 $line;
    } ## end-while
    close $fh;
    close $fh2;
    return $found;
} ## end sub


=item get_template

    $template = get_template($prompt, $mc_path);

Prompt for an item or block template.

=cut
    
sub get_template
{
    my $prompt = $_[0];
    my $mc_path = $_[1];
    my $template = 0;
    my $stem;

    while (! $template) 
    {
        $stem = get_response($prompt);
        $template = File::Spec->catfile($mc_path, $stem);
        if ($template !~ /\.json$/) {
            $template .= '.json';
        }
        if ( ! -r $template ) {
            print "${template} does not exist or is not readable!",
                "Try again, or Ctrl-C to abort\n";
            $template = 0;
        }
    } ## end-while
    return ($stem, $template);
} ## end get_template()

=item get_simple_item_json

Just get the item name and make a .json file.

=cut

sub get_simple_item_json
{
    my $prompt = $_[0];
    my $outpath = $_[1];
    my $json;
    my $resp;

    $resp = get_response($prompt);
    $json = File::Spec->catfile($outpath, $resp);
    $json .= '.json';
    return ($resp, $json,);
} ## end get_simple_item_json()

=item get_item_of_block_json

=cut

sub get_item_of_block_json
{
    my $prompt = $_[0];
    my $outpath = $_[1];
    my ($json, $stem, $parent);
    $stem = get_response($prompt);
    $json = File::Spec->catfile($outpath, $stem);
    $json .= '.json';
    $prompt = "Name of parent block (e.g. fooblock): ";
    $parent = get_response($prompt);
    return ($stem, $parent, $json);
} ## end sub

=item find_model_variants

returns a list of unique models found in a blockstate json.

=cut

sub find_model_variants
{
    my $bs_json = $_[0];
    my @variants = ();

    open (my $fh, "<", $bs_json) or die "Cannot open ${bs_json}: $!";
    while (my $line = <$fh>)
    {
        if ($line =~ /"(.+?)"\s*:\s*{\s*"model"\s*:\s*"(.+?)"/) {
            push @variants, $2
        }
    } ## end-while
    close $fh;
    @variants = uniq @variants;
    return @variants;
} ## end find_model_variants()


=item find_facing_variants

returns a list of facing,model,other trios found in a blockstate json.

=cut

sub find_facing_variants
{
    my $bs_json = $_[0];
    my @variants = ();

    open (my $fh, "<", $bs_json) or die "Cannot open ${bs_json}: $!";
    while (my $line = <$fh>)
    {
        if ($line =~ /"(.+?)":\s*{\s*"model":\s*"(.+?)"\s*},?\s*$/) 
        {
            push @variants, ($1, $2, 0);
        }
        elsif ($line =~ 
          /"(.+?)":\s*{\s*"model":\s*"(.+?)",(\s*".+)},?\s*$/) 
        {
            push @variants, ($1, $2, $3);
        }
    } ## end-while
    close $fh;
    return @variants;
} ## end find_model_variants()

=back

=head1 HISTORY


=cut
