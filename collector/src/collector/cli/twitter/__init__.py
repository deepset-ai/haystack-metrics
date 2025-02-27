import os
import re
import time

import click
from datadog import api as dd
from datadog import initialize
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


@click.group("twitter")
@click.option('--username', default="Haystack_AI")
@click.option('--dd-api-key', default="")
@click.option('--dd-api-host', default="https://api.datadoghq.eu")
@click.option('--dry-run', default=False, is_flag=True)
@click.pass_context
def twitter_scraper(ctx, username, dd_api_key, dd_api_host, dry_run):
    ctx.ensure_object(dict)
    ctx.obj['DRY_RUN'] = dry_run
    ctx.obj['DEFAULT_TAGS'] = ["type:health", "source:twitter", f"username:{username}"]

    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    target_url = f"https://twitter.com/{username}"
    driver = webdriver.Chrome(options=options)
    driver.get(target_url)
    time.sleep(10)
    response = driver.page_source
    driver.close()

    try:
        follower_count_element_idx = response.find('<a href="/Haystack_AI/verified_followers"')
        ctx.obj["FOLLOWERS"] = find_next_match(response, follower_count_element_idx, r'>[\d,]+<')[1:-1]
    except:
        ctx.obj["FOLLOWERS"] = 0

    dd_api_key = dd_api_key or os.environ.get("DD_API_KEY")
    if dd_api_key:
        initialize(api_key=dd_api_key, api_host=dd_api_host)


@twitter_scraper.command()
@click.pass_context
def followers(ctx):
    followers = ctx.obj.get('FOLLOWERS')
    if followers:
        followers = followers.replace(',', '')
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
