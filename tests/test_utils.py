import pytest
import pandas as pd
from utils import postprocess


@pytest.fixture
def example_df():
    df = pd.DataFrame(
        {
            "kind": ["1", "2", "1", "2", "1"],
            "tags": [["a", "b"], ["a"], ["a", "b"], ["c"], ["a", "b"]],
            "other_data": [1, 2, 1, 4, 1],
            "_sa_instance_state": [None] * 5,
        }
    )
    return df


def test_postprocess_dedupe(example_df):
    expected_cols = [
        "kind",
        "tags",
        "other_data",
    ]
    df = postprocess(example_df.copy())[expected_cols]

    expected_df = pd.DataFrame(
        {
            "kind": ["2", "1", "2"],
            "tags": [["a"], ["a", "b"], ["c"]],
            "other_data": [2, 1, 4],
        }
    )

    # can't sort tags list (unhashable)
    df["tags_str"] = df["tags"].apply(str)
    expected_df["tags_str"] = expected_df["tags"].apply(str)
    sort_cols = [col for col in df.columns if col != "tags"]

    df = df.sort_values(by=sort_cols).reset_index(drop=True)
    expected_df = expected_df.sort_values(by=sort_cols).reset_index(drop=True)

    pd.testing.assert_frame_equal(df, expected_df)


def test_postprocess_created_at():
    # assert timestamp str (not int)
    # assert sorted
    pass
