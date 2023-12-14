import os
from purple_py.db import (
    client,
    create_weaviate_event_class,
    create_weaviate_user_class,
    load_events_into_weaviate,
    load_neo4j_data,
)
from purple_py.parse import parse_event_json


# download events in strfry
# strfry router strfry-router.config

# start weaviate docker container
# docker compose up -d && docker compose logs -f weaviate

# load events into weaviate
create_weaviate_event_class(client)
create_weaviate_user_class(client)
load_events_into_weaviate(client)

# export events as json
# ./strfry export dbdump.jsonl

# load data into neo4j
# STRFRY_PATH = os.getenv("STRFRY_DB_FOLDER")
# parse_event_json(os.path.join(STRFRY_PATH, "dbdump.jsonl"))

#  echo ':source neo4j-import/constraints.cypher' | cypher-shell -u neo4j -p neo4j
# load_neo4j_data()

# python app.py
