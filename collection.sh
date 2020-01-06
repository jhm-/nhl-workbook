#!/bin/bash
# Copyright © 2015-2019 Jack Morton (jhm@jemscout.com)

docroot="http://www.nhl.com/scores/htmlreports"

# Each team plays 41 home games and 41 away games.
# The 2012-2013 NHL lockout season had only 720 games played in total.
# With the introduction of the Golden Knights in 2017, the total number of NHL
# games has gone up from 1,230 to 1,271.
for i in {17..18}
do
  x=0$((i))
  y=0$((i+1))
  dir="20${x: -2}-20${y: -2}"

  echo -e "\n-> building directory tree for $dir"
  mkdir -p $dir/roster $dir/summary $dir/events $dir/face-offs $dir/play \
    $dir/shots $dir/toi $dir/toi/home $dir/toi/visitor

  echo "-> collecting documents"
  for p in {1..1271}
  do
    n=000$((p))
    # roster
    wget -P $dir/roster -nc -q \
      "$docroot/20${x: -2}20${y: -2}/RO02${n: -4}.HTM" || continue
    # summmary
    wget -P $dir/summary -nc -q \
      "$docroot/20${x: -2}20${y: -2}/GS02${n: -4}.HTM" || continue
    # events
    wget -P $dir/events -nc -q \
      "$docroot/20${x: -2}20${y: -2}/ES02${n: -4}.HTM" || continue
    # face-offs
    wget -P $dir/face-offs -nc -q \
      "$docroot/20${x: -2}20${y: -2}/FS02${n: -4}.HTM" || continue
    # play-by-plays
    wget -P $dir/play -nc -q \
      "$docroot/20${x: -2}20${y: -2}/PL02${n: -4}.HTM" || continue
    # shots
    wget -P $dir/shots -nc -q \
      "$docroot/20${x: -2}20${y: -2}/SS02${n: -4}.HTM" || continue
    # home team time-on-ice
    wget -P $dir/toi/home -nc -q \
      "$docroot/20${x: -2}20${y: -2}/TH02${n: -4}.HTM" || continue
    # visitor team time-on-ice
    wget -P $dir/toi/visitor -nc -q  \
      "$docroot/20${x: -2}20${y: -2}/TV02${n: -4}.HTM" || continue
    echo -n "."
  done
done
echo -e "\n-> done"
