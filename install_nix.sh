#!/bin/bash

# set -e
set -x

echo "Installing Nix package manager..."
sh <(curl -L https://nixos.org/nix/install) --daemon

echo "Sourcing Nix..."
. /root/.nix-profile/etc/profile.d/nix.sh

echo "Running Nix Develop..."
nix develop
