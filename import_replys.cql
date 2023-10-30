// df_replys = get_table(Session, Reply)
// df_replys.to_csv("neo4j-import/replys.csv")

// echo ':source import_replys.cql' | cypher-shell -u neo4j -p neo4j

CREATE CONSTRAINT unique_user_pubkey
IF NOT EXISTS
ON (n:User)
ASSERT n.pubkey IS UNIQUE;

CREATE CONSTRAINT unique_event_id
IF NOT EXISTS
ON (e:Event)
ASSERT e.id IS UNIQUE;

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM 'file:///replys.csv' AS row
MERGE (pubkey:User {pubkey: row.pubkey})
MERGE (e:Event {id: row.id})
MERGE (repliedEvent:Event {id: row.ref_id})
SET e.kind = row.kind, 
    e.createdAt = toInteger(row.created_at),
    e.relay_url = row.relay_url,
    e.marker = row.marker
MERGE (pubkey)-[:CREATES]->(e)
MERGE (pubkey)-[:REPLIES_VIA]->(e)
MERGE (e)-[:REPLIES_TO]->(repliedEvent)

// TODO: add ref_pubkey to csv
//MERGE (repliedUser:User {pubkey: row.ref_pubkey})
//MERGE (e)-[:TARGETS]->(repliedUser)
//MERGE (pubkey)-[r:REPLIES]->(replied)
