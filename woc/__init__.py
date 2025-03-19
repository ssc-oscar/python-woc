#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-01-17

"""
# To Use
.. include:: ../README.md
   :start-line: 4
   :end-before: ## Contributing
# Guide (Local)
.. include:: ../docs/guide.md
# Guide (Remote)
.. include:: ../docs/guide_remote.md
# To Contribute
.. include:: ../docs/contributing.md
# World of Code Tutorial
.. include:: ../docs/tutorial.md
# World of Code DataFormat
.. include:: ../docs/DataFormat.md

"""  # noqa: D205

__all__ = ["local", "tch", "detect", "objects", "remote"]

import importlib.metadata

__version__ = importlib.metadata.version("python-woc")
