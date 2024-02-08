import json

import click
import pypistats


@click.group("pypi")
def pypi_cli():
    pass


@pypi_cli.command()
@click.argument('package_name')
@click.argument('timeframe', default="last_day")
def downloads(package_name, timeframe):
    stats = json.loads(pypistats.recent(package_name, format="json"))
    click.echo(stats["data"][timeframe])
