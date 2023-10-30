import pytest
import pandas as pd
from parse import parse_follows, parse_reactions


@pytest.fixture
def reaction_with_single_tags():
    event = {
        "id": ["id123"],
        "pubkey": ["pubkey123"],
        "kind": 7,
        "content": "+",
        "created_at": [1695510784],
        "tags": [[["e", "e_id"], ["p", "p_id"]]],
    }
    return pd.DataFrame(event)


@pytest.fixture
def reaction_with_multiple_tags():
    # https://github.com/nostr-protocol/nips/blob/master/25.md#tags
    event = {
        "id": ["id123"],
        "pubkey": ["pubkey123"],
        "kind": 7,
        "content": "+",
        "created_at": [1695510784],
        "tags": [[["e", "e_id1"], ["p", "p_id1"], ["e", "e_id2"], ["p", "p_id2"]]],
    }
    return pd.DataFrame(event)


@pytest.fixture
def follow_event():
    # https://github.com/nostr-protocol/nips/blob/master/02.md
    event = {
        "id": ["id123"],
        "pubkey": ["pubkey123"],
        "kind": 3,
        "created_at": [1695510784],
        "tags": [[["p", "p_id1"], ["p", "p_id2"]]],
    }
    return pd.DataFrame(event)


def test_parse_follow(follow_event):
    df = parse_follows(follow_event)
    expected = pd.DataFrame(
        {
            "id": follow_event.loc[0, "id"],
            "pubkey": follow_event.loc[0, "pubkey"],
            "created_at": follow_event.loc[0, "created_at"],
            "p": [item[1] for item in follow_event.loc[0, "tags"] if item[0] == "p"],
        }
    )
    pd.testing.assert_frame_equal(df, expected)


def test_parse_reaction_with_single_tags(reaction_with_single_tags):
    df = parse_reactions(reaction_with_single_tags)
    tags = reaction_with_single_tags.loc[0, "tags"]
    expected = pd.DataFrame(
        {
            "id": reaction_with_single_tags.loc[0, "id"],
            "pubkey": reaction_with_single_tags.loc[0, "pubkey"],
            "content": reaction_with_single_tags.loc[0, "content"],
            "created_at": reaction_with_single_tags.loc[0, "created_at"],
            "e": [item[1] for item in tags if item[0] == "e"],
            "p": [item[1] for item in tags if item[0] == "p"],
        }
    )
    pd.testing.assert_frame_equal(df, expected, check_like=True)


def test_parse_reaction_with_multiple_tags(reaction_with_multiple_tags):
    df = parse_reactions(reaction_with_multiple_tags)
    tags = reaction_with_multiple_tags.loc[0, "tags"]
    expected = pd.DataFrame(
        {
            "id": reaction_with_multiple_tags.loc[0, "id"],
            "pubkey": reaction_with_multiple_tags.loc[0, "pubkey"],
            "content": reaction_with_multiple_tags.loc[0, "content"],
            "created_at": reaction_with_multiple_tags.loc[0, "created_at"],
            "e": [
                next((tag[1] for tag in reversed(tags) if tag[0] == "e"), None)
            ],  # get last tag
            "p": [next((tag[1] for tag in reversed(tags) if tag[0] == "p"), None)],
        }
    )
    pd.testing.assert_frame_equal(df, expected, check_like=True)
