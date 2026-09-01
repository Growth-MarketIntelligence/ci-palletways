from app.core.database import SessionLocal
from app.models import Source, Document, Evidence, Event, Signal
from sqlalchemy import text

def cleanup():
    db = SessionLocal()
    try:
        # Keep only these valid names defined in your register script
        valid_names = ["Palletforce", "Pall-Ex", "Palletline", "Fortec Distribution"]
        
        sources_to_delete = db.query(Source).filter(~Source.name.in_(valid_names)).all()
        
        if not sources_to_delete:
            print("No old sources found to delete.")
            return

        source_ids = [s.id for s in sources_to_delete]
        print(f"Found {len(source_ids)} old sources to delete. Cleaning up...")
        
        # Bottom-up deletion to avoid foreign key constraint errors
        docs_to_delete = db.query(Document).filter(Document.source_id.in_(source_ids)).all()
        doc_ids = [d.id for d in docs_to_delete]
        
        if doc_ids:
            evidences = db.query(Evidence).filter(Evidence.document_id.in_(doc_ids)).all()
            evidence_ids = [e.id for e in evidences]
            
            if evidence_ids:
                events = db.query(Event).filter(Event.evidence_id.in_(evidence_ids)).all()
                event_ids = [e.id for e in events]
                
                if event_ids:
                    db.query(Signal).filter(Signal.event_id.in_(event_ids)).delete(synchronize_session=False)
                    
                    # Delete from insight_supporting_events join table using raw SQL
                    event_ids_str = ','.join(f"'{str(eid)}'" for eid in event_ids)
                    db.execute(text(f"DELETE FROM insight_supporting_events WHERE event_id IN ({event_ids_str})"))
                    
                    db.query(Event).filter(Event.id.in_(event_ids)).delete(synchronize_session=False)
                
                db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).delete(synchronize_session=False)
            
            db.query(Document).filter(Document.id.in_(doc_ids)).delete(synchronize_session=False)
            
        for s in sources_to_delete:
            print(f"Deleting source: {s.name} ({s.url})")
            db.delete(s)
            
        db.commit()
        print("Cleanup complete!")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
