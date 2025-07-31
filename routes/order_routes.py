from fastapi import APIRouter

order_router = APIRouter(prefix="/order", tags=["order"])

@order_router.get("/")
async def ordem():
    return {"mensagem": "Você está na rota de pedidos do aplicativo."}