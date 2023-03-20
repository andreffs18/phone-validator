#!/bin/bash
# Load testing each solution takes 60 seconds per 4 clients * 3 inputs = 12 minutes
# Between each load test we wait 60 seconds to distinguish tests in grafana = 12 minutes
# Each solution takes 60 seconds to initialize = 1 minute
# So 12 + 12 + 1 = 25 minutes per solution
# 5 solutions * 25 minutes = 1h25mins to run full load test

DATE=$(date '+%Y-%m-%d')

# for MODE in "in_memory" "trie" "mongo" "postgres" "redis"
for MODE in "postgres" "postgres_async" "postgres_async_singleton" "postgres_async_pool"
do
    mkdir -p loadtest/$DATE/$MODE;
    echo "👀 Starting \"$MODE\" load test..."
    echo "BACKEND=backend.$MODE" > .env
    source .env
    docker-compose --env-file .env up -d
    echo "Sleeping for 60 to let server bootstrap"
    sleep 60

    for number in "+1983248" "+344999813123" "+6983248"
    do
        for clients in 1 2 4 8
        do
            echo "Running for 60seconds '-c $clients' for '$number' ..."
            hey -z 60s -c $clients -t 0 -m POST -H "Content-Type: application/json" -d  "[\"$number\"]" http://localhost:8080/aggregate > loadtest/$DATE/$MODE/output-c$clients-$number.txt
            echo "Sleeping for 60"
            sleep 60
        done
    done

    # Print once finished
    for file in loadtest/$DATE/$MODE/*.txt; do
        echo $file
        cat $file | sed -n -e 7p -e 32p -e 43p
        echo ""
    done

done
