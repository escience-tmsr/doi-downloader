"""Command-line entry point for downloading PDFs by DOI.

Wraps doi_downloader.download() directly; unlike benchmark/batch_download.py
this is meant for everyday single- or few-DOI use, not benchmarking runs, so
it takes plain DOIs or a DOI-list file rather than a domain-annotated CSV,
and defaults match download()'s own defaults.
"""

import argparse
import sys

from doi_downloader.doi_downloader import download

# Shown while the progress window waits for the first progress table.
PROGRESS_WINDOW_START_HTML = "<p>doi-downloader is starting...</p>"
PLAYWRIGHT_BROWSER_HINT = (
    "The progress window needs Playwright's Chromium browser. If it is not installed, install it with:\n"
    "    playwright install chromium"
)


def read_doi_file(path):
    """
    Read DOIs from a text file, one per line.

    Args:
        path: Path to the file. Blank lines and lines starting with # are skipped.

    Returns:
        List of DOI strings, in file order.
    """
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def open_progress_window():
    """
    Open the browser window with the live progress table before the first download, so
    that a browser that cannot start is reported once, with a hint, instead of failing
    every DOI.

    Returns:
        True if the window opened, False if it could not (the reason is printed).
    """
    from doi_downloader import progress_browser

    try:
        progress_browser.get_browser_view().update(PROGRESS_WINDOW_START_HTML)
    except Exception as e:
        print(f"Could not open the progress window: {e}", file=sys.stderr)
        print(PLAYWRIGHT_BROWSER_HINT, file=sys.stderr)
        return False
    return True


def wait_before_closing_progress_window():
    """
    Keep the progress window open until the user presses Enter, as it closes when the
    command ends. Only in a terminal: a script or pipeline would wait forever.
    """
    if not sys.stdin.isatty():
        return
    try:
        input("Press Enter to close the progress window...")
    except (EOFError, KeyboardInterrupt):
        pass


def build_parser():
    """
    Build the argument parser for the doi-downloader command-line tool.

    Returns:
        A configured argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="doi-downloader",
        description="Download PDF files for scientific articles by DOI.",
    )
    parser.add_argument("dois", nargs="*", help="One or more DOIs to download.")
    parser.add_argument(
        "-f",
        "--file",
        help="Path to a text file with one DOI per line (lines starting with # are ignored).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory to save downloaded PDFs in (default: current directory).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if a matching file already exists.",
    )
    parser.add_argument(
        "--domain",
        help="Journal/domain name to record for analytics, applied to every DOI given.",
    )
    parser.add_argument(
        "--no-benchmark",
        action="store_true",
        help="Disable performance tracking for this run.",
    )
    parser.add_argument(
        "--show-progress",
        action="store_true",
        help="Show a live progress table in a browser window (needs Playwright's Chromium browser).",
    )
    return parser


def main(argv=None):
    """
    Parse arguments and download every requested DOI.

    Args:
        argv: Argument list to parse (defaults to sys.argv[1:] via argparse).

    Returns:
        0 if every DOI downloaded successfully, 1 if any DOI failed, 2 if the progress
        window could not be opened.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    dois = list(args.dois)
    if args.file:
        try:
            dois += read_doi_file(args.file)
        except OSError as e:
            parser.error(f"cannot read DOI file {args.file}: {e.strerror}")
    if not dois:
        parser.error("no DOIs given: pass one or more DOIs, or --file <path>")
    if args.show_progress and not open_progress_window():
        return 2

    failures = 0
    for doi in dois:
        try:
            result = download(
                doi=doi,
                output_dir=args.output_dir,
                force_download=args.force,
                journal_domain=args.domain,
                enable_benchmark=not args.no_benchmark,
                show_progress=args.show_progress,
            )
        except Exception as e:
            print(f"FAIL {doi}: {e}")
            failures += 1
            continue

        if result:
            print(f"OK {doi}: {result}")
        else:
            print(f"FAIL {doi}: no PDF found")
            failures += 1

    if args.show_progress:
        wait_before_closing_progress_window()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
