# SPDX-License-Identifier: GPL-2.0
#
# Copyright (C) 2019 Netronome Systems, Inc.

""" Test representation """
# TODO: document

import importlib
import json
import os

import core
import core.cmd as CMD


class Test(object):
    """Test class

    """

    def __init__(self, path, name):
        self.path = path
        self.name = name

        core.log_open_sec("Test %s init" % (self.name, ))

        self._info_load()

        # Load dynamically the python func
        if "pymod" in self.info:
            test_group = os.path.basename(os.path.dirname(path))
            m = importlib.import_module("tests.%s.%s.%s" %
                                        (test_group, name,
                                         self.info["pymod"]))
            self._exec_pyfunc = getattr(m, self.info["pyfunc"])
        core.log_end_sec()

    def _info_load(self):
        with open(os.path.join(self.path, 'info.json'), 'r') as fp:
            self.info = json.load(fp)
        core.log("Info file", json.dumps(self.info, indent=2))

    def is_disabled(self):
        return "disabled" in self.info and self.info["disabled"]

    def prep(self):
        if "prep" not in self.info or self.is_disabled():
            return
        core.log_open_sec("Preparing for test %s" % (self.name,))
        CMD.cmd_run(os.path.join(self.path, self.info["prep"]))
        core.log_end_sec()

    def exec(self, tree, thing, result_dir):
        if self.is_disabled():
            core.log(f"Skipping test {self.name} - disabled", "")
            return True

        core.log_open_sec(f"Running test {self.name}")

        test_dir = os.path.join(result_dir, self.name)
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        retcode, out, err = self._exec(tree, thing, result_dir)

        # Write out the results
        with open(os.path.join(test_dir, "retcode"), "w+") as fp:
            fp.write(str(retcode))
        with open(os.path.join(test_dir, "stdout"), "w+") as fp:
            fp.write(out)
        with open(os.path.join(test_dir, "stderr"), "w+") as fp:
            fp.write(err)
        with open(os.path.join(test_dir, "summary"), "w+") as fp:
            fp.write("==========\n")
            if retcode == 0:
                fp.write("%s - OKAY\n" % (self.name, ))
            else:
                fp.write("%s - FAILED\n" % (self.name,))
                fp.write("\n")
                if err.strip():
                    if err[:-1] != '\n':
                        err += '\n'
                    fp.write(err)
                elif out.strip():
                    if out[:-1] != '\n':
                        out += '\n'
                    fp.write(out)

        core.log_end_sec()

        return retcode == 0

    def _exec(self, tree, thing, result_dir):
        if "run" in self.info:
            return self._exec_run(tree, thing, result_dir)
        elif "pymod" in self.info:
            return self._exec_pyfunc(tree, thing, result_dir)

    def _exec_run(self, tree, thing, result_dir):
        retcode = 0
        try:
            out, err = CMD.cmd_run(os.path.join(self.path, self.info["run"]),
                                   include_stderr=True)
        except core.cmd.CmdError as e:
            retcode = e.retcode
            out = e.stdout
            err = e.stderr

        return retcode, out, err
