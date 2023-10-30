// echo ':source import_users.cql' | cypher-shell -u neo4j -p neo4j

CREATE CONSTRAINT unique_user_pubkey
IF NOT EXISTS
ON (n:User)
ASSERT n.pubkey IS UNIQUE;

CREATE CONSTRAINT unique_event_id
IF NOT EXISTS
ON (e:Event)
ASSERT e.id IS UNIQUE;

USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row 
MERGE (user:User {pubkey: row.pubkey})
SET user.name = row.name,
    user.about = row.about,
    user.website = row.website,
    user.nip05 = row.nip05,
    user.lud16 = row.lud16,
    user.picture = row.picture,
    user.banner = row.banner,
    user.created_at = toInteger(row.created_at);
