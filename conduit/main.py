import os
import sys

try:
    from conduit.config import STRFRY_PATH
except ModuleNotFoundError:
    print("Run with command: python -m conduit.main")
    sys.exit()

from conduit.db import (
    client,
    create_weaviate_event_class,
    create_weaviate_user_class,
    load_events_into_weaviate,
    load_neo4j_data,
)
from conduit.parse import parse_event_json

print("Errors logged in 'logfile.log'")
# These commented commands need to be run before executing the python code
# download events in strfry
# `strfry router strfry-router.config`

# export events as json for neo4j
# `strfry export dbdump.jsonl`

# start weaviate docker container
# `docker compose up -d``

# load events into weaviate
create_weaviate_event_class(client)
create_weaviate_user_class(client)
load_events_into_weaviate(client)

# load data into neo4j
parse_event_json(os.path.join(STRFRY_PATH, "dbdump.jsonl"))

# loads follows, mentions, reactions, replys, users into neo4j
load_neo4j_data()

# cd [path/to/conduit]
print("Start app with 'python -m conduit.app'")
