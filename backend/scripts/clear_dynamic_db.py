from app.core.database import SessionLocal
from app.models import Signal, Event, Evidence, Document, CollectionRun

def clear_dynamic_data():
    db = SessionLocal()
    try:
        # Delete in order to respect foreign key constraints
        
        print("Deleting Signals...")
        db.query(Signal).delete()
        
        print("Deleting Events...")
        db.query(Event).delete()
        
        print("Deleting Evidence...")
        db.query(Evidence).delete()
        
        print("Deleting Documents...")
        db.query(Document).delete()
        
        print("Deleting CollectionRuns...")
        db.query(CollectionRun).delete()
        
        db.commit()
        print("\nSuccessfully cleared all dynamic records!")
        print("You can now run the pipeline from a completely clean slate.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_dynamic_data()
