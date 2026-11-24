from bai_datalab.data_analysis import analyse_delimited_dataset


def test_dataset_profile():
    content = (
        b"y,x1,x2,constant\n"
        b"0,1,1,5\n"
        b"0,2,2,5\n"
        b"0,3,3,5\n"
        b"1,4,4,5\n"
    )

    result = analyse_delimited_dataset(
        "data.csv",
        content,
    )

    assert result["rows"] == 4
    assert result["columns"] == 4
    assert result["variables"]["constant"]["constant"] is True
    assert result["variables"]["y"]["binary"] is True
    assert result["high_correlations"]
