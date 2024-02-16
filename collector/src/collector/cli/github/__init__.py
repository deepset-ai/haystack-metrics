import os
import time

import click
from datadog import initialize
from datadog import api as dd
from github import Github, Auth


DEFAULT_TAGS = ["type:health", "source:github"]


@click.group("github")
@click.option('--repo-name', default="deepset-ai/haystack")
@click.option('--gh-token', default="")
@click.option('--dd-api-key', default="")
@click.option('--dd-api-host', default="https://api.datadoghq.eu")
@click.option('--dry-run', default=False, is_flag=True)
@click.pass_context
def github_cli(ctx, repo_name, gh_token, dd_api_key, dd_api_host, dry_run):
    ctx.ensure_object(dict)
    ctx.obj['DRY_RUN'] = dry_run

    gh_token = gh_token or os.environ.get("GITHUB_TOKEN")
    if gh_token:
        g = Github(auth=Auth.Token(gh_token))
        ctx.obj['REPO'] = g.get_repo(repo_name)

    dd_api_key = dd_api_key or os.environ.get("DD_API_KEY")
    if dd_api_key:
        initialize(api_key=dd_api_key, api_host=dd_api_host)


@github_cli.command()
@click.pass_context
def stars(ctx):
    stars = ctx.obj.get('REPO').stargazers_count
    if not ctx.obj.get('DRY_RUN'):
        dd.Metric.send(metric="haystack.github.stars", points=[(time.time(), int(stars))], tags=DEFAULT_TAGS)

    click.echo(stars)


@github_cli.command()
@click.pass_context
def referrers(ctx):
    metrics = []
    output = []
    for ref in ctx.obj.get('REPO').get_top_referrers():
        metrics.append(
            {
                "metric": "haystack.github.referrers",
                "type": "count",
                "tags": DEFAULT_TAGS + [ref.referrer],
                'points': [(time.time(), ref.uniques)],
            }
        )
        output.append(f"{ref.referrer} {ref.uniques}")

    if not ctx.obj.get('DRY_RUN'):
        dd.Metric.send(metrics=metrics)

    click.echo("\n".join(output))


@github_cli.command()
@click.pass_context
def clones(ctx):
    # Daily clones
    stats = ctx.obj.get('REPO').get_clones_traffic()
    if not ctx.obj.get('DRY_RUN'):
        dd.Metric.send(metric="haystack.github.clones", points=[(time.time(), int(stats["count"]))], tags=DEFAULT_TAGS)
    click.echo(stats["count"])


@github_cli.command()
@click.pass_context
def views(ctx):
    # Daily views
    stats = ctx.obj.get('REPO').get_views_traffic()
    if not ctx.obj.get('DRY_RUN'):
        dd.Metric.send(metric="haystack.github.views", points=[(time.time(), int(stats["count"]))], tags=DEFAULT_TAGS)
    click.echo(stats["count"])
