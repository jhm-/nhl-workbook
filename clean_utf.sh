#!/bin/bash
# Copyright © 2015 Jack Morton (jhm@jemscout.com)

FOLDERS=( events face-offs play roster shots summary toi/home toi/visitor )

for f in "${FOLDERS[@]}"
do
  echo "-> $f"
  FILES="$1/$f/*.HTM"
  for i in $FILES
  do
 	mv $i $i.old
  	sed 's/UTF-16/UTF-8/g' $i.old > $i
  	rm -f $i.old
  	echo -n '.'
  done
  echo -e "\n"
done
