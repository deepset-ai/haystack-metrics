import os
import time

import click
import requests
from datadog import api as dd
from datadog import initialize


@click.group("docker")
@click.option("--repo-name", default="deepset/haystack")
@click.option("--dd-api-key", default="")
@click.option("--dd-api-host", default="https://api.datadoghq.eu")
@click.option("--dry-run", default=False, is_flag=True)
@click.pass_context
def docker_cli(ctx, repo_name, dd_api_key, dd_api_host, dry_run):
    ctx.ensure_object(dict)
    ctx.obj["DRY_RUN"] = dry_run
    ctx.obj["DEFAULT_TAGS"] = ["type:health", "source:docker", f"repo:{repo_name}"]
    ctx.obj["REPO_NAME"] = repo_name
    dd_api_key = dd_api_key or os.environ.get("DD_API_KEY")
    if dd_api_key:
        initialize(api_key=dd_api_key, api_host=dd_api_host)


@docker_cli.command()
@click.pass_context
def pulls(ctx):
    repo_name = ctx.obj.get("REPO_NAME")
    stats = requests.get(f"https://hub.docker.com/v2/repositories/{repo_name}", timeout=3).json()
    pulls = stats["pull_count"]

    if not ctx.obj.get("DRY_RUN"):
        dd.Metric.send(
            metric="haystack.github.stars", points=[(time.time(), int(pulls))], tags=ctx.obj.get("DEFAULT_TAGS")
        )

    click.echo(pulls)
