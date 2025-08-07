from fastapi import APIRouter, Depends, dependencies, HTTPException
from schemas.schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from dependencies.dependencies import iniciar_sessao, verificar_token   
from sqlalchemy.orm import Session
from models.models import Pedidos, Usuario, ItensPedido
from typing import List

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

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(iniciar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para listar os pedidos.")
    else:
        pedidos = session.query(Pedidos).all()
    return {
        "pedidos": pedidos
    } 

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int,
                                item_pedido_schema: ItemPedidoSchema, 
                                session: Session = Depends(iniciar_sessao),
                                usuario: Usuario = Depends(verificar_token)):
    
    pedido = session.query(Pedidos).filter(Pedidos.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id!=pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para excluir esse pedido.")
    
    item_pedido = ItensPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem":"Item criado com sucesso.",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int,
                                session: Session = Depends(iniciar_sessao),
                                usuario: Usuario = Depends(verificar_token)):
    
    item_pedido = session.query(ItensPedido).filter(ItensPedido.id==id_item_pedido).first()
    pedido = session.query(Pedidos).filter(Pedidos.id==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item não encontrado.")
    if not usuario.admin and usuario.id!=pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para excluir um item.")
    
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem":"Item removido com sucesso.",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(iniciar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    
    if not usuario.admin and usuario.id!=pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para finalizar esse pedido.")

    pedido.status = "Finalizado"
    session.commit()
    return {
        "mensagem": f"Pedido número {pedido.id} finalizado com sucesso",
        "pedido": pedido
    }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(iniciar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedidos).filter(Pedidos.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    
    if not usuario.admin and usuario.id!=pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para finalizar esse pedido.")
    
    return {
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.get("/listar/{id_usuario}", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(id_usuario: int, session: Session = Depends(iniciar_sessao), usuario: Usuario = Depends(verificar_token)):
    
    if not usuario.admin and usuario.id!=id_usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para listar os pedidos.")
    else:
        pedidos = session.query(Pedidos).filter(Pedidos.usuario==id_usuario).all()

    return pedidos