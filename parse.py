def parse_tags(df, output_col, filter_tag=None):
    # filter_tag = "p", "e", etc.
    cols = ["pubkey", "created_at", "tags"]
    df = df.reset_index(drop=True)[cols].explode("tags")
    if filter_tag:
        df = df[df["tags"].str[0] == filter_tag]
    df[output_col] = df["tags"].str[1]
    df = df.drop(columns="tags").reset_index(drop=True)
    return df
