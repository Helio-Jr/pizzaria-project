from fastapi import APIRouter, Depends, HTTPException
from models.models import Usuario
from dependencies.dependencies import iniciar_sessao
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas.schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": id_usuario, "exp": data_expiracao} #geralmente usa sub na chave do id
    jwt_codigicado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codigicado

def verificar_token(token, session: Session=Depends(iniciar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.id == 1).first()
    return usuario 

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario

@auth_router.get("/")
async def autenticacao():
    return {"mensagem": "Você está na rota de autenticação do aplicativo.", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(iniciar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Já existe usuário com esse email.")
    else:
        senha_cripto = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_cripto, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"Usuário {usuario_schema.nome} cadastrado com sucesso."}
    
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(iniciar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos.")  
    else:
        acess_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {
            "access_token": acess_token,
            "refresh_token": refresh_token,
            "token type": "Bearer"
        }
            
@auth_router.post("/refresh")
async def use_refrash_token(token):
    usuario = verificar_token(token)
    acess_token = criar_token(usuario.id)
    return {
        "access_token": acess_token,
        "token type": "Bearer"
    }