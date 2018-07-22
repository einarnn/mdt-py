#!/bin/sh
#
# Copyright (c) 2018 Cisco
#
# Generate Python code from telemetry and dialout proto files
#
PROTO_ARCHIVE=/opt/git-repos/bigmuddy-network-telemetry-proto/proto_archive

# Check the directory exists
if [ ! -d "$PROTO_ARCHIVE" ]; then
    echo PROTO_ARCHIVE directory $PROTO_ARCHIVE does not exist
    exit 1
fi

# Generate dialout code
python -m grpc_tools.protoc \
    -I$PROTO_ARCHIVE/mdt_grpc_dialout \
    --python_out=. \
    --grpc_python_out=. \
    $PROTO_ARCHIVE/mdt_grpc_dialout/mdt_grpc_dialout.proto

# Generate Telemetry message code
python -m grpc_tools.protoc \
    -I$PROTO_ARCHIVE \
    --python_out=. \
    --grpc_python_out=. \
    $PROTO_ARCHIVE/telemetry.proto
