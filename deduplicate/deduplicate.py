import click
import vpype as vp


@click.command()
@vp.generator
def deduplicate():
    """
    Insert documentation here...
    """
    lc = vp.LineCollection()
    return lc


deduplicate.help_group = "Plugins"
