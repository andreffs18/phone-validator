#!/bin/bash
# Load testing each solution takes 60 seconds per 4 clients * 3 inputs = 12 minutes
# Between each load test we wait 60 seconds to distinguish tests in grafana = 12 minutes
# Each solution takes 60 seconds to initialize = 1 minute
# So 12 + 12 + 1 = 25 minutes per solution
# 5 solutions * 25 minutes = 1h25mins to run full load test

DATE=$(date '+%Y-%m-%d')

for MODE in "in_memory" "trie" "mongo" "postgres_async" "redis"
do
    mkdir -p loadtest/$DATE/$MODE;
    echo "👀 Starting \"$MODE\" load test..."
    echo "BACKEND=backend.$MODE" > .env
    source .env
    docker-compose --env-file .env up -d
    echo "Sleeping for 60 to let server bootstrap"
    sleep 60

    ANNOTATION_ID=$(curl -X POST http://localhost:3000/api/annotations -u "admin:password" -H "Accept: application/json" -H "Content-Type: application/json" --data-raw "{\"dashboardUID\":\"uFoisl0Vjk\",\"time\":$(date +%s000),\"tags\":[\"backend.$MODE\"],\"text\":\"Load test for 'backend.$MODE' backend\"}" | jq '.id')

    for number in "+1983248" "+344999813123" "+6983248"
    do
        for clients in 1 2 4 8
        do
            echo "Running for 60seconds '-c $clients' for '$number' ..."
            hey -z 60s -c $clients -t 60 -m POST -H "Content-Type: application/json" -d "[\"$number\"]" http://localhost:8080/aggregate > loadtest/$DATE/$MODE/output-c$clients-$number.txt
            echo "Sleeping for 60"

            PROCESS_VIRTUAL_MEMORY_BYTES=$(curl -s http://localhost:8080/metrics | grep "process_virtual_memory_bytes" | tail -n1 | cut -d ' ' -f 2)
            PROCESS_RESIDENT_MEMORY_BYTES=$(curl -s http://localhost:8080/metrics | grep "process_resident_memory_bytes" | tail -n1 | cut -d ' ' -f 2)
            echo "process_virtual_memory_bytes $PROCESS_VIRTUAL_MEMORY_BYTES" >> loadtest/$DATE/$MODE/output-c$clients-$number.txt
            echo "process_resident_memory_bytes $PROCESS_RESIDENT_MEMORY_BYTES" >> loadtest/$DATE/$MODE/output-c$clients-$number.txt

            sleep 60
        done
    done

    # Print RPS, P95 and Total Requests once finished
    for file in loadtest/$DATE/$MODE/*.txt; do
        echo $file
        cat $file | sed -n -e 7p -e 32p -e 43p -e 47p -e 48
        echo ""
    done

    curl -X PATCH http://localhost:3000/api/annotations/$ANNOTATION_ID -u "admin:password" -H "Content-Type: application/json" --data-raw "{\"timeEnd\":$(date +%s000)}"
done
