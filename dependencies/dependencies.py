from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models.models import db
from sqlalchemy.orm import sessionmaker, Session
from models.models import Usuario
from jose import jwt, JWTError

def iniciar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session=Depends(iniciar_sessao)):
    print("--------------------------------")
    print(token)
    try:
        dic_info =  jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = dic_info.get("sub")
        print(id_usuario)
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado! Verifique a validade do token.")
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido! Usuário não existe.")
    return usuario 