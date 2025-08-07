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
    try:
        dic_info =  jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError as erro:
        print(erro)
        raise HTTPException(status_code=401, detail="Acesso Negado! Verifique a validade do token.")
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido! Usuário não existe.")
    return usuario 