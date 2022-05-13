#!/usr/bin/env bash
# Copyright 2022 Omnivector Solutions LLC
# See LICENSE file for licensing details.

set -euo pipefail

GO_VERSION="1.18.2"
GO_TARBALL="go$GO_VERSION.linux-amd64.tar.gz"
GO_URL="https://go.dev/dl/$GO_TARBALL"

REPO="https://github.com/vpenso/prometheus-slurm-exporter.git"
BIN="prometheus-slurm-exporter"

# container name
CONTAINER="centos-builder-$RANDOM"

echo "Creating CentOS7 container $CONTAINER"
lxc launch images:centos/7/amd64 $CONTAINER
sleep 3 # wait a bit until container is ready

echo "Installing dependencies"
lxc exec $CONTAINER -- yum makecache
lxc exec $CONTAINER -- yum install -y git tar wget

echo "Downloading Go $GO_VERSION"
lxc exec $CONTAINER -- wget $GO_URL
echo "Extracting $GO_TARBALL"
lxc exec $CONTAINER -- tar -C /usr/local -xzf $GO_TARBALL

echo "Cloning repo"
lxc exec $CONTAINER -- git clone $REPO

echo "Compiling code"
lxc exec $CONTAINER --env "PATH=$PATH:/usr/local/go/bin" \
	            --cwd "/root/prometheus-slurm-exporter" \
	            -- go build -v

echo "Getting binary"
lxc file pull "$CONTAINER/root/prometheus-slurm-exporter/$BIN" .

echo "Creating tarball"
tar cvzf slurm-exporter.tar.gz "$BIN"

echo "Cleaning up"
lxc delete --force $CONTAINER
rm "$BIN"
