from fastapi import APIRouter, Depends
from schemas.schemas import PedidoSchema
from dependencies.dependencies import iniciar_sessao, verificar_token   
from sqlalchemy.orm import Session
from models.models import Pedidos

order_router = APIRouter(prefix="/order", tags=["order"])

@order_router.get("/")
async def pedidos():
    return {"mensagem": "Você está na rota de pedidos do aplicativo."}

@order_router.post("/pedido")
async def gerar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(iniciar_sessao)):
    novo_pedido = Pedidos(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem":f"Pedido {novo_pedido.id} criado com sucesso."}