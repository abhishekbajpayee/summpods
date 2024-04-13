#!/bin/bash

args="$@"

# Check if the build output directory exists
if [ ! -d "/tmp/build_output" ]; then
  # Create the directory
  mkdir -p "/tmp/build_output"
  mkdir -p "/tmp/build_output/logs"
fi

# Build container using dockerfile
docker build -t build_image .

# Run container by running:
# 1. mongodb server
# 2. bazel target
docker run -e USER="$(id -u)" -u="$(id -u)" \
  -v ~/summpods:/src/workspace \
  -v ~/db:/data/db \
  -v /tmp/build_output:/tmp/build_output \
  -v ~/.secrets:/.secrets \
  -p 80:5000 \
  -w /src/workspace \
  build_image \
  "supervisord -c /src/workspace/src/conf/supervisord.conf && \
   bazel --output_user_root=/tmp/build_output $args"
