def parse_follows(df):
    follows_cols = ["pubkey", "created_at", "tags"]
    df = df.reset_index(drop=True)[follows_cols].explode("tags")
    df = df[df["tags"].str[0] == "p"]
    df["follows"] = df["tags"].str[1]
    df = df.drop(columns="tags").reset_index(drop=True)
    return df
