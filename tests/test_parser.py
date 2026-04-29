from recovery_app.parsers.photorec_parser import parse_progress, parse_recovered_files


def test_parse_progress():
    assert parse_progress("Pass 2 - 67%") == 67.0
    assert parse_progress("noop") is None


def test_parse_recovered_files():
    output = "Recovered: /recup/f1.jpg (100 bytes)\nRecovered: /recup/f2.pdf (200 bytes)"
    result = parse_recovered_files(output)
    assert result.summary["file_count"] == 2
    assert result.summary["by_extension"]["jpg"] == 1
