from datetime import datetime
from nostr_sdk import EventId


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


def postprocess(df):
    if "kind" in df.columns:
        df["kind_name"] = df["kind"].map(kind_name_dict)
    if "created_at" in df.columns:
        df["created_at"] = df["created_at"].apply(
            lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %I:%M%p")
        )
        df = df.sort_values(["created_at"], ascending=True)
    if "_sa_instance_state" in df.columns:
        df = df.drop("_sa_instance_state", axis=1)
    return df


def format_data_table(df):
    df = df.applymap(
        lambda x: str(x) if not isinstance(x, (str, int, float, bool)) else x
    )
    if df.index.name == "id":
        df["id_hex"] = df.index
        df["id"] = df["id_hex"].apply(lambda x: EventId.from_hex(x).to_bech32())
        df["id_short"] = df["id"].apply(lambda x: x[:15] + "..." if len(x) > 15 else x)

    output_id_col = "id"  # "id_short" if want to shorten text
    cols = [
        output_id_col,
        "created_at",
        "pubkey",
        "kind",
        "kind_name",
        "content",
        "reply_count",
    ]

    df["pubkey"] = df["pubkey"].apply(add_link)
    table_data = df[cols].to_dict("records")

    tooltip_data = [
        {output_id_col: {"value": i["id"], "type": "markdown"}}
        for i in df[["id"]].to_dict("records")
    ]

    table_columns = [
        {"name": i, "id": i, "type": "text", "presentation": "markdown"}
        if i == "pubkey"
        else {"name": i, "id": i}
        for i in cols
    ]
    return table_data, table_columns, tooltip_data


def shorten_text(text: str, max_len: int):
    pass


def add_link(text):
    display_text = text[:15] + "..." if len(text) > 15 else text
    url = f"/user/{text}"
    return f"[{display_text}]({url})"
