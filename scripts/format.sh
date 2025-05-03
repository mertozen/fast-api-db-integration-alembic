#!/bin/sh -e
set -x

ruff check ../ scripts --fix
ruff format ../ scripts
