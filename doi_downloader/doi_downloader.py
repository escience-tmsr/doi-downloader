from doi_downloader import loader as ld
from doi_downloader import pdf_download as pdf_dl
from doi_downloader.benchmark import BenchmarkLogger
import os
import time

plugins = ld.plugins

# Initialize benchmark logger
benchmark_logger = BenchmarkLogger("benchmark/logs/benchmark_log.jsonl")

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
    
    if not force_download and os.path.exists(os.path.join(output_dir, f"{doi}.pdf")):
        print(f"File already exists: {os.path.join(output_dir, f'{doi}.pdf')}")
        return os.path.join(output_dir, f"{doi}.pdf")

    downloaded_file = None

    for name, plugin in plugins.items():
        # Create attempt record if benchmarking is enabled
        attempt = None
        start_time = None
        
        if enable_benchmark:
            attempt = benchmark_logger.create_attempt(doi, name, journal_domain)
            start_time = time.time()
        
        try:
            # Call plugin with original signature (no ctx parameter)
            url = plugin.get_pdf_url(doi)
            
            if url:
                # Mark URL resolution success
                if attempt:
                    attempt.url_resolved = True
                    attempt.resolved_url = url
                
                # Sanitize DOI for filename
                safe_filename = doi.replace("/", "_").replace(".", "_") + ".pdf"
                print(f"Plugin: {name},  doi:{doi},  url: {url}")
                downloaded_file = pdf_dl.download_pdf(url, safe_filename, output_dir)
                
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

    return downloaded_file