from app.core.database import SessionLocal
from app.models import Source, Document, IntelligenceTopic, Event
from app.services.crawler import NetworkCrawler
from app.services.strategy_extractor import extract_strategy_events
from app.services.differ import get_text_diff

def run_strategy_collection():
    db = SessionLocal()
    try:
        strategy_topic = db.query(IntelligenceTopic).filter_by(code="STRATEGY_MP").first()
        if not strategy_topic:
            print("ERROR: STRATEGY_MP topic not found. Run seed script.")
            return

        # Use sources that were originally set up for Network (to share documents)
        network_topic = db.query(IntelligenceTopic).filter_by(code="NETWORK_GEOGRAPHIC_EXPANSION").first()
        sources = db.query(Source).filter_by(topic_id=network_topic.id).all() if network_topic else []
        
        print("=== STRATEGY & MARKET POSITIONING COLLECTION ===")
        
        for source in sources:
            print(f"\nSource: {source.name}")
            
            # Independent crawl using Strategy Vocabulary but shared Source constraint
            crawler = NetworkCrawler(db, source, topic_id_override=strategy_topic.id)
            run, new_docs, changed_docs = crawler.crawl()
            
            ai_processed = 0
            evidence_count = 0
            events_count = 0
            
            # Process NEW documents
            for i, doc in enumerate(new_docs, 1):
                print(f"[{i}/{len(new_docs)}] Analyzing new document with AI: {doc.url}")
                events = extract_strategy_events(db, str(doc.id), strategy_topic.id)
                ai_processed += 1
                events_count += len(events)
                for ev in events:
                    if ev.evidence_id:
                        evidence_count += 1
                        
            # Process CHANGED documents
            for i, doc in enumerate(changed_docs, 1):
                print(f"[{i}/{len(changed_docs)}] Analyzing changed document with AI: {doc.url}")
                prev_doc = db.query(Document).filter(
                    Document.source_id == doc.source_id,
                    Document.url == doc.url,
                    Document.id != doc.id
                ).order_by(Document.collected_at.desc()).first()
                
                ai_context = None
                if prev_doc:
                    ai_context = get_text_diff(prev_doc.text_content, doc.text_content)
                    
                events = extract_strategy_events(db, str(doc.id), strategy_topic.id, ai_context=ai_context)
                ai_processed += 1
                events_count += len(events)
                for ev in events:
                    if ev.evidence_id:
                        evidence_count += 1

            # Process UNCHANGED documents that haven't been processed for Strategy yet
            for doc in crawler.unchanged_docs:
                # Check if this document already has strategy events (or was previously evaluated)
                # For simplicity, if we don't have ANY strategy events for this document, we process it once.
                # In a robust production system, we'd have an explicit 'Evaluation' record to track "No Events Found".
                # Here we check if any Strategy Event exists for this doc.
                existing_strat_events = db.query(Event).filter(
                    Event.topic_id == strategy_topic.id,
                    Event.evidence.has(document_id=doc.id)
                ).count()
                
                if existing_strat_events == 0:
                    print(f"Analyzing historical unchanged document with AI: {doc.url}")
                    events = extract_strategy_events(db, str(doc.id), strategy_topic.id)
                    ai_processed += 1
                    events_count += len(events)
                    for ev in events:
                        if ev.evidence_id:
                            evidence_count += 1

            print(f"\nURLs discovered: {crawler.discovered_count}")
            print(f"URLs fetched: {len(new_docs) + len(changed_docs) + len(crawler.unchanged_docs)}")
            print(f"URLs from HTML: {crawler.discovered_from_html}")
            print(f"URLs from Sitemap: {crawler.discovered_from_sitemap}")
            print(f"URLs from RSS: {crawler.discovered_from_rss}")
            print()
            print(f"New documents: {len(new_docs)}")
            print(f"Changed documents: {len(changed_docs)}")
            print(f"Unchanged documents: {len(crawler.unchanged_docs)}")
            print(f"Failed URLs: {len(crawler.failed_urls)}")
            print()
            print(f"Strategy documents sent to AI Provider: {ai_processed}")
            print(f"Strategy events extracted: {events_count}")
            print(f"Evidence records created: {evidence_count}")
            print("-" * 50)
            
    finally:
        db.close()

if __name__ == "__main__":
    run_strategy_collection()
