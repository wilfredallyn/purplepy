// echo ':source neo4j-import/import_reactions.cypher' | cypher-shell -u neo4j -p neo4j

CREATE CONSTRAINT unique_user_pubkey
IF NOT EXISTS
ON (n:User)
ASSERT n.pubkey IS UNIQUE;

CREATE CONSTRAINT unique_event_id
IF NOT EXISTS
ON (e:Event)
ASSERT e.id IS UNIQUE;

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM 'file:///reactions.csv' AS row 
MERGE (pubkey:User {pubkey: row.pubkey})
MERGE (e:Event {id: row.e})
ON CREATE SET e.created_at = toInteger(row.created_at)
MERGE (pubkey)-[:CREATES]->(e)

WITH row, pubkey, e WHERE NOT (row.p IS NULL OR row.p = "")
MERGE (pUser:User {pubkey: row.p})
MERGE (e)-[:TARGETS]->(pUser)
MERGE (pubkey)-[:REACTS_VIA]->(e)
SET e.content = row.content
