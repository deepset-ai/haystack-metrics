# SPDX-FileCopyrightText: 2024-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
import click

from collector.__about__ import __version__
from .github import github_cli


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="collector")
def collector():
    pass


collector.add_command(github_cli)
