from app.core.database import SessionLocal
from app.models import Signal, SignalEvent

def clean_signals():
    db = SessionLocal()
    try:
        print(f"Deleting {db.query(SignalEvent).count()} SignalEvents...")
        db.query(SignalEvent).delete()
        
        print(f"Deleting {db.query(Signal).count()} Signals...")
        db.query(Signal).delete()
        
        db.commit()
        print("Successfully wiped all old signals. Events remain intact.")
    except Exception as e:
        db.rollback()
        print(f"Error cleaning signals: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_signals()
