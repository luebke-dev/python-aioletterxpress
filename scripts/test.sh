#!/bin/bash
set -e
set -x

PYTHONPATH=. pytest --cov-config=.coveragerc --cov=aioletterxpress --cov-report=term-missing tests "${@}"
