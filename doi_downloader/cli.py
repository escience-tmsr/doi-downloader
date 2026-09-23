"""Command-line entry point for downloading PDFs by DOI.

Wraps doi_downloader.download() directly; unlike benchmark/batch_download.py
this is meant for everyday single- or few-DOI use, not benchmarking runs, so
it takes plain DOIs or a DOI-list file rather than a domain-annotated CSV,
and defaults match download()'s own defaults.
"""

import argparse
import sys

from doi_downloader.doi_downloader import download


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
        "-f", "--file",
        help="Path to a text file with one DOI per line (lines starting with # are ignored).",
    )
    parser.add_argument(
        "-o", "--output-dir", default=".",
        help="Directory to save downloaded PDFs in (default: current directory).",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-download even if a matching file already exists.",
    )
    parser.add_argument(
        "--domain",
        help="Journal/domain name to record for analytics, applied to every DOI given.",
    )
    parser.add_argument(
        "--no-benchmark", action="store_true",
        help="Disable performance tracking for this run.",
    )
    return parser


def main(argv=None):
    """
    Parse arguments and download every requested DOI.

    Args:
        argv: Argument list to parse (defaults to sys.argv[1:] via argparse).

    Returns:
        0 if every DOI downloaded successfully, 1 if any DOI failed.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    dois = list(args.dois)
    if args.file:
        dois += read_doi_file(args.file)
    if not dois:
        parser.error("no DOIs given: pass one or more DOIs, or --file <path>")

    failures = 0
    for doi in dois:
        try:
            result = download(
                doi=doi,
                output_dir=args.output_dir,
                force_download=args.force,
                journal_domain=args.domain,
                enable_benchmark=not args.no_benchmark,
            )
        except Exception as e:
            print(f"✗ {doi}: {e}")
            failures += 1
            continue

        if result:
            print(f"✓ {doi}: {result}")
        else:
            print(f"✗ {doi}: no PDF found")
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
