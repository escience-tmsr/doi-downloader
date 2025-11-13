from doi_downloader import loader as ld
from doi_downloader import pdf_download as pdf_dl
from doi_downloader.benchmark import BenchmarkLogger, BenchmarkContext
import os

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
        # Create benchmark context if enabled
        if enable_benchmark:
            ctx = BenchmarkContext(
                benchmark_logger, 
                doi=doi, 
                plugin_name=name,
                journal_domain=journal_domain
            )
        else:
            ctx = None
        
        try:
            if ctx:
                ctx.__enter__()
            
            url = plugin.get_pdf_url(doi, ctx)
            
            if url:
                # Mark URL resolution success
                if ctx:
                    ctx.mark_url_resolved(url)
                
                # Sanitize DOI for filename
                safe_filename = doi.replace("/", "_").replace(".", "_") + ".pdf"
                print(f"Plugin: {name},  doi:{doi},  url: {url}")
                downloaded_file = pdf_dl.download_pdf(url, safe_filename, output_dir)
                
                if downloaded_file:
                    # Mark download success
                    if ctx:
                        ctx.mark_pdf_downloaded(downloaded_file)
                    break
        
        finally:
            if ctx:
                ctx.__exit__(None, None, None)
        
        # If we got here without downloading, the attempt failed
        # It should already be logged by context manager

    return downloaded_file