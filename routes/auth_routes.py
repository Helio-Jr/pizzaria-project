from fastapi import APIRouter, Depends, HTTPException
from models.models import Usuario
from dependencies.dependencies import iniciar_sessao
from main import bcrypt_context
from schemas.schemas import UsuarioSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["auth"])

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