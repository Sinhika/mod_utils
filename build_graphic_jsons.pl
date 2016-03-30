#!/usr/bin/perl
#
=head1 NAME
    
    build_graphic_jsons.pl - create a set of blockstate/model/etc jsons.

=head1 SYNOPSIS

    build_graphic_jsons.pl [top_dir]

=over

=item top_dir

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

# constants to be re-defined when necessary
# where are the vamilla assets?
my $MC_ASSETS = File::Spec->catdir($ENV{HOME},
                        "/Projects/Minecraft_1.8/vanilla/assets/minecraft");
my $MC_BLOCKSTATE_PATH = "${MC_ASSETS}/blockstates";
my $MC_BLOCK_MODEL_PATH = "${MC_ASSETS}/models/block";
my $MC_ITEM_MODEL_PATH = "${MC_ASSETS}/models/item";

# output directory is...
my $TOP_LEVEL = defined($ARGV[0]) ? $ARGV[0] : getcwd();
my $BLOCKSTATE_PATH = "${TOP_LEVEL}/blockstates";
my $BLOCK_MODEL_PATH = "${TOP_LEVEL}/models/block";
my $ITEM_MODEL_PATH = "${TOP_LEVEL}/models/item";

my $verbose = 1;

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
           "Face block [like pumpkin] (F), pillar block (P), ",
           "Thin pane [like glass] (T), Special case (S) ? ";
    $resp = <STDIN>;
    $block_subtype = ($resp =~ /^[GCFPTS]/i) ? uc(substr($resp,0,1)) : 'G';
}
else {
    print "Generic inventory item (G;default), item-of-block (B), bow (W),",
        " armor set (A) ? ";
    $resp = <STDIN>;
    $item_subtype = ($resp =~ /^[GBAW]/i) ?  uc(substr($resp,0,1)) : 'G';
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

=item get_block_info

=cut

sub get_block_info
{
    my $block_type = $_[0];

    print "block_type ${block_type} not yet implemented.\n";
} ## end-get_block_info

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

    if ($item_type eq 'G') 
    {
        $prompt = "Vanilla item to use as template (e.g. wheat_seeds): ";
        ($item_stem, $item_template) 
            = get_template($prompt, $MC_ITEM_MODEL_PATH);
        $prompt = "Name of item to create files for (e.g. foo_seeds): ";
        @out_jsons = get_simple_item_json($prompt, $ITEM_MODEL_PATH);
       
        open(my $fh, "<", $item_template) 
            or die "Cannot open < ${item_template}: $!";
        open(my $fh2, ">", $out_jsons[1])
            or die "Cannot open < " . $out_jsons[1] . ": $!";
        
        while (my $line = <$fh>)
        {
            if ($line =~ s/${item_stem}/${out_jsons[0]}/ ) {$found = 1};
            print $fh2 $line;
        } ## end-while
        close $fh;
        close $fh2;
        if (! $found) {
            print "Unable to find texture name ${item_stem} in ",
                "${item_template}; you need to change it manually in ",
                $out_jsons[1],".\n";
        }
    } ## end if 'G'
    else {
        print "item_type ${item_type}  not yet implemented.\n";
    }
} ## end get_item_info()

=item get_template

    $template = get_template($prompt, $mc_path);

Prompt for an item or block template.

=cut
    
sub get_template
{
    my $prompt = $_[0];
    my $mc_path = $_[1];
    my $resp; 
    my $template = 0;
    my $stem;

    while (! $template) 
    {
        print $prompt;
        $resp = <STDIN>;
        chomp($resp);
        $stem = $resp;
        $template = File::Spec->catfile($mc_path, $resp);
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

=item get_target_info

=cut

sub get_simple_item_json
{
    my $prompt = $_[0];
    my $outpath = $_[1];
    my $json;
    my $resp;

    print $prompt;
    $resp = <STDIN>;
    chomp($resp);
    $json = File::Spec->catfile($outpath, $resp);
    $json .= '.json';
    return ($resp, $json,);
} ## end get_simple_item_json()


=back

=head1 HISTORY


=cut
