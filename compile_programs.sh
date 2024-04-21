#!/usr/bin/env bash

# This script compiles all $PROGRAMS_FOLDER programs to mir
PROGRAMS_FOLDER="programs"
COMPILED_PROGRAMS_FOLDER="programs-compiled"

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}" 2>/dev/null)" && pwd -P)"
TARGET_PATH="${SCRIPT_PATH}/${COMPILED_PROGRAMS_FOLDER}"
PROGRAMS_PATH="${SCRIPT_PATH}/${PROGRAMS_FOLDER}"

PYNADAC="pynadac"

cd "${PROGRAMS_PATH}" || exit 1

for file in *.py ; do
  echo "Compiling ${file}"
  "$PYNADAC" --target-dir "${TARGET_PATH}" \
    --generate-mir-json \
    "${file}"
done 

echo "------------------------"
echo "Compiled programs: all files in the programs directory were compiled to mir: [$TARGET_PATH]"

