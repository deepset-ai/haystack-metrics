import os

import click
from github import Github, Auth


@click.group("github")
@click.option('--token', default="")
@click.pass_context
def github_cli(ctx, token):
    ctx.ensure_object(dict)
    token = token or os.environ.get("GITHUB_TOKEN")
    if token:
        ctx.obj['GITHUB_AUTH'] = Auth.Token(token)


@github_cli.command()
@click.argument('repo_name')
@click.pass_context
def stars(ctx, repo_name):
    auth = ctx.obj.get('GITHUB_AUTH')
    g = Github(auth=auth)
    click.echo(g.get_repo(repo_name).stargazers_count)
    # try:
    #     r = requests.get("http://localhost:1416/status")
    # except ConnectionError:
    #     click.echo("Hayhooks server is not responding. To start one, run `hayooks run`")
    #     return

    # if r.status_code >= 400:
    #     body = r.json()
    #     click.echo(f"Hayhooks server is unhealty: [{r.status_code}] {r. json().get('detail')}")
    #     return

    # click.echo("Hayhooks server is up and running.")
    # body = r.json()
    # if pipes := body.get("pipelines"):
    #     click.echo("\nPipelines deployed:")
    #     for p in pipes:
    #         click.echo(f"- {p}")
