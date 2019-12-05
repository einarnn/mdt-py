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

#
# simple function to check for existence of a binary on the current
# path
#
checkExists() {
    bin=`command -v $1`
    if [ -z "$bin" ]
    then
	echo this script requires $1 to be on your path
	exit 1
    fi
}

#
# check we have executables we need
#
checkExists protoc

# Generate dialout code
python -m grpc_tools.protoc \
    -I$PROTO_ARCHIVE/mdt_grpc_dialout \
    --python_out=. \
    --python_grpc_out=. \
    $PROTO_ARCHIVE/mdt_grpc_dialout/mdt_grpc_dialout.proto

# Generate Telemetry message code
python -m grpc_tools.protoc \
    -I$PROTO_ARCHIVE \
    --python_out=. \
    --python_grpc_out=. \
    $PROTO_ARCHIVE/telemetry.proto
