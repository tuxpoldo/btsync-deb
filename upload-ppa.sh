#!/bin/bash

for dist in trusty; do
	git reset --hard
	git clean -f -d -x
	find . -name "changelog" -type f -print0 | xargs -0 sed -i 's/unstable;/$dist;/g'
	bash make-all-srcs.sh
	for file in *.changes
	do
		dput ppa:silvenga/btsync $file
	done
	git reset --hard
	git clean -f -d -x
done 


