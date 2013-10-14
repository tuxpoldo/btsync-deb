#!/bin/bash
pushd btsync-common
make -f debian/rules  get-orig-source
popd

