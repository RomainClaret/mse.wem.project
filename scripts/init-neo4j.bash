#!/usr/bin/env bash

DOCKER_CONTAINR=wem-neo4j

docker cp ./data ${DOCKER_CONTAINR}:/var/lib/neo4j/import/neo4j-data
cat populate-neo4j.cypher | docker exec -i ${DOCKER_CONTAINR} cypher-shell --fail-fast
