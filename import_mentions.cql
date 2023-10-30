// df_mentions = get_table(Session, Mention)
// df_mentions.to_csv("neo4j-import/mentions.csv")

// echo ':source import_mentions.cql' | cypher-shell -u neo4j -p neo4j

CREATE CONSTRAINT unique_user_pubkey
IF NOT EXISTS
ON (n:User)
ASSERT n.pubkey IS UNIQUE;

CREATE CONSTRAINT unique_event_id
IF NOT EXISTS
ON (e:Event)
ASSERT e.id IS UNIQUE;

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM 'file:///mentions.csv' AS row
MERGE (pubkey:User {pubkey: row.pubkey})
MERGE (mentioned:User {pubkey: row.ref_pubkey})
MERGE (e:Event {id: row.id})
SET e.kind = row.kind, 
    e.createdAt = toInteger(row.created_at)
MERGE (pubkey)-[:CREATES]->(e)
MERGE (e)-[:TARGETS]->(mentioned)
MERGE (pubkey)-[:MENTIONS_VIA]->(e)
