from models.models import db
from sqlalchemy.orm import sessionmaker

def iniciar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()