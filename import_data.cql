// df_kind_3 = query_db(Session=Session, kind=3)
// df_follows = parse_follows(df_kind_3)
// df_follows.to_sql('follow', engine, if_exists="replace")
// df_follows.to_csv("neo4j-import/follows.csv", index=False)

// echo ':source import_data.cql' | cypher-shell -u neo4j -p neo4j

// Create nodes for each pubkey
LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
MERGE (u:User {id: row.pubkey})
ON CREATE SET u.createdAt = row.created_at;

// Create nodes for each followed pubkey
LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
MERGE (f:User {id: row.follows});

// Create FOLLOWS relationship between pubkeys and followed profiles
LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
MATCH (follower:User {id: row.pubkey}), (followed:User {id: row.follows})
MERGE (follower)-[:FOLLOWS]->(followed);
