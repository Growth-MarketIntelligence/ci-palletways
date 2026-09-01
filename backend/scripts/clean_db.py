from app.core.database import SessionLocal
from app.models import Event, Evidence, Signal, Document, CollectionRun

def clean_database():
    db = SessionLocal()
    try:
        # Delete generated intelligence and collection data
        print(f"Deleting {db.query(Signal).count()} Signals...")
        db.query(Signal).delete()
        
        print(f"Deleting {db.query(Event).count()} Events...")
        db.query(Event).delete()
        
        print(f"Deleting {db.query(Evidence).count()} Evidence...")
        db.query(Evidence).delete()
        
        print(f"Deleting {db.query(Document).count()} Documents...")
        db.query(Document).delete()
        
        print(f"Deleting {db.query(CollectionRun).count()} CollectionRuns...")
        db.query(CollectionRun).delete()
        
        db.commit()
        print("Database successfully wiped of fabricated data.")
    except Exception as e:
        db.rollback()
        print(f"Error cleaning DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
