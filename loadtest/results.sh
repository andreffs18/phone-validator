#!/bin/bash
DATE="2023-03-21"
# DATE=$(date '+%Y-%m-%d')

for MODE in "in_memory" "trie" "mongo" "postgres_async" "redis"
do
    # Print RPS, P95 and Total Requests once finished
    for file in loadtest/$DATE/$MODE/*.txt
    do
        echo $file
        cat $file | sed -n -e 7p -e 32p -e 43p -e 47p -e 48p
        echo ""
    done
done
