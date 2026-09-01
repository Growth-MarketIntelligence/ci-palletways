import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from app.models.base import Base
from app.core.config import settings

@pytest.fixture(scope="session")
def engine():
    test_db_url = settings.test_database_url
    engine = create_engine(test_db_url)
    
    if database_exists(engine.url):
        drop_database(engine.url)
    
    create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    engine.dispose()
    drop_database(engine.url)

@pytest.fixture(scope="function")
def db(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
