import dash
from dash import html
from db import neo4j_driver
from nostr_sdk import PublicKey
import pandas as pd


dash.register_page(__name__, path_template="/network", name="Network")


def get_top_followed_pubkeys(tx, num_users=5):
    query = """
        MATCH (follower:User)-[:FOLLOWS]->(followed:User)
        RETURN followed.pubkey AS pubkey, COUNT(follower) AS followers_count
        ORDER BY followers_count DESC
        LIMIT $num_users
    """
    return tx.run(query, num_users=num_users).data()


def get_most_targeted_user(tx, num_users=5):
    query = f"""
        MATCH (targetedUser:User)<-[:TARGETS]-()
        RETURN targetedUser.pubkey AS pubkey, COUNT(*) AS times_targeted
        ORDER BY times_targeted DESC
        LIMIT {num_users}
    """
    return tx.run(query).data()


def get_most_active_users(tx, num_users=5):
    query = f"""
        MATCH (user:User)-[:CREATES]->(event:Event)
        RETURN user.pubkey AS pubkey, count(event) AS events_created
        ORDER BY events_created DESC
        LIMIT {num_users}
    """
    return tx.run(query).data()


def format_html_results(df):
    df["pubkey"] = df["pubkey"].apply(lambda x: PublicKey.from_hex(x).to_bech32())
    table_data = [html.Tr([html.Th(col) for col in df.columns])] + [
        html.Tr(
            [
                html.Td(
                    html.A(
                        df.iloc[i]["pubkey"],
                        href=f"http://njump.me/{df.iloc[i]['pubkey']}",
                    )
                )
                if col == "pubkey"
                else html.Td(df.iloc[i][col])
                for col in df.columns
            ]
        )
        for i in range(len(df))
    ]
    return table_data


def layout(num_users=5):
    with neo4j_driver.session() as session:
        result_followed = session.read_transaction(get_top_followed_pubkeys, num_users)
        result_targeted = session.read_transaction(get_most_targeted_user, num_users)
        result_active = session.read_transaction(get_most_active_users, num_users)

    df_followed = pd.DataFrame(result_followed)
    df_targeted = pd.DataFrame(result_targeted)
    df_active = pd.DataFrame(result_active)

    if len(df_followed) == 0 and len(df_targeted) == 0 and len(df_active) == 0:
        layout = html.Div(
            [
                html.P(f"Import data into Neo4j to analyze network"),
            ]
        )
        return layout

    layout = html.Div(
        [
            html.H3(f"Top {num_users} Most Followed Pubkeys"),
            html.Table(format_html_results(df_followed)),
            html.Hr(),
            html.H3(f"Top {num_users} Most Targeted Users"),
            html.Table(format_html_results(df_targeted)),
            html.Hr(),
            html.H3(f"Top {num_users} Most Active Users"),
            html.Table(format_html_results(df_active)),
        ]
    )
    return layout
