#!/bin/bash

cd "/mnt/c/Users/Gboluwaga Akinleye/Documents/AWS project/bigdatapipeline" || exit

for i in {1..10}; do
    echo "// Auto commit $i - $(date)" >> dummy.txt
    git add .
    git commit -m "Automated commit $i: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin master

    # Sleep pattern: 20, 15, 40 min repeating
    mod=$(( i % 3 ))
    if [ "$mod" -eq 1 ]; then
        sleep_time=$((20 * 60))
    elif [ "$mod" -eq 2 ]; then
        sleep_time=$((15 * 60))
    else
        sleep_time=$((40 * 60))
    fi

    # Don't sleep after the last iteration
    if [ "$i" -lt 10 ]; then
        sleep "$sleep_time"
    fi
done
