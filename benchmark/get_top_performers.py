"""
analyze_performance.py - Generate reports from benchmark data
"""
import sys
import os
from doi_downloader.benchmark import BenchmarkLogger, BenchmarkAnalyzer

def main(log_file="benchmark/logs/benchmark_log.jsonl"):
    logger = BenchmarkLogger(log_file)
    analyzer = BenchmarkAnalyzer(logger)
    
    output = ''
    output += '='*60
    output += os.linesep
    output += 'PERFORMANCE SUMMARY'
    output += os.linesep
    output += '='*60
    output += os.linesep

    # Overall stats
    overall = analyzer.overall_success_rate()
    output += f"\nTotal Attempts: {overall.get('total_attempts', 0)}"
    output += os.linesep
    output += f"URL Resolution Rate: {overall.get('url_resolution_rate', 0)}%"
    output += os.linesep
    output += f"PDF Download Rate: {overall.get('pdf_download_rate', 0)}%"
    output += os.linesep

    # Top performing plugins
    output += "\n" + "="*60
    output += os.linesep
    output += "TOP PERFORMING PLUGINS"
    output += os.linesep
    output += '='*60
    output += os.linesep
    per_plugin = analyzer.per_plugin_performance()
    sorted_plugins = sorted(
        per_plugin.items(), 
        key=lambda x: x[1]['pdf_download_rate'], 
        reverse=True
    )
    for plugin, stats in sorted_plugins[:5]:
        output += f"\n{plugin}:"
        output += os.linesep
        output += f"  Download Rate: {stats['pdf_download_rate']}%"
        output += os.linesep
        output += f"  Attempts: {stats['total_attempts']}"
        output += os.linesep
    
    # Top performing journals
    output += "\n" + "="*60
    output += os.linesep
    output += "TOP PERFORMING JOURNALS"
    output += os.linesep
    output += '='*60
    output += os.linesep

    per_journal = analyzer.per_journal_performance()
    sorted_journals = sorted(
        per_journal.items(), 
        key=lambda x: x[1]['pdf_download_rate'], 
        reverse=True
    )
    for journal, stats in sorted_journals[:5]:
        output += f"\n{journal}:"
        output += os.linesep
        output += f"  Download Rate: {stats['pdf_download_rate']}%"
        output += os.linesep
        output += f"  Attempts: {stats['total_attempts']}"
        output += os.linesep
    
    # Generate full reports
    output += "\n" + "="*60
    print("Generating detailed reports...")
    print("✓ Reports saved to 'benchmark/reports/top_performers.txt'")

    with open('benchmark/reports/top_performers.txt', 'w', encoding='utf-8') as f:
        f.write(output)

if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else "benchmark/logs/benchmark_log.jsonl"
    main(log_file)