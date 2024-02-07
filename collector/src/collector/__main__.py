# SPDX-FileCopyrightText: 2024-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
import sys

if __name__ == "__main__":
    from collector.cli import collector

    sys.exit(collector())
