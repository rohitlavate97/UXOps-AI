#!/bin/bash

cd "$(dirname "$0")"

agy \
  --dangerously-skip-permissions \
  --project=my-project
