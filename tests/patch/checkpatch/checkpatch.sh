#!/bin/bash
# SPDX-License-Identifier: GPL-2.0
#
# Copyright (C) 2019 Netronome Systems, Inc.

IGNORED=\
COMMIT_LOG_LONG_LINE,\
MACRO_ARG_REUSE,\
ALLOC_SIZEOF_STRUCT,\
NO_AUTHOR_SIGN_OFF

tmpfile=$(mktemp)

./scripts/checkpatch.pl --strict --ignore=$IGNORED -g HEAD | tee $tmpfile

grep '0 errors, 0 warnings, 0 checks' $tmpfile
ret=$?

rm $tmpfile

exit $ret

# ./scripts/checkpatch.pl --ignore=SPACING_CAST,LONG_LINE,LONG_LINE_COMMENT,LONG_LINE_STRING,LINE_SPACING_STRUCT,FILE_PATH_CHANGES,CAMELCASE,OPEN_ENDED_LINE,AVOID_EXTERNS_HEADER,UNCOMMENTED_DEFINITION
