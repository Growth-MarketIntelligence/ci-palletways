import pytest
import respx
import httpx
from datetime import datetime, timezone
from app.services.crawler import NetworkCrawler, CandidateURL
from app.models import Source, Market, Competitor, IntelligenceTopic, CollectionRun
from app.services.collector import get_utc_now

@pytest.fixture
def setup_crawler_data(db):
    market = db.query(Market).filter_by(country_code="GB").first()
    if not market:
        market = Market(name="United Kingdom", country_code="GB")
        db.add(market)
    
    comp = db.query(Competitor).filter_by(canonical_name="CrawlComp").first()
    if not comp:
        comp = Competitor(name="CrawlComp", canonical_name="CrawlComp")
        db.add(comp)
    
    topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
    if not topic:
        topic = IntelligenceTopic(
            code="NETWORK_GEOGRAPHIC_EXPANSION", 
            name="Network",
            topic_vocabulary={
                "core": ["network", "depot"],
                "expansion": ["expand", "new"],
                "membership": ["join", "joins"]
            }
        )
        db.add(topic)
    else:
        topic.topic_vocabulary = {
            "core": ["network", "depot"],
            "expansion": ["expand", "new"],
            "membership": ["join", "joins"]
        }
        db.add(topic)
    db.commit()
    
    source = Source(
        competitor_id=comp.id,
        market_id=market.id,
        topic_id=topic.id,
        source_type="Website",
        name="Crawl Source",
        url="https://test.crawl.com/",
        domain="test.crawl.com",
        collection_enabled=True,
    )
    db.add(source)
    db.commit()
    return source

def test_relevance_scoring(db, setup_crawler_data):
    source = setup_crawler_data
    crawler = NetworkCrawler(db, source)
    
    # 1. URL keyword match
    c1 = CandidateURL(url="https://test.crawl.com/network")
    assert crawler.score_candidate(c1) >= 10
    
    # 2. Strong anchor text, no URL keyword
    c2 = CandidateURL(url="https://test.crawl.com/article1", anchor_text="Company joins the network")
    assert crawler.score_candidate(c2) >= 30 # "joins" (15) + "network" (15) = 30
    
    # 3. Strong referrer context
    c3 = CandidateURL(url="https://test.crawl.com/article2", referring_title="Company Newsroom")
    assert crawler.score_candidate(c3) >= 10
    
    # 4. Unknown/Zero score
    c4 = CandidateURL(url="https://test.crawl.com/about-us")
    assert crawler.score_candidate(c4) == 0
    
    # 5. Irrelevant penalty
    c5 = CandidateURL(url="https://test.crawl.com/login")
    assert crawler.score_candidate(c5) < 0
    
    # 6. Recency
    c6 = CandidateURL(url="https://test.crawl.com/article3", publish_date=get_utc_now())
    assert crawler.score_candidate(c6) >= 20

def test_url_normalization(db, setup_crawler_data):
    source = setup_crawler_data
    crawler = NetworkCrawler(db, source)
    base = "https://test.crawl.com/"
    assert crawler.normalize_url(base, "/about") == "https://test.crawl.com/about"
    assert crawler.normalize_url(base, "https://other.com/about") is None

@respx.mock
def test_palletforce_style_discovery(db, setup_crawler_data):
    source = setup_crawler_data
    crawler = NetworkCrawler(db, source)
    crawler.max_depth = 1
    crawler.max_pages = 5
    
    html_seed = "<html><head><title>Newsroom</title></head><body><a href='/en/currie-solutions-joins-palletforce-to-grow-pallet-business/'>Currie Solutions joins Palletforce to grow pallet business</a></body></html>"
    respx.get("https://test.crawl.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/sitemap.xml").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/sitemap_index.xml").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/").mock(return_value=httpx.Response(200, text=html_seed))
    respx.get("https://test.crawl.com/en/currie-solutions-joins-palletforce-to-grow-pallet-business/").mock(return_value=httpx.Response(200, text="content"))
    
    run, new_docs, changed_docs = crawler.crawl()
    
    assert "https://test.crawl.com/en/currie-solutions-joins-palletforce-to-grow-pallet-business/" in crawler.visited
    assert crawler.discovered_from_html == 1

@respx.mock
def test_sitemap_discovery(db, setup_crawler_data):
    source = setup_crawler_data
    crawler = NetworkCrawler(db, source)
    crawler.max_depth = 0
    
    respx.get("https://test.crawl.com/robots.txt").mock(return_value=httpx.Response(404))
    
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
       <url>
          <loc>https://test.crawl.com/news/1</loc>
          <lastmod>2023-01-01</lastmod>
       </url>
    </urlset>'''
    respx.get("https://test.crawl.com/sitemap.xml").mock(return_value=httpx.Response(200, text=sitemap_xml))
    respx.get("https://test.crawl.com/sitemap_index.xml").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/").mock(return_value=httpx.Response(200, text="seed"))
    respx.get("https://test.crawl.com/news/1").mock(return_value=httpx.Response(200, text="news"))
    
    run, new_docs, changed_docs = crawler.crawl()
    assert crawler.discovered_from_sitemap == 1
    assert "https://test.crawl.com/news/1" in crawler.visited

@respx.mock
def test_rss_discovery(db, setup_crawler_data):
    source = setup_crawler_data
    crawler = NetworkCrawler(db, source)
    crawler.max_depth = 0
    
    respx.get("https://test.crawl.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/sitemap.xml").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/sitemap_index.xml").mock(return_value=httpx.Response(404))
    
    html_seed = "<html><head><link rel='alternate' type='application/rss+xml' href='/feed.xml' /></head><body></body></html>"
    respx.get("https://test.crawl.com/").mock(return_value=httpx.Response(200, text=html_seed))
    
    rss_xml = '''<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
      <title>Feed</title>
      <item>
        <title>Article joins network</title>
        <link>https://test.crawl.com/rss-article</link>
      </item>
    </channel>
    </rss>'''
    respx.get("https://test.crawl.com/feed.xml").mock(return_value=httpx.Response(200, text=rss_xml))
    respx.get("https://test.crawl.com/rss-article").mock(return_value=httpx.Response(200, text="article"))
    
    run, new_docs, changed_docs = crawler.crawl()
    assert crawler.discovered_from_rss == 1
    assert "https://test.crawl.com/rss-article" in crawler.visited

@respx.mock
def test_crawler_unchanged_docs(db, setup_crawler_data):
    source = setup_crawler_data
    crawler1 = NetworkCrawler(db, source)
    crawler1.max_pages = 1
    
    respx.get("https://test.crawl.com/robots.txt").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/sitemap.xml").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/sitemap_index.xml").mock(return_value=httpx.Response(404))
    respx.get("https://test.crawl.com/").mock(return_value=httpx.Response(200, text="same content"))
    
    # Run 1
    run1, new1, changed1 = crawler1.crawl()
    assert len(new1) == 1
    
    # Run 2
    crawler2 = NetworkCrawler(db, source)
    crawler2.max_pages = 1
    run2, new2, changed2 = crawler2.crawl()
    
    assert len(new2) == 0
    assert len(changed2) == 0
    assert len(crawler2.unchanged_docs) == 1
