#!/bin/bash

args="$@"

# Check if the build output directory exists
if [ ! -d "/tmp/build_output" ]; then
  # Create the directory
  mkdir -p "/tmp/build_output"
fi

# Run container
docker run -e USER="$(id -u)" -u="$(id -u)" \
  -v ~/summpods:/src/workspace \
  -v /tmp/build_output:/tmp/build_output \
  -p 80:5000 \
  -w /src/workspace gcr.io/bazel-public/bazel:latest \
  --output_user_root=/tmp/build_output \
  $args
