// df_replys = get_table(Session, Reply)
// df_replys.to_csv("neo4j-import/replys.csv")

// echo ':source import_replys.cql' | cypher-shell -u neo4j -p neo4j

// CREATE CONSTRAINT unique_user_pubkey ON (n:User) ASSERT n.pubkey IS UNIQUE;

USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///replys.csv' AS row
MERGE (pubkey:User {pubkey: row.pubkey})
MERGE (replied:User {pubkey: row.ref_id})
MERGE (pubkey)-[r:REPLIES]->(replied)
ON CREATE SET r.kind = row.kind, r.createdAt = row.created_at, r.id = row.id;
