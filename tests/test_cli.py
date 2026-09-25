from unittest.mock import patch

import pytest

from doi_downloader import cli

DOI_A = "10.1000/a"
DOI_B = "10.1000/b"


def test_read_doi_file_skips_blank_and_comment_lines(tmp_path):
    doi_file = tmp_path / "dois.txt"
    doi_file.write_text(f"{DOI_A}\n\n# a comment\n{DOI_B}\n")
    assert cli.read_doi_file(doi_file) == [DOI_A, DOI_B]


def test_main_requires_at_least_one_doi():
    with pytest.raises(SystemExit):
        cli.main([])


def test_main_downloads_each_doi_and_returns_zero_on_success():
    with patch.object(cli, "download", return_value="/tmp/a.pdf") as mock_download:
        exit_code = cli.main([DOI_A, DOI_B])
    assert exit_code == 0
    assert mock_download.call_count == 2


def test_main_returns_nonzero_when_a_download_fails():
    with patch.object(cli, "download", return_value=None):
        exit_code = cli.main([DOI_A])
    assert exit_code == 1


def test_main_returns_nonzero_when_download_raises():
    with patch.object(cli, "download", side_effect=ValueError("boom")):
        exit_code = cli.main([DOI_A])
    assert exit_code == 1


def test_main_reads_dois_from_file(tmp_path):
    doi_file = tmp_path / "dois.txt"
    doi_file.write_text(f"{DOI_A}\n{DOI_B}\n")
    with patch.object(cli, "download", return_value="/tmp/a.pdf") as mock_download:
        exit_code = cli.main(["--file", str(doi_file)])
    assert exit_code == 0
    assert mock_download.call_count == 2


def test_main_passes_flags_through_to_download():
    with patch.object(cli, "download", return_value="/tmp/a.pdf") as mock_download:
        cli.main([DOI_A, "--output-dir", "out", "--force", "--domain", "Nature", "--no-benchmark"])
    mock_download.assert_called_once_with(
        doi=DOI_A,
        output_dir="out",
        force_download=True,
        journal_domain="Nature",
        enable_benchmark=False,
    )


def test_main_defaults_match_download_defaults():
    with patch.object(cli, "download", return_value="/tmp/a.pdf") as mock_download:
        cli.main([DOI_A])
    mock_download.assert_called_once_with(
        doi=DOI_A,
        output_dir=".",
        force_download=False,
        journal_domain=None,
        enable_benchmark=True,
    )


def test_main_reports_missing_doi_file_without_traceback(tmp_path, capsys):
    missing = tmp_path / "missing.txt"
    with patch.object(cli, "download") as mock_download, pytest.raises(SystemExit) as excinfo:
        cli.main(["--file", str(missing)])
    assert excinfo.value.code == 2
    assert f"cannot read DOI file {missing}" in capsys.readouterr().err
    mock_download.assert_not_called()
