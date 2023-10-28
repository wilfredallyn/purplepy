// df_kind_3 = query_db(Session=Session, kind=3)
// df_follows = parse_tags(df_kind_3, output_col="follows", filter_tag="p")
// df_follows.to_sql('follow', engine, if_exists="replace")
// df_follows.to_csv("neo4j-import/follows.csv", index=False)

// echo ':source import_follows.cql' | cypher-shell -u neo4j -p neo4j

// CREATE CONSTRAINT unique_user_pubkey ON (n:User) ASSERT n.pubkey IS UNIQUE;

USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
MERGE (follower:User {pubkey: row.pubkey})
MERGE (followed:User {pubkey: row.follows})
MERGE (follower)-[r:FOLLOWS]->(followed)
ON CREATE SET r.createdAt = row.created_at;

// TODO: check created_at to see if need to update relationship
