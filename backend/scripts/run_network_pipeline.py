from app.core.database import SessionLocal
from app.models import Source, Document, IntelligenceTopic
from app.services.crawler import NetworkCrawler
from app.services.extractor import extract_network_events
from app.services.signal_generator import generate_network_signals
from app.services.differ import get_text_diff

def run_pipeline():
    db = SessionLocal()
    try:
        topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
        sources = db.query(Source).filter_by(topic_id=topic.id).all() if topic else []
        
        print("Network Pipeline Run\n--------------------")
        for source in sources:
            print(f"\nCompetitor: {source.name}")
            
            crawler = NetworkCrawler(db, source)
            run, new_docs, changed_docs = crawler.crawl()
            
            ai_processed = 0
            evidence_count = 0
            events_count = 0
            signals_count = 0
            
            # Process NEW documents
            for doc in new_docs:
                events = extract_network_events(db, str(doc.id))
                ai_processed += 1
                events_count += len(events)
                for ev in events:
                    if ev.evidence_id:
                        evidence_count += 1
                        
            # Process CHANGED documents
            for doc in changed_docs:
                # Find previous document
                prev_doc = db.query(Document).filter(
                    Document.source_id == doc.source_id,
                    Document.url == doc.url,
                    Document.id != doc.id
                ).order_by(Document.collected_at.desc()).first()
                
                ai_context = None
                if prev_doc:
                    ai_context = get_text_diff(prev_doc.text_content, doc.text_content)
                    
                events = extract_network_events(db, str(doc.id), ai_context=ai_context)
                ai_processed += 1
                events_count += len(events)
                for ev in events:
                    if ev.evidence_id:
                        evidence_count += 1
            
            # Generate Signals
            signal = generate_network_signals(db, str(source.competitor_id))
            if signal:
                signals_count = 1

            print(f"Seed URLs: 1")
            print(f"HTML candidates: {crawler.discovered_from_html}")
            print(f"Sitemap candidates: {crawler.discovered_from_sitemap}")
            print(f"RSS candidates: {crawler.discovered_from_rss}")
            print(f"Unique candidates: {crawler.discovered_count}")
            # High priority > 0
            high_pri = sum(1 for c in crawler.queue if -c[0] > 0)
            print(f"High-priority candidates: {high_pri}")
            
            print(f"URLs fetched: {len(new_docs) + len(changed_docs) + len(crawler.unchanged_docs)}")
            print(f"New Documents: {len(new_docs)}")
            print(f"Changed Documents: {len(changed_docs)}")
            print(f"Unchanged Documents: {len(crawler.unchanged_docs)}")
            print(f"Failed URLs: {len(crawler.failed_urls)}")
            print(f"AI processed: {ai_processed}")
            print(f"Evidence created: {evidence_count}")
            print(f"Events created: {events_count}")
            print(f"Signals created: {signals_count}")
            print("-" * 50)
    finally:
        db.close()

if __name__ == "__main__":
    run_pipeline()
