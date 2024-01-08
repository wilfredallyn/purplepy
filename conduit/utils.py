from dash import dash_table
from datetime import datetime
from nostr_sdk import EventId, PublicKey

# https://github.com/nostr-protocol/nips#event-kinds
kind_name_dict = {
    0: "Metadata",
    1: "Short Text Note",
    2: "Recommend Relay",
    3: "Contacts",
    4: "Encrypted Direct Messages",
    5: "Event Deletion",
    6: "Repost",
    7: "Reaction",
    8: "Badge Award",
    16: "Generic Repost",
    40: "Channel Creation",
    41: "Channel Metadata",
    42: "Channel Message",
    43: "Channel Hide Message",
    44: "Channel Mute User",
    1063: "File Metadata",
    1311: "Live Chat Message",
    1984: "Reporting",
    1985: "Label",
    4550: "Community Post Approval",
    9041: "Zap Goal",
    9734: "Zap Request",
    9735: "Zap",
    10000: "Mute List",
    10001: "Pin List",
    10002: "Relay List Metadata",
    13194: "Wallet Info",
    22242: "Client Authentication",
    23194: "Wallet Request",
    23195: "Wallet Response",
    24133: "Nostr Connect",
    27235: "HTTP Auth",
    30000: "Categorized People List",
    30001: "Categorized Bookmark List",
    30008: "Profile Badges",
    30009: "Badge Definition",
    30017: "Create or update a stall",
    30018: "Create or update a product",
    30023: "Long-form Content",
    30024: "Draft Long-form Content",
    30078: "Application-specific Data",
    30311: "Live Event",
    30315: "User Statuses",
    30402: "Classified Listing",
    30403: "Draft Classified Listing",
    31922: "Date-Based Calendar Event",
    31923: "Time-Based Calendar Event",
    31924: "Calendar",
    31925: "Calendar Event RSVP",
    31989: "Handler recommendation",
    31990: "Handler information",
    34550: "Community Definition",
    65000: "Job feedback",  # https://github.com/nostr-protocol/nips/blob/vending-machine/90.md#kinds
    65001: "Job result",
    # 65002-66000	Job request kinds
}


def get_npub(pubkey):
    return PublicKey.from_hex(pubkey).to_bech32()


def get_pubkey_hex(npub):
    return PublicKey.from_bech32(npub).to_hex()


def get_event_bech(event_hex):
    return EventId.from_hex(event_hex).to_bech32()


def get_events_by_time(df):
    if "created_at" in df.columns:
        df["created_at"] = df["created_at"].apply(parse_datetime)
    df["day_of_week"] = df["created_at"].dt.day_name()
    df["hour_of_day"] = df["created_at"].dt.hour
    return df


def parse_datetime(ts):
    if isinstance(ts, int):  # Unix timestamp
        return datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        if len(ts) == 18:  # Format: "YYYY-MM-DD HH:MMAM" or "YYYY-MM-DD HH:MMPM"
            return datetime.strptime(ts, "%Y-%m-%d %I:%M%p")
        elif ts.endswith("Z"):  # ISO 8601 Format: "YYYY-MM-DDTHH:MM:SSZ"
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        else:
            raise ValueError("Unexpected format for 'created_at' column")
    else:
        raise ValueError("Input must be a string or integer")


def parse_datetime_str(ts):
    if isinstance(ts, int):  # Unix timestamp
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %I:%M%p")
    elif isinstance(ts, str):
        if len(ts) == 18:  # Format: "YYYY-MM-DD HH:MMAM" or "YYYY-MM-DD HH:MMPM"
            return ts
        elif ts.endswith("Z"):  # ISO 8601 Format: "YYYY-MM-DDTHH:MM:SSZ"
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            return dt.strftime("%Y-%m-%d %I:%M%p")
        else:
            raise ValueError("Unexpected format for 'created_at' column")
    else:
        raise ValueError("Input must be a string or integer")


def format_data_table(df):
    if "pubkey" in df.columns:
        df = format_pubkey_html_link(df)

    cols_list = []
    for col in df.columns:
        if col == "pubkey":
            cols_list.append(
                {"name": col, "id": col, "type": "text", "presentation": "markdown"}
            )
        else:
            cols_list.append({"name": col, "id": col})

    data_table = dash_table.DataTable(
        data=df.to_dict("records"),
        columns=cols_list,
        style_data_conditional=[
            {
                "if": {"column_id": "content"},
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "maxWidth": 200,
                "minWidth": 50,
            }
        ],
        tooltip_data=[
            {
                column: {"value": str(value), "type": "markdown"}
                for column, value in row.items()
            }
            for row in df.to_dict("records")
        ],
        markdown_options={"html": True},
    )
    return data_table


def format_pubkey_html_link(df):
    df["pubkey"] = df["pubkey"].apply(
        lambda x: f'<a href="http://njump.me/{x}">{x}</a>'
    )
    return df
