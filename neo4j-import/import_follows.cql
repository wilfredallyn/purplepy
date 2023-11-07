// echo ':source neo4j-import/import_follows.cql' | cypher-shell -u neo4j -p neo4j

CREATE CONSTRAINT unique_user_pubkey
IF NOT EXISTS
ON (n:User)
ASSERT n.pubkey IS UNIQUE;

CREATE CONSTRAINT unique_event_id
IF NOT EXISTS
ON (e:Event)
ASSERT e.id IS UNIQUE;

USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
MERGE (follower:User {pubkey: row.pubkey})
MERGE (followed:User {pubkey: row.p})
MERGE (e:Event {id: row.id})
SET e.createdAt = toInteger(row.created_at)
MERGE (follower)-[:CREATES]->(e)
MERGE (e)-[:TARGETS]->(followed)
MERGE (follower)-[r:FOLLOWS]->(followed)

// add MERGE (follower)-[r:FOLLOWS_VIA]->(e) ?
// TODO: check created_at to see if need to update relationship
