import dash
from dash import html

dash.register_page(__name__, path_template="/neo4j", name="Neo4j")


def layout():
    return html.Div(
        [
            html.H2("Neo4j"),
            html.A(
                "Open Neo4j Browser",
                href="http://localhost:7474",
                target="_blank",
                className="btn btn-primary",
            ),
            html.Pre(
                """
Example cypher query:

// Identify most targeted user
MATCH (targetedUser:User)<-[:TARGETS]-()
RETURN targetedUser.pubkey AS pubkey, COUNT(*) AS times_targeted
ORDER BY times_targeted DESC
LIMIT 5

// Identify most followed user
MATCH (u:User)-[r:FOLLOWS]->(other:User)
WITH u, COUNT(r) AS followsCount
ORDER BY followsCount DESC
LIMIT 5
RETURN u, followsCount

// Return the network graph for that user
MATCH (u)-[rel:FOLLOWS]->(followed:User)
RETURN u, rel, followed
                """,
                style={
                    "border": "1px solid #ddd",
                    "padding": "10px",
                    "background": "#f7f7f7",
                },
            ),
        ]
    )
