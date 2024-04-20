import os
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

import click
from datadog import initialize
from datadog import api as dd


@click.group("twitter")
@click.option("--chrome-path")
@click.option('--username', default="Haystack_AI")
@click.option('--dd-api-key', default="")
@click.option('--dd-api-host', default="https://api.datadoghq.eu")
@click.option('--dry-run', default=False, is_flag=True)
@click.pass_context
def twitter_scraper(ctx, chrome_path, username, dd_api_key, dd_api_host, dry_run):
    ctx.ensure_object(dict)
    ctx.obj['DRY_RUN'] = dry_run
    ctx.obj['DEFAULT_TAGS'] = ["type:health", "source:twitter", f"username:{username}"]

    options = ChromeOptions()
    options.headless = True
    if chrome_path:
        options.binary_location = chrome_path
    target_url = f"https://twitter.com/{username}"
    driver = webdriver.Chrome(options=options)
    driver.get(target_url)
    time.sleep(10)
    response = driver.page_source
    driver.close()

    try:
        follower_count_element_idx = response.find('<a href="/Haystack_AI/verified_followers"')
        ctx.obj["FOLLOWERS"] = find_next_match(response, follower_count_element_idx, r'>\d{3,}<')[1:-1]
    except:
        ctx.obj["FOLLOWERS"] = 0

    dd_api_key = dd_api_key or os.environ.get("DD_API_KEY")
    if dd_api_key:
        initialize(api_key=dd_api_key, api_host=dd_api_host)


@twitter_scraper.command()
@click.pass_context
def followers(ctx):
    followers = ctx.obj.get('FOLLOWERS')
    if not ctx.obj.get('DRY_RUN'):
        dd.Metric.send(
            metric="haystack.twitter.followers",
            points=[(time.time(), int(followers))],
            tags=ctx.obj.get('DEFAULT_TAGS'),
        )

    click.echo(followers)


def find_next_match(text, start_index, pattern):
    # Use re.search() to find the next match
    match = re.search(pattern, text[start_index:])

    if match:
        # Adjust the start position by adding the start_index
        start_pos = match.start() + start_index
        end_pos = match.end() + start_index
        return text[start_pos:end_pos]
    else:
        raise RuntimeError("No match found")
