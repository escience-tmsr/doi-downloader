"""
analyze_performance.py - Generate reports from benchmark data
"""
import sys
from doi_downloader.benchmark import BenchmarkLogger, BenchmarkAnalyzer

def main(log_file="benchmark/logs/benchmark_log.jsonl"):
    logger = BenchmarkLogger(log_file)
    analyzer = BenchmarkAnalyzer(logger)
    
    print("="*60)
    print("QUICK PERFORMANCE SUMMARY")
    print("="*60)
    
    # Overall stats
    overall = analyzer.overall_success_rate()
    print(f"\nTotal Attempts: {overall.get('total_attempts', 0)}")
    print(f"URL Resolution Rate: {overall.get('url_resolution_rate', 0)}%")
    print(f"PDF Download Rate: {overall.get('pdf_download_rate', 0)}%")
    
    # Top performing plugins
    print("\n" + "="*60)
    print("TOP PERFORMING PLUGINS")
    print("="*60)
    per_plugin = analyzer.per_plugin_performance()
    sorted_plugins = sorted(
        per_plugin.items(), 
        key=lambda x: x[1]['pdf_download_rate'], 
        reverse=True
    )
    for plugin, stats in sorted_plugins[:5]:
        print(f"\n{plugin}:")
        print(f"  Download Rate: {stats['pdf_download_rate']}%")
        print(f"  Attempts: {stats['total_attempts']}")
    
    # Top performing journals
    print("\n" + "="*60)
    print("TOP PERFORMING JOURNALS")
    print("="*60)
    per_journal = analyzer.per_journal_performance()
    sorted_journals = sorted(
        per_journal.items(), 
        key=lambda x: x[1]['pdf_download_rate'], 
        reverse=True
    )
    for journal, stats in sorted_journals[:5]:
        print(f"\n{journal}:")
        print(f"  Download Rate: {stats['pdf_download_rate']}%")
        print(f"  Attempts: {stats['total_attempts']}")
    
    # Generate full reports
    print("\n" + "="*60)
    print("Generating detailed reports...")
    analyzer.generate_report("benchmark/reports/performance_report.txt")
    analyzer.export_to_csv("benchmark/reports/performance_data.csv")
    print("✓ Reports saved to 'reports/' directory")

if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else "benchmark/logs/benchmark_log.jsonl"
    main(log_file)