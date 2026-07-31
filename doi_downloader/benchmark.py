"""
Performance Benchmarking System for DOI Downloader
===================================================

Architecture:
1. BenchmarkLogger: Captures metrics for a download attempt
2. BenchmarkAnalyzer: Generates reports from the logged data
3. Integration points in existing code
"""

import csv
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

# =============================================================================
# 1. DATA MODEL
# =============================================================================


@dataclass
class DownloadAttempt:
    """Records a single download attempt with relevant context"""

    doi: str  # DOI on which the download attempt was made
    timestamp: str  # When the download attempt was made
    plugin_name: str  # Which plugin was used to make the download attempt
    resolved_url: str | None = None  # DOI resolves to a URL
    journal_domain: str | None = None  # Resolved URL contains the journal name (domain of the URL)

    # Success metrics
    url_resolved: bool = False  # Was the DOI successfully resolved to a URL?
    pdf_downloaded: bool = False  # Was the PDF successfully downloaded?

    # Additional metadata
    duration_ms: float | None = None  # How long did the download attempt take?
    file_size_bytes: int | None = None  # How large was the PDF file, if downloaded?
    error_message: str | None = None  # What was the error message if download failed?
    http_status: int | None = None  # HTTP response code

    def to_dict(self):
        return asdict(self)


# =============================================================================
# 2. BENCHMARK LOGGER
# =============================================================================


class BenchmarkLogger:
    """Simplified logger for capturing download performance metrics"""

    def __init__(self, log_file: str = "benchmark_log.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_attempt(self, attempt: DownloadAttempt):
        """Append a download attempt to the log file"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            json.dump(attempt.to_dict(), f)
            f.write("\n")

    def create_attempt(self, doi: str, plugin_name: str, journal_domain: str | None = None) -> DownloadAttempt:
        """Factory method to create a new attempt"""
        return DownloadAttempt(
            doi=doi, timestamp=datetime.now(UTC).isoformat(), plugin_name=plugin_name, journal_domain=journal_domain
        )

    def read_attempts(self) -> list[DownloadAttempt]:
        """Read all attempts from log file"""
        if not self.log_file.exists():
            return []

        attempts = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    attempts.append(DownloadAttempt(**data))
        return attempts


# =============================================================================
# 3. BENCHMARK ANALYZER
# =============================================================================


class BenchmarkAnalyzer:
    """Analyzes logged benchmark data and generates reports"""

    def __init__(self, logger: BenchmarkLogger):
        self.logger = logger
        self.attempts = logger.read_attempts()

    def overall_success_rate(self) -> dict:
        """Calculate overall success rates"""
        if not self.attempts:
            return {"error": "No data available"}

        total = len(self.attempts)
        url_resolved = sum(1 for a in self.attempts if a.url_resolved)
        pdf_downloaded = sum(1 for a in self.attempts if a.pdf_downloaded)

        return {
            "total_attempts": total,
            "url_resolution_rate": round(url_resolved / total * 100, 2),
            "pdf_download_rate": round(pdf_downloaded / total * 100, 2),
        }

    def per_plugin_performance(self) -> dict:
        """Calculate success rates per plugin"""
        plugin_stats = defaultdict(lambda: {"total": 0, "url_resolved": 0, "pdf_downloaded": 0})

        for attempt in self.attempts:
            plugin = attempt.plugin_name
            plugin_stats[plugin]["total"] += 1
            if attempt.url_resolved:
                plugin_stats[plugin]["url_resolved"] += 1
            if attempt.pdf_downloaded:
                plugin_stats[plugin]["pdf_downloaded"] += 1

        # Calculate percentages
        results = {}
        for plugin, stats in plugin_stats.items():
            total = stats["total"]
            results[plugin] = {
                "total_attempts": total,
                "url_resolution_rate": round(stats["url_resolved"] / total * 100, 2),
                "pdf_download_rate": round(stats["pdf_downloaded"] / total * 100, 2),
            }

        return results

    def per_journal_performance(self) -> dict:
        """Calculate success rates per journal/domain"""
        journal_stats = defaultdict(lambda: {"total": 0, "url_resolved": 0, "pdf_downloaded": 0})

        for attempt in self.attempts:
            if not attempt.journal_domain:
                continue

            journal = attempt.journal_domain
            journal_stats[journal]["total"] += 1
            if attempt.url_resolved:
                journal_stats[journal]["url_resolved"] += 1
            if attempt.pdf_downloaded:
                journal_stats[journal]["pdf_downloaded"] += 1

        # Calculate percentages
        results = {}
        for journal, stats in journal_stats.items():
            total = stats["total"]
            results[journal] = {
                "total_attempts": total,
                "url_resolution_rate": round(stats["url_resolved"] / total * 100, 2),
                "pdf_download_rate": round(stats["pdf_downloaded"] / total * 100, 2),
            }

        return results

    def plugin_journal_matrix(self) -> dict:
        """Analyze performance for each plugin-journal combination"""
        matrix = defaultdict(lambda: defaultdict(lambda: {"total": 0, "url_resolved": 0, "pdf_downloaded": 0}))

        for attempt in self.attempts:
            if not attempt.journal_domain:
                continue

            plugin = attempt.plugin_name
            journal = attempt.journal_domain
            matrix[plugin][journal]["total"] += 1
            if attempt.url_resolved:
                matrix[plugin][journal]["url_resolved"] += 1
            if attempt.pdf_downloaded:
                matrix[plugin][journal]["pdf_downloaded"] += 1

        # Calculate percentages
        results = {}
        for plugin, journals in matrix.items():
            results[plugin] = {}
            for journal, stats in journals.items():
                total = stats["total"]
                results[plugin][journal] = {
                    "total_attempts": total,
                    "url_resolution_rate": round(stats["url_resolved"] / total * 100, 2),
                    "pdf_download_rate": round(stats["pdf_downloaded"] / total * 100, 2),
                }

        return results

    def generate_report(self, output_file: str = "benchmark_report.txt"):
        """Generate a comprehensive text report"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("DOI DOWNLOADER PERFORMANCE REPORT\n")
            f.write(f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Overall stats
            f.write("OVERALL PERFORMANCE\n")
            f.write("-" * 80 + "\n")
            overall = self.overall_success_rate()
            f.writelines(f"{key}: {value}\n" for key, value in overall.items())
            f.write("\n")

            # Per-plugin stats
            f.write("PERFORMANCE BY PLUGIN\n")
            f.write("-" * 80 + "\n")
            per_plugin = self.per_plugin_performance()
            for plugin, stats in sorted(per_plugin.items()):
                f.write(f"\n{plugin}:\n")
                f.writelines(f"  {key}: {value}\n" for key, value in stats.items())
            f.write("\n")

            # Per-journal stats
            f.write("PERFORMANCE BY JOURNAL\n")
            f.write("-" * 80 + "\n")
            per_journal = self.per_journal_performance()
            for journal, stats in sorted(per_journal.items()):
                f.write(f"\n{journal}:\n")
                f.writelines(f"  {key}: {value}\n" for key, value in stats.items())
            f.write("\n")

            # Plugin-journal matrix
            f.write("PLUGIN-JOURNAL PERFORMANCE MATRIX\n")
            f.write("-" * 80 + "\n")
            matrix = self.plugin_journal_matrix()
            for plugin, journals in sorted(matrix.items()):
                f.write(f"\n{plugin}:\n")
                for journal, stats in sorted(journals.items()):
                    f.write(f"  {journal}:\n")
                    f.writelines(f"    {key}: {value}\n" for key, value in stats.items())

        print(f"Report generated: {output_file}")

    def export_to_csv(self, output_file: str = "benchmark_data.csv"):
        """Export raw data to CSV for further analysis"""
        if not self.attempts:
            print("No data to export")
            return

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.attempts[0].to_dict().keys())
            writer.writeheader()
            for attempt in self.attempts:
                writer.writerow(attempt.to_dict())

        print(f"Data exported to: {output_file}")


# =============================================================================
# 5. USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    logger = BenchmarkLogger("benchmark_log.jsonl")
    analyzer = BenchmarkAnalyzer(logger)

    analyzer.generate_report("performance_report.txt")
    analyzer.export_to_csv("performance_data.csv")

    print("\nOVERALL PERFORMANCE:")
    print(json.dumps(analyzer.overall_success_rate(), indent=2))

    print("\nPER-PLUGIN PERFORMANCE:")
    print(json.dumps(analyzer.per_plugin_performance(), indent=2))
