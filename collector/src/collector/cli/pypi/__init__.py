from datetime import date, timedelta
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
    if timeframe == "last_day":  # Use pypistats.overall because .recent daily numbers don't sum up to monthly total
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        stats = json.loads(
            pypistats.overall(
                package_name, format="json", start_date=yesterday, end_date=yesterday, mirrors=False
            )
        )
        click.echo(stats["data"][0]["downloads"])
    else:
        stats = json.loads(pypistats.recent(package_name, format="json"))
        click.echo(stats["data"][timeframe])
