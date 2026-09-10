
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Cliente(BaseModel):
    nome: str
    email:str
    senha:str
    telefone:str
    endereco:str
    cpf:str

class Produtos(BaseModel):
    categoria_id: int
    nome: str
    descricao: str
    preco: float
    disponivel: bool
    imagem_url: str
    quantidade_disponivel: int

class Categorias(BaseModel):
    nome: str

class Pedidos(BaseModel):
    cliente_id: int
    data_pedido: Optional[datetime] = None
    endereco_entrega: str
    forma_pagamento: str

class itenspedido(BaseModel):
    pedido_id: int
    produto_id: int
    quantidade: int
    preco_unitario: float

class admins(BaseModel):
    nome: str
    email:str
    senha:str