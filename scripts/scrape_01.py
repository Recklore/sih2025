# test.py (minimal, corrected)
import os
import json
import html as html_lib
from urllib.parse import urlparse, urldefrag, parse_qsl, urlencode, urlunparse
from datetime import datetime, timezone

import scrapy
from scrapy.crawler import CrawlerProcess
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")


def normalize_url(url: str) -> str:
    url = url.strip()
    url, _ = urldefrag(url)
    p = urlparse(url)
    qs = parse_qsl(p.query, keep_blank_values=True)

    def keep(k):
        lk = k.lower()
        if lk.startswith("utm_") or lk.startswith("qt-") or lk in {"session", "sid", "jsessionid"}:
            return False
        return True

    kept = [(k, v) for k, v in qs if keep(k)]
    kept.sort()
    new_q = urlencode(kept, doseq=True)
    canon = urlunparse((p.scheme, p.netloc, p.path or "/", p.params, new_q, ""))
    if canon.endswith("/") and (p.path or "") != "/":
        canon = canon[:-1]
    return canon


def is_html_response(response: scrapy.http.Response) -> bool:
    ctype = response.headers.get("Content-Type", b"").decode("utf-8", errors="ignore").lower()
    if ctype:
        return ("text/" in ctype) or ("html" in ctype) or ("xml" in ctype)
    return urlparse(response.url).path.lower().endswith((".htm", ".html", ".php", ""))


def make_safe_filename(url: str) -> str:
    p = urlparse(url)
    net = p.netloc.replace(":", "_")
    path = p.path.strip("/").replace("/", "_") or "root"
    qs = p.query.replace("&", "_").replace("=", "-")
    base = f"{net}__{path}"
    if qs:
        base = f"{base}__{qs}"
    return base[:200] + ".html"


def make_cdata(s: str) -> str:
    if "]]>" not in s:
        return f"<![CDATA[{s}]]>"
    parts = s.split("]]>")
    return "".join(f"<![CDATA[{p}]]>" + ("<!--split-->" if i != len(parts) - 1 else "") for i, p in enumerate(parts))


def summarize_with_sarvam(text: str, logger=None) -> str:
    """
    Summarize text using Sarvam AI API.
    Falls back to truncated text if API call fails.
    """
    if not SARVAM_API_KEY:
        if logger:
            logger.warning("SARVAM_API_KEY not found in .env, using truncated text")
        return text[:2000] + "..." if len(text) > 2000 else text

    # Truncate input to avoid token limits (adjust as needed)
    input_text = text[:8000] if len(text) > 8000 else text

    try:
        # Sarvam AI API endpoint (adjust if different)
        url = "https://api.sarvam.ai/v1/chat/completions"

        headers = {"Authorization": f"Bearer {SARVAM_API_KEY}", "Content-Type": "application/json"}

        payload = {
            "model": "sarvam-2b",  # Adjust model name as per Sarvam AI docs
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise, informative summaries of webpage content.",
                },
                {
                    "role": "user",
                    "content": f"Summarize the following webpage content in 2-3 concise paragraphs, highlighting the main topics and key information:\n\n{input_text}",
                },
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        summary = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if summary:
            if logger:
                logger.debug(f"Successfully summarized text ({len(text)} -> {len(summary)} chars)")
            return summary
        else:
            raise ValueError("Empty summary returned from API")

    except Exception as e:
        if logger:
            logger.error(f"Sarvam API error: {e}. Using fallback truncation.")
        # Fallback to truncated text
        return text[:2000] + "..." if len(text) > 2000 else text


def get_file_category(url: str) -> str | None:
    """
    Determine file category based on URL extension.
    Returns 'pdf', 'docs', 'html', or None.
    Skips images, js, css files.
    """
    parsed = urlparse(url)
    path = parsed.path.lower()

    # Skip unwanted file types
    skip_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".webp",
        ".ico",
        ".css",
        ".js",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp4",
        ".mp3",
        ".avi",
        ".mov",
        ".wav",
    ]

    if any(path.endswith(ext) for ext in skip_extensions):
        return None

    # Categorize wanted files
    if path.endswith(".pdf"):
        return "pdf"

    if any(path.endswith(ext) for ext in [".doc", ".docx", ".xlsx", ".xls", ".ppt", ".pptx", ".txt"]):
        return "docs"

    if any(path.endswith(ext) for ext in [".html", ".htm"]):
        return "html"

    return None


def download_and_save_file(response: scrapy.http.Response, category: str, base_dir: str = "data") -> str | None:
    """
    Download and save file to categorized folder.
    Returns the saved file path or None on failure.
    """
    try:
        url = response.url

        # Create category directory
        category_dir = os.path.join(base_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        # Generate safe filename
        parsed = urlparse(url)
        net = parsed.netloc.replace(":", "_").replace(".", "_")
        path = parsed.path.strip("/").replace("/", "_") or "root"

        # Get original extension
        original_ext = os.path.splitext(parsed.path)[1] or ""
        if not original_ext and category == "html":
            original_ext = ".html"

        # Create unique filename
        base_name = f"{net}__{path}"
        if not base_name.endswith(original_ext):
            base_name = base_name.rsplit(".", 1)[0] if "." in base_name else base_name
            base_name += original_ext

        # Truncate if too long
        if len(base_name) > 200:
            name_part = base_name[:190]
            base_name = name_part + original_ext

        file_path = os.path.join(category_dir, base_name)

        # Handle duplicates by adding counter
        counter = 1
        original_file_path = file_path
        while os.path.exists(file_path):
            name_without_ext = os.path.splitext(original_file_path)[0]
            file_path = f"{name_without_ext}_{counter}{original_ext}"
            counter += 1

        # Write file
        with open(file_path, "wb") as f:
            f.write(response.body)

        return file_path

    except Exception as e:
        if hasattr(response, "logger"):
            response.logger.error(f"Failed to save file {response.url}: {e}")
        return None


class SitemapSpider(scrapy.Spider):
    name = "sitemap_spider"
    start_urls = ["https://www.curaj.ac.in/"]
    allowed_domains = [urlparse(start_urls[0]).netloc]

    visited_urls = set()
    pages_file = "pages.jl"
    sitemap_file = "generated_sitemap.xml"

    # File download configuration
    data_dir = "data"
    enable_file_download = True

    custom_settings = {
        "CLOSESPIDER_TIMEOUT": 120,
        "DEPTH_LIMIT": 5,
        "DOWNLOAD_DELAY": 0.5,  # Increased to be gentle on API rate limits
        "LOG_ENABLED": True,
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_FAIL_ON_DATALOSS": False,
    }

    async def start(self):
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.parse, dont_filter=True)

    def parse(self, response):
        url = normalize_url(response.url)
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)

        # Check if this is a downloadable file (PDF, docs, HTML file)
        file_category = get_file_category(response.url)

        # Download and save files to categorized folders
        if file_category and self.enable_file_download:
            file_path = download_and_save_file(response, file_category, self.data_dir)
            if file_path:
                self.logger.info(f"📁 Saved {file_category}: {url} → {file_path}")

        # Continue with HTML page processing (summarization)
        if not is_html_response(response):
            self.logger.debug(f"Skipping non-HTML: {response.url}")
            return

        raw_html = response.text or ""
        title = response.xpath("//title/text()").get() or ""
        text_nodes = response.xpath("//body//text()[normalize-space()]").getall()
        content_text = " ".join(t.strip() for t in text_nodes)
        content_text = html_lib.unescape(content_text)

        fetched_at = datetime.now(timezone.utc).isoformat()

        # Generate summary using Sarvam AI
        summary = summarize_with_sarvam(content_text, logger=self.logger)

        rec = {
            "url": url,
            "title": title.strip(),
            "summary": summary,
            "fetched_at": fetched_at,
        }

        with open(self.pages_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

        self.logger.info(f"Saved page: {url}")

        domain_root = urlparse(response.url).scheme + "://" + urlparse(response.url).netloc
        for link in response.css("a::attr(href)").getall():
            absolute = response.urljoin(link)
            absolute = normalize_url(absolute)
            if absolute.startswith(domain_root) and absolute not in self.visited_urls:
                yield scrapy.Request(absolute, callback=self.parse)

    def closed(self, reason):
        now = datetime.now(timezone.utc).isoformat()
        with open(self.sitemap_file, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            if os.path.exists(self.pages_file):
                with open(self.pages_file, "r", encoding="utf-8") as fh:
                    for line in fh:
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        loc = rec.get("url")
                        lastmod = rec.get("fetched_at", now)
                        summary = rec.get("summary", "")
                        summary_escaped = html_lib.escape(summary)
                        f.write("  <url>\n")
                        f.write(f"    <loc>{loc}</loc>\n")
                        f.write(f"    <lastmod>{lastmod}</lastmod>\n")
                        f.write(f"    <content>{make_cdata(summary_escaped)}</content>\n")
                        f.write("  </url>\n")
            f.write("</urlset>\n")
        self.logger.info(f"[✅] Sitemap saved as {self.sitemap_file} ({len(self.visited_urls)} urls)")
        self.logger.info(f"[✅] Page records saved as {self.pages_file}")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(SitemapSpider)
    process.start()
