
=head1 NAME

generator.pm - common variables and functions used by gen_*.pl scripts.

=head1 SYNOPSIS

use FindBin;
use lib "$FindBin::Bin";
use generator;

=head1 DESCRIPTION

=cut

package generator
require Exporter

use strict;
use warnings;

our @ISA = qw( Exporter );

our @EXPORT = qw( 
    get_response check_repeat get_simple_json_path
    $MC_ASSETS $MC_BLOCKSTATE_PATH $MC_BLOCK_MODEL_PATH $MC_ITEM_MODEL_PATH
);

our @EXPORT_OK = qw();

our %EXPORT_TAGS = ();

# constants to be re-defined when necessary
# where are the vanilla assets?
our $MC_ASSETS = File::Spec->catdir($ENV{HOME},
                        "/Projects/Minecraft_1.15/vanilla/assets/minecraft");
our $MC_BLOCKSTATE_PATH = "${MC_ASSETS}/blockstates";
our $MC_BLOCK_MODEL_PATH = "${MC_ASSETS}/models/block";
our $MC_ITEM_MODEL_PATH = "${MC_ASSETS}/models/item";

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


=item get_simple_json_path

Just get the thing's name and make a .json file.

Returns: list of (name, full path to json).

=cut

sub get_simple_json_path
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

############ MANDATORY 1 ############
1;

__END__

=back

=head1 HISTORY

=cut

