from doi_downloader import loader as ld
from doi_downloader import pdf_download as pdf_dl
from doi_downloader.benchmark import BenchmarkLogger
import os
import time

plugins = ld.plugins

# Initialize benchmark logger
benchmark_logger = BenchmarkLogger("benchmark/logs/benchmark_log.jsonl")


def sanitize_doi(doi):
    """Replace slashes and periods in doi by underscores"""
    return doi.replace("/", "_").replace(".", "_")


def download(doi, output_dir=".", force_download=False, 
             journal_domain=None, enable_benchmark=True):
    """
    Download PDF with optional benchmarking
    
    Args:
        doi: DOI identifier
        output_dir: Output directory for PDF
        force_download: Skip cache check
        journal_domain: Journal/domain name for analytics
        enable_benchmark: Enable performance tracking
    """
    if not doi:
        raise ValueError("DOI cannot be empty.")
    
    os.makedirs(output_dir, exist_ok=True)
    
    safe_filename = sanitize_doi(doi) + ".pdf"
    if not force_download and os.path.exists(os.path.join(output_dir, f"{safe_filename}")):
        print(f"File already exists: {os.path.join(output_dir, f'{safe_filename}')}")
        return os.path.join(output_dir, f"{safe_filename}")

    downloaded_file = None

    for name, plugin in sorted(plugins.items(), key=lambda item: item[0]):
        # Create attempt record if benchmarking is enabled
        attempt = None
        start_time = None
        
        if enable_benchmark:
            attempt = benchmark_logger.create_attempt(doi, name, journal_domain)
            start_time = time.time()
        
        try:
            # Call plugin with original signature (no ctx parameter)
            urls = plugin.get_pdf_urls(doi)
            
            if urls:
                # Mark URL resolution success
                if attempt:
                    attempt.url_resolved = True
                    attempt.resolved_url = urls[0]
                
                print(f"Plugin: {name},  doi:{doi},  url: {urls[0]}")
                downloaded_file, verified = pdf_dl.download_pdf(urls[0], safe_filename, output_dir)
                
                if downloaded_file:
                    # Mark download success
                    if attempt:
                        attempt.pdf_downloaded = True
                        from pathlib import Path
                        if Path(downloaded_file).exists():
                            attempt.file_size_bytes = Path(downloaded_file).stat().st_size
                    break
        
        except Exception as e:
            # Log error if benchmarking
            if attempt:
                attempt.error_message = str(e)
        
        finally:
            # Log the attempt with duration
            if attempt:
                attempt.duration_ms = round((time.time() - start_time) * 1000, 2)
                benchmark_logger.log_attempt(attempt)

    return downloaded_file, verified
