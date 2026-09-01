import httpx
import hashlib
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models import Source, Document, CollectionRun

def get_utc_now():
    return datetime.now(timezone.utc)

import logging
from readability import Document as ReadabilityDocument

logger = logging.getLogger(__name__)

def extract_dates_from_html(soup: BeautifulSoup):
    """Conservatively extract dates from HTML metadata."""
    published_at = None
    updated_at = None
    
    # Try OpenGraph/Article tags
    pub_meta = soup.find("meta", property="article:published_time") or soup.find("meta", attrs={"name": "publication_date"})
    if pub_meta and pub_meta.get("content"):
        try:
            published_at = datetime.fromisoformat(pub_meta["content"].replace("Z", "+00:00"))
        except ValueError:
            pass
            
    upd_meta = soup.find("meta", property="article:modified_time") or soup.find("meta", attrs={"name": "updated_date"})
    if upd_meta and upd_meta.get("content"):
        try:
            updated_at = datetime.fromisoformat(upd_meta["content"].replace("Z", "+00:00"))
        except ValueError:
            pass

    return published_at, updated_at

def collect_url(db: Session, source_id: str, url: str, run: CollectionRun):
    """
    Fetches the specific URL, extracts content, dates and links,
    handles deduplication, and returns (Document, status, links).
    Status can be: "NEW", "UNCHANGED", "CHANGED", or "FAILED".
    """
    try:
        with httpx.Client(timeout=15.0, headers={"User-Agent": "Mozilla/5.0 PalletwaysCI/1.0"}, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract links before removing elements
            links = []
            doc_title = soup.title.string.strip() if soup.title and soup.title.string else ""
            for a_tag in soup.find_all("a", href=True):
                links.append({
                    "href": a_tag["href"],
                    "anchor_text": a_tag.get_text(separator=" ", strip=True),
                    "referring_title": doc_title
                })
            
            # Attempt to extract clean article content using Readability
            text_content = ""
            try:
                r_doc = ReadabilityDocument(html)
                summary_html = r_doc.summary()
                r_soup = BeautifulSoup(summary_html, "html.parser")
                text_content = r_soup.get_text(separator="\n").strip()
            except Exception as e:
                logger.warning(f"Readability extraction failed for {url}: {e}")

            # Fallback to BeautifulSoup if Readability fails or returns empty/too small
            if not text_content or len(text_content) < 100:
                for script in soup(["script", "style"]):
                    script.extract()
                text_content = soup.get_text(separator="\n").strip()
    
            # Remove PostgreSQL incompatible null bytes from scraped text
            if text_content:
                text_content = text_content.replace("\x00", "")
            
            # Simple content hash for deduplication
            content_hash = hashlib.sha256(text_content.encode("utf-8")).hexdigest()
            
            # Extract Dates
            published_at, updated_at = extract_dates_from_html(soup)
            
            # Check for deduplication
            # The DB enforces uq_source_content_hash, so we check if ANY doc
            # in this source has the exact same content hash.
            existing_doc = db.query(Document).filter(
                Document.source_id == source_id,
                Document.content_hash == content_hash
            ).first()
            
            run.items_found += 1
            
            if existing_doc:
                # Content unchanged (or exact duplicate found elsewhere on site)
                run.items_duplicate += 1
                return existing_doc, "UNCHANGED", links
            else:
                # Check if this URL previously existed but changed
                latest_url_doc = db.query(Document).filter(
                    Document.source_id == source_id,
                    Document.url == url
                ).order_by(Document.collected_at.desc()).first()
                
                # New content or changed content
                doc = Document(
                    source_id=source_id,
                    url=url,
                    title=soup.title.string if soup.title else None,
                    content_type=response.headers.get("content-type"),
                    content_hash=content_hash,
                    text_content=text_content,
                    source_published_at=published_at,
                    source_updated_at=updated_at,
                    collected_at=get_utc_now()
                )
                db.add(doc)
                
                if latest_url_doc:
                    # It's a changed document (hash is different)
                    run.items_updated += 1
                    status = "CHANGED"
                else:
                    # Brand new URL
                    run.items_new += 1
                    status = "NEW"
                
                db.commit()
                db.refresh(doc)
                return doc, status, links
                
    except Exception as e:
        run.error_message = str(e)
        run.items_failed += 1
        db.commit()
        return None, "FAILED", []
