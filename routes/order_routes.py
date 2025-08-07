from fastapi import APIRouter, Depends, dependencies, HTTPException
from schemas.schemas import PedidoSchema
from dependencies.dependencies import iniciar_sessao, verificar_token   
from sqlalchemy.orm import Session
from models.models import Pedidos, Usuario

order_router = APIRouter(prefix="/order", tags=["order"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    return {"mensagem": "Você está na rota de pedidos do aplicativo."}

@order_router.post("/pedido")
async def gerar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(iniciar_sessao)):
    novo_pedido = Pedidos(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem":f"Pedido {novo_pedido.id} criado com sucesso."}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(iniciar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    
    if not usuario.admin and usuario.id!=pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para excluir esse pedido.")

    pedido.status = "Cancelado"
    session.commit()
    return {
        "mensagem": f"Pedido número {pedido.id} cancelado com sucesso",
        "pedido": pedido
    }
