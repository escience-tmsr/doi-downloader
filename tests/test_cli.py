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
        show_progress=False,
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
        show_progress=False,
    )


def test_main_reports_missing_doi_file_without_traceback(tmp_path, capsys):
    missing = tmp_path / "missing.txt"
    with patch.object(cli, "download") as mock_download, pytest.raises(SystemExit) as excinfo:
        cli.main(["--file", str(missing)])
    assert excinfo.value.code == 2
    assert f"cannot read DOI file {missing}" in capsys.readouterr().err
    mock_download.assert_not_called()


class FakeProgressWindow:
    """Stands in for progress_browser's BrowserView; fails to start if given an error."""

    def __init__(self, startup_error=None):
        self.startup_error = startup_error
        self.contents = []

    def update(self, html_content):
        if self.startup_error is not None:
            raise self.startup_error
        self.contents.append(html_content)


@pytest.fixture
def progress_window(monkeypatch):
    from doi_downloader import progress_browser

    window = FakeProgressWindow()
    monkeypatch.setattr(progress_browser, "get_browser_view", lambda: window)
    return window


def run_in_terminal(monkeypatch, is_terminal):
    """Let the command run as if in a terminal or not; returns the prompts it waited on."""
    prompts = []
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: is_terminal)
    monkeypatch.setattr("builtins.input", lambda prompt="": prompts.append(prompt))
    return prompts


def test_show_progress_opens_the_window_first_and_passes_the_option_to_download(monkeypatch, progress_window):
    run_in_terminal(monkeypatch, False)
    with patch.object(cli, "download", return_value="/tmp/a.pdf") as mock_download:
        exit_code = cli.main([DOI_A, "--show-progress"])
    assert exit_code == 0
    assert progress_window.contents == [cli.PROGRESS_WINDOW_START_HTML]
    assert mock_download.call_args.kwargs["show_progress"] is True


def test_show_progress_waits_for_enter_in_a_terminal(monkeypatch, progress_window):
    prompts = run_in_terminal(monkeypatch, True)
    with patch.object(cli, "download", return_value="/tmp/a.pdf"):
        cli.main([DOI_A, "--show-progress"])
    assert prompts == ["Press Enter to close the progress window..."]


def test_show_progress_does_not_wait_outside_a_terminal(monkeypatch, progress_window):
    prompts = run_in_terminal(monkeypatch, False)
    with patch.object(cli, "download", return_value="/tmp/a.pdf"):
        cli.main([DOI_A, "--show-progress"])
    assert prompts == []


def test_show_progress_ends_quietly_when_the_wait_is_interrupted(monkeypatch, progress_window):
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)

    def interrupted_input(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupted_input)
    with patch.object(cli, "download", return_value="/tmp/a.pdf"):
        assert cli.main([DOI_A, "--show-progress"]) == 0


def test_without_show_progress_no_window_opens_and_nothing_waits(monkeypatch, progress_window):
    prompts = run_in_terminal(monkeypatch, True)
    with patch.object(cli, "download", return_value="/tmp/a.pdf") as mock_download:
        cli.main([DOI_A])
    assert progress_window.contents == []
    assert prompts == []
    assert mock_download.call_args.kwargs["show_progress"] is False


def test_a_window_that_cannot_open_is_reported_with_the_playwright_hint(monkeypatch, capsys):
    from doi_downloader import progress_browser

    missing_browser = RuntimeError("Executable doesn't exist at /home/user/.cache/ms-playwright/chromium")
    monkeypatch.setattr(progress_browser, "get_browser_view", lambda: FakeProgressWindow(missing_browser))
    with patch.object(cli, "download") as mock_download:
        exit_code = cli.main([DOI_A, DOI_B, "--show-progress"])
    assert exit_code == 2
    mock_download.assert_not_called()
    error_output = capsys.readouterr().err
    assert "Could not open the progress window: Executable doesn't exist" in error_output
    assert "playwright install chromium" in error_output
