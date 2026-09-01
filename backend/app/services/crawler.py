import urllib.parse
import urllib.robotparser
import logging
import heapq
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
import feedparser

from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import Source, CollectionRun, Document, IntelligenceTopic
from app.services.collector import collect_url, get_utc_now

logger = logging.getLogger(__name__)

@dataclass
class CandidateURL:
    url: str
    anchor_text: str = ""
    referring_url: str = ""
    referring_title: str = ""
    discovery_source: str = "HTML"
    publish_date: Optional[datetime] = None
    score: int = 0
    depth: int = 0

class NetworkCrawler:
    def __init__(self, db: Session, source: Source, topic_id_override=None):
        self.db = db
        self.source = source
        self.topic_id = topic_id_override or source.topic_id
        self.max_depth = settings.network_crawl_max_depth
        self.max_pages = settings.network_crawl_max_pages
        self.domain = source.domain
        
        self.visited = set()
        # Priority queue stores (-score, depth, counter, candidate)
        self.queue = []
        self.counter = 0
        
        self.rp = urllib.robotparser.RobotFileParser()
        self.rp_initialized = False
        
        # Results
        self.new_docs = []
        self.changed_docs = []
        self.unchanged_docs = []
        self.failed_urls = []
        
        # Discovery Stats
        self.discovered_from_html = 0
        self.discovered_from_sitemap = 0
        self.discovered_from_rss = 0
        self.discovered_count = 1 # Seed URL
        
        # Topic Vocabulary
        self.vocabulary = []
        self._load_vocabulary()
        
    def _load_vocabulary(self):
        topic = self.db.query(IntelligenceTopic).filter(IntelligenceTopic.id == self.topic_id).first()
        if topic and topic.topic_vocabulary:
            vocab = topic.topic_vocabulary
            if isinstance(vocab, dict):
                # Flatten categorical JSONB
                for key, words in vocab.items():
                    if isinstance(words, list):
                        self.vocabulary.extend([str(w).lower() for w in words])
            elif isinstance(vocab, list):
                self.vocabulary.extend([str(w).lower() for w in vocab])

    def score_candidate(self, candidate: CandidateURL) -> int:
        """Multi-signal deterministic scoring engine."""
        url_lower = candidate.url.lower()
        anchor_lower = candidate.anchor_text.lower()
        referrer_title_lower = candidate.referring_title.lower()
        referrer_url_lower = candidate.referring_url.lower()
        
        # 1. Irrelevant penalty
        if any(x in url_lower for x in ["/login", "/cart", "/checkout", "/account", "mailto:", "tel:", "javascript:", ".pdf", ".jpg"]):
            return -100
            
        score = 0
        
        # 2. URL Score
        for word in self.vocabulary:
            if f"/{word}" in url_lower or f"{word}-" in url_lower or f"-{word}" in url_lower:
                score += 10
                
        # 3. Anchor Score
        for word in self.vocabulary:
            if word in anchor_lower.split():
                score += 15
                
        # 4. Referrer Score
        news_indicators = ["news", "press", "blog", "insight", "announcement", "resource", "newsroom"]
        if any(ind in referrer_title_lower for ind in news_indicators) or any(ind in referrer_url_lower for ind in news_indicators):
            score += 10
            
        # 5. Source Type Score
        if candidate.discovery_source == "RSS":
            score += 20
        elif candidate.discovery_source == "SITEMAP":
            if "news" in url_lower or "blog" in url_lower or "article" in url_lower:
                score += 15
            else:
                score += 5
                
        # 6. Recency Score (Bonus if within last 90 days)
        if candidate.publish_date:
            try:
                days_old = (get_utc_now() - candidate.publish_date).days
                if days_old <= 90:
                    score += 20
                elif days_old <= 365:
                    score += 10
            except Exception:
                pass
                
        # 7. Pagination and Archive Navigation Score
        pagination_indicators = ["?page=", "/page/", "older", "next", "previous", "load more", "archive"]
        if any(ind in url_lower or ind in anchor_lower for ind in pagination_indicators):
            if any(news_ind in referrer_url_lower or news_ind in referrer_title_lower for news_ind in news_indicators):
                score += 25
            else:
                score += 10
                
        return score

    def _init_robots(self):
        if not self.rp_initialized:
            parsed = urllib.parse.urlparse(self.source.url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            self.rp.set_url(robots_url)
            try:
                with httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0 PalletwaysCI/1.0"}, follow_redirects=True) as client:
                    resp = client.get(robots_url)
                    if resp.status_code == 200:
                        lines = resp.text.splitlines()
                        self.rp.parse(lines)
                    else:
                        self.rp.allow_all = True
            except Exception as e:
                logger.warning(f"Failed to read robots.txt for {self.source.url}: {e}")
                self.rp = None
            self.rp_initialized = True

    def _can_fetch(self, url: str) -> bool:
        self._init_robots()
        if self.rp is not None:
            return self.rp.can_fetch("*", url)
        return True

    def normalize_url(self, base_url: str, link: str) -> str:
        link = link.split('#')[0]
        abs_url = urllib.parse.urljoin(base_url, link)
        parsed = urllib.parse.urlparse(abs_url)
        if parsed.scheme not in ["http", "https"]:
            return None
        if self.domain not in parsed.netloc:
            return None
        return abs_url

    def _push_candidate(self, candidate: CandidateURL):
        if candidate.url in self.visited:
            return
        candidate.score = self.score_candidate(candidate)
        if candidate.score >= 0:
            self.counter += 1
            heapq.heappush(self.queue, (-candidate.score, candidate.depth, self.counter, candidate))

    def _discover_sitemaps(self):
        self._init_robots()
        sitemap_urls = []
        if self.rp and self.rp.site_maps():
            sitemap_urls.extend(self.rp.site_maps())
            
        parsed = urllib.parse.urlparse(self.source.url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if not sitemap_urls:
            sitemap_urls = [f"{base}/sitemap.xml", f"{base}/sitemap_index.xml"]
            
        for sm_url in sitemap_urls:
            try:
                with httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0 PalletwaysCI/1.0"}, follow_redirects=True) as client:
                    resp = client.get(sm_url)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.content, "xml")
                        # Handle sitemapindex
                        for sitemap_tag in soup.find_all("sitemap"):
                            loc = sitemap_tag.find("loc")
                            if loc and loc.text:
                                if loc.text not in sitemap_urls:
                                    sitemap_urls.append(loc.text)
                                    
                        # Handle url
                        for url_tag in soup.find_all("url"):
                            loc = url_tag.find("loc")
                            if loc and loc.text:
                                norm_url = self.normalize_url(base, loc.text)
                                if norm_url:
                                    self.discovered_from_sitemap += 1
                                    self.discovered_count += 1
                                    
                                    pub_date = None
                                    lastmod = url_tag.find("lastmod")
                                    if lastmod and lastmod.text:
                                        try:
                                            # basic parsing
                                            dt_str = lastmod.text.replace("Z", "+00:00")
                                            if len(dt_str) == 10: # YYYY-MM-DD
                                                dt_str += "T00:00:00+00:00"
                                            pub_date = datetime.fromisoformat(dt_str)
                                            if pub_date.tzinfo is None:
                                                pub_date = pub_date.replace(tzinfo=timezone.utc)
                                        except ValueError:
                                            pass
                                            
                                    candidate = CandidateURL(
                                        url=norm_url,
                                        discovery_source="SITEMAP",
                                        publish_date=pub_date,
                                        depth=1
                                    )
                                    self._push_candidate(candidate)
            except Exception as e:
                logger.warning(f"Failed to fetch sitemap {sm_url}: {e}")

    def _discover_rss(self, current_url: str):
        try:
            with httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0 PalletwaysCI/1.0"}, follow_redirects=True) as client:
                resp = client.get(current_url)
                if resp.status_code != 200:
                    return
                html = resp.text
        except Exception:
            return
            
        soup = BeautifulSoup(html, "html.parser")
        feed_urls = []
        for link in soup.find_all("link", type=lambda t: t in ["application/rss+xml", "application/atom+xml"]):
            href = link.get("href")
            if href:
                norm_url = self.normalize_url(current_url, href)
                if norm_url:
                    feed_urls.append(norm_url)
                    
        for feed_url in feed_urls:
            try:
                with httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0 PalletwaysCI/1.0"}, follow_redirects=True) as client:
                    resp = client.get(feed_url)
                    if resp.status_code == 200:
                        feed = feedparser.parse(resp.content)
                        for entry in feed.entries:
                            if hasattr(entry, 'link'):
                                norm_url = self.normalize_url(feed_url, entry.link)
                                if norm_url:
                                    self.discovered_from_rss += 1
                                    self.discovered_count += 1
                                    
                                    pub_date = None
                                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                        import time
                                        pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)
                                        
                                    title = entry.title if hasattr(entry, 'title') else ""
                                    
                                    candidate = CandidateURL(
                                        url=norm_url,
                                        anchor_text=title,
                                        discovery_source="RSS",
                                        publish_date=pub_date,
                                        depth=1
                                    )
                                    self._push_candidate(candidate)
            except Exception as e:
                logger.warning(f"Failed to fetch RSS {feed_url}: {e}")

    def crawl(self) -> Tuple[CollectionRun, List[Document], List[Document]]:
        run = CollectionRun(source_id=self.source.id, started_at=get_utc_now(), status="RUNNING")
        self.db.add(run)
        self.db.commit()
        
        # Discover sitemaps first
        self._discover_sitemaps()
        
        # Add seed URL
        seed_candidate = CandidateURL(url=self.source.url, discovery_source="HTML", depth=0)
        seed_candidate.score = 100 # Highest priority
        self.counter += 1
        heapq.heappush(self.queue, (-seed_candidate.score, seed_candidate.depth, self.counter, seed_candidate))
        
        pages_fetched = 0
        
        while self.queue and pages_fetched < self.max_pages:
            neg_score, depth, _, candidate = heapq.heappop(self.queue)
            current_url = candidate.url
            
            if current_url in self.visited:
                continue
                
            self.visited.add(current_url)
            
            if not self._can_fetch(current_url):
                self.failed_urls.append(current_url)
                continue
                
            # Fetch using collector
            doc, status, links = collect_url(self.db, str(self.source.id), current_url, run)
            pages_fetched += 1
            
            if status == "FAILED":
                self.failed_urls.append(current_url)
                continue
            elif status == "NEW":
                self.new_docs.append(doc)
            elif status == "CHANGED":
                self.changed_docs.append(doc)
            elif status == "UNCHANGED":
                self.unchanged_docs.append(doc)
                
            # Discover RSS from the fetched HTML if it's the seed page
            if depth == 0:
                self._discover_rss(current_url)
                
            # Discover HTML links if depth allows
            if depth < self.max_depth:
                for link_data in links:
                    norm_url = self.normalize_url(current_url, link_data["href"])
                    if norm_url and norm_url not in self.visited:
                        self.discovered_from_html += 1
                        self.discovered_count += 1
                        
                        new_candidate = CandidateURL(
                            url=norm_url,
                            anchor_text=link_data.get("anchor_text", ""),
                            referring_url=current_url,
                            referring_title=link_data.get("referring_title", ""),
                            discovery_source="HTML",
                            depth=depth + 1
                        )
                        self._push_candidate(new_candidate)
        
        run.completed_at = get_utc_now()
        run.status = "SUCCESS"
        self.db.commit()
        
        return run, self.new_docs, self.changed_docs
