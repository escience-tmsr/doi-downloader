"""
batch_download.py - Process CSV with benchmarking
"""
import csv
import sys
from doi_downloader.doi_downloader import download
from doi_downloader.benchmark import BenchmarkLogger, BenchmarkAnalyzer

MAX_DOI = 20

def process_csv(input_csv, output_dir="downloads"):
    """
    Process CSV file with DOI, URL, and domain columns
    
    CSV format:
    DOI,resolved_url,domain
    10.1000/example,https://example.com/pdf,Nature
    """
    
    total = 0
    successful = 0
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            doi = row.get('doi', '').strip()
            domain = row.get('domain', '').strip()
            
            if total >= MAX_DOI:
                print(f"Pre-set maximum ({MAX_DOI}) reached. Stopping...")
                break
            if not doi:
                continue
            
            total += 1
            print(f"\n[{total}] Processing: {doi} (Domain: {domain})")
            
            try:
                result = download(
                    doi=doi,
                    output_dir=output_dir,
                    journal_domain=domain,
                    enable_benchmark=True
                )
                
                if result:
                    successful += 1
                    print(f"✓ Downloaded: {result}")
                else:
                    print(f"✗ Failed to download: {doi}")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Total processed: {total}")
    print(f"Successful downloads: {successful}")
    print(f"Success rate: {successful/total*100:.1f}%")
    print(f"{'='*60}")
    
    # Generate report
    print("\nGenerating benchmark report...")
    logger = BenchmarkLogger("benchmark/logs/benchmark_log.jsonl")
    analyzer = BenchmarkAnalyzer(logger)
    analyzer.generate_report("benchmark/reports/performance_report.txt")
    analyzer.export_to_csv("benchmark/reports/performance_data.csv")
    print("✓ Reports generated in 'reports/' directory")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_download.py <input.csv>")
        sys.exit(1)
    
    process_csv(sys.argv[1])
