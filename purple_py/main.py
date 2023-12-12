from db import (
    load_events_into_weaviate,
    load_neo4j_data,
)
from dotenv import load_dotenv
import os
from parse import parse_event_json
from purple_py.db import client


load_dotenv()

# download events in strfry
# strfry router strfry-router.config


# load events into weaviate
# create_weaviate_event_class(client)
# create_weaviate_user_class(client)
# load_events_into_weaviate(client)

# export events as json
# ./strfry export dbdump.jsonl

# load data into neo4j
STRFRY_PATH = os.getenv("STRFRY_DB_FOLDER")
parse_event_json(os.path.join(STRFRY_PATH, "dbdump.jsonl"))

#  echo ':source neo4j-import/constraints.cypher' | cypher-shell -u neo4j -p neo4j
load_neo4j_data()

# python app.py
