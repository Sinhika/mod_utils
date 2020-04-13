
=head1 NAME

generator.pm - common variables and functions used by gen_*.pl scripts.

=head1 SYNOPSIS

use FindBin;
use lib "$FindBin::Bin";
use generator;

=head1 DESCRIPTION

=cut

package generator;

require Exporter;

use strict;
use warnings;

our @ISA = qw( Exporter );

our @EXPORT = qw( 
    get_response check_repeat get_simple_json_path get_template
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

=item B<get_response>

Print a prompt, read response from STDIN.

Returns: response, stripped of EOL.

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

=item B<check_repeat>

Print prompt and check response for 'Yes'-like answer.

Returns: 1 on yes, 0 on not-yes

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


=item B<get_simple_json_path>

Just get the thing's name and make a .json pathname.

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


=item B<get_template>
 
 $template = get_template($stem, $mc_path);

given the filename stem, assemble a pathname to the template json
and check that it exists.

Returns: full path to template json, or undef if not readable.

=cut

sub get_template
{
    my ($stem, $mc_path) = @_;
    my $template = File::Spec->catfile($mc_path, $stem);
    if ($template !~ /\.json$/) {
        $template .= '.json';
    }
    if ( ! -r $template ) {
        warn "${template} does not exist or is not readable!\n";
        $template = undef;
    }
    return $template;
} ## end sub get_template

=item B<get_template_prompt>

    $template = get_template($prompt, $mc_path);

Prompt for an item or block template.

Returns: list of ($stem, $template).

=cut
    
sub get_template_prompt
{
    my $prompt = $_[0];
    my $mc_path = $_[1];
    my $template = undef;
    my $stem;

    while (not defined $template) 
    {
        $stem = get_response($prompt);
        $template = get_template($stem, $mc_path);
    } ## end-while
    return ($stem, $template);
} ## end get_template_prompt()


############ MANDATORY 1 ############
1;

__END__

=back

=head1 HISTORY

=cut

