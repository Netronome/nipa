#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
#
# Copyright (C) 2019 Netronome Systems, Inc.

"""Command line interface for reading from a mdir

Script providing an ability to test local patch series.
On single patch series is expected as generated by git format-patch.
"""

import argparse
import configparser
import os
import re

import core
from core import Patch
from core import Series
from core import Tree
from core import Tester

config = configparser.ConfigParser()
config.read(['nipa.config', "mdir.config"])

results_dir = config.get('results', 'dir',
                         fallback=os.path.join(core.NIPA_DIR, "results"))

# TODO: use config
parser = argparse.ArgumentParser()
parser.add_argument('--mdir', required=True,
                    help='path to the directory with the patches')
parser.add_argument('--tree', required=True,
                    help='path to the tree to test on')
parser.add_argument('--tree-name', default='net-next',
                    help='the tree name to expect')
parser.add_argument('--tree-branch', default='master',
                    help='the branch or commit to use as a base for applying patches')
parser.add_argument('--result-dir', default=results_dir,
                    help='the directory where results will be generated')
args = parser.parse_args()

args.mdir = os.path.abspath(args.mdir)
args.tree = os.path.abspath(args.tree)

core.log_open_sec("Loading patches")
try:
    files = [os.path.join(args.mdir, f) for f in sorted(os.listdir(args.mdir))]
    series = Series()

    for f in files:
        with open(f, 'r') as fp:
            data = fp.read()
            if re.search(r"\[.* 0+/\d.*\]", data) and \
               not re.search(r"\n@@ -\d", data):
                series.set_cover_letter(data)
            else:
                series.add_patch(Patch(data))
finally:
    core.log_end_sec()

tree = Tree(args.tree_name, args.tree_name, args.tree, branch=args.tree_branch)
tester = Tester(args.result_dir)

if not tree.check_applies(series):
    print("Patch series does not apply cleanly to the tree")
    os.sys.exit(1)

series_ret, patch_ret = tester.test_series(tree, series)
good_patch = 0
for one_patch in patch_ret:
    if len(one_patch) == sum(one_patch):
        good_patch += 1

print("%d patches, %d/%d series tests passed, %d/%d patches passed all tests" %
      (len(series.patches),
       sum(series_ret), len(series_ret),
       good_patch, len(patch_ret)))
os.sys.exit(0)
