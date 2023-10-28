// df_mentions = get_table(Session, Mention)
// df_mentions.to_csv("neo4j-import/mentions.csv")

// echo ':source import_mentions.cql' | cypher-shell -u neo4j -p neo4j

// CREATE CONSTRAINT unique_user_pubkey ON (n:User) ASSERT n.pubkey IS UNIQUE;

USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///mentions.csv' AS row
MERGE (pubkey:User {pubkey: row.pubkey})
MERGE (mentioned:User {pubkey: row.ref_id})
MERGE (pubkey)-[r:MENTIONS]->(mentioned)
ON CREATE SET r.kind = row.kind, r.createdAt = row.created_at, r.id = row.id;




