from fastapi import FastAPI
from database import Dbcontroller
from modelos import Cliente, Produtos, Categorias, Pedidos, itenspedido, admins
from datetime import datetime


db = Dbcontroller()
app = FastAPI()
tabelas = [
    "clientes",
    "produtos",
    "categorias",
    "pedidos"
]


@app.get("/")
def read_root():
    return db.ler_banco()


@app.post("/inserir_cliente")
def inserir_cliente(cliente:Cliente):
    dado = {
        "nome":cliente.nome,
        "email":cliente.email,
        "senha":cliente.senha,
        "telefone":cliente.telefone,
        "endereco":cliente.endereco,
        "cpf":cliente.cpf}
    response = db.inserir_tabela(tabelas[0],dado)
    return {"message":response}

@app.delete("/remover_cliente")
def remover_cliente(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[0],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/atualizar_cliente")
def atualizar_cliente(identificador_nome,identificador_,cliente:Cliente):
    dado = {
        "nome":cliente.nome,
        "email":cliente.email,
        "senha":cliente.senha,
        "telefone":cliente.telefone,
        "endereco":cliente.endereco,
        "cpf":cliente.cpf}
    response = db.atualizar_tabela(tabelas[0],dado,indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.post("/inserir_produto") #criar rota para inserir produto
def inserir_produto(produto:Produtos):
    dado = {
        "categoria_id":produto.categoria_id,
        "nome":produto.nome,
        "descricao":produto.descricao,
        "preco":produto.preco,
        "disponivel":produto.disponivel,
        "imagem_url":produto.imagem_url,
        "quantidade_disponivel":produto.quantidade_disponivel}
    response = db.inserir_tabela(tabelas[1],dado)
    return {"message":response}
@app.delete("/remover_produto") #criar rota para remover produto
def remover_produto(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[1],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_produto") #atualizar produto
def alterar_produto(id:int,coluna:str,dado):
    return{
        "message":db.atualizar_tabela(
            coluna=coluna,
            dado=dado,
            tabela=tabelas[1],
            id=id,
            id_nome="produto_id"
        )
        }


@app.post("/inserir_categoria") #criar rota para inserir categoria
def inserir_categoria(categoria:Categorias):
    dado = {
        "nome":categoria.nome}
    response = db.inserir_tabela(tabelas[2],dado)
    return {"message":response}
@app.delete("/remover_categoria") #criar rota para remover categoria
def remover_categoria(identificador_nome,identificador_):
    response = db.remover_de_tabela(tabelas[2],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_categoria") #atualizar categoria
def alterar_categoria(id:int,dado):
    return{
        "message":db.atualizar_tabela(
            coluna="nome",
            dado=dado,
            tabela=tabelas[2],
            id=id,
            id_nome="categoria_id"
        )
        }


@app.post("/inserir_pedido") #criar rota para inserir pedido
def inserir_pedido(pedido:Pedidos):
    dado = {
        "cliente_id":pedido.cliente_id,
        "data_pedido":pedido.data_pedido or datetime.now(),
        "endereco_entrega":pedido.endereco_entrega,
        "forma_pagamento":pedido.forma_pagamento}
    response = db.inserir_tabela(tabelas[3],dado)
    return {"message":response}
@app.delete("/remover_pedido") #criar rota para remover pedido
def remover_pedido(identificador_nome,identificador_):  
    response = db.remover_de_tabela(tabelas[3],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_pedido")
def alterar_pedido(id:int,coluna:str,dado):

    return{
            "message":db.atualizar_tabela(
                coluna=coluna,
                dado=dado,
                tabela=tabelas[3],
                id=id,
                id_nome="pedido_id"
            )
            }
@app.post("/inserir_item_pedido") #criar rota para inserir item pedido
def inserir_item_pedido(item:itenspedido):
    dado = {
        "pedido_id":item.pedido_id,
        "produto_id":item.produto_id,
        "quantidade":item.quantidade,
        "preco_unitario":item.preco_unitario}
    response = db.inserir_tabela("itenspedido",dado)
    return {"message":response}
@app.delete("/remover_item_pedido") #criar rota para remover item pedido
def remover_item_pedido(identificador_nome,identificador_):
    response = db.remover_de_tabela("itenspedido",indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}
@app.patch("/alterar_item_pedido")
def alterar_item_pedido(id:int,coluna:str,dado):
    return{
            "message":db.atualizar_tabela(
                coluna=coluna,
                dado=dado,
                tabela="itenspedido",
                id=id,
                id_nome="item_pedido_id"
            )
            }

@app.post("/inserir_admin") #criar rota para inserir admin
def inserir_admin(admin:admins):
    dado = {
        "nome":admin.nome,
        "email":admin.email,
        "senha":admin.senha}
    response = db.inserir_tabela("admins",dado)
    return {"message":response}
@app.delete("/remover_admin") #criar rota para remover admin
def remover_admin(identificador_nome,identificador_):
    response = db.remover_de_tabela("admins",indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}
@app.patch("/alterar_admin")
def alterar_admin(id:int,coluna:str,dado):
    return{
            "message":db.atualizar_tabela(
                coluna=coluna,
                dado=dado,
                tabela="admins",
                id=id,
                id_nome="admin_id"
            )
            }