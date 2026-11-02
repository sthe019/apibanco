from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from database import Dbcontroller
from modelos import *
from datetime import datetime

def get_db():return Dbcontroller()

app = FastAPI()
tabelas = [
    "clientes",
    "produtos",
    "categorias",
    "pedidos"
]


@app.get("/")
def read_root():
    db = get_db()
    return {"message":db.ler_banco()}

@app.get('/ler_tabela/{tabela}')
def read_tabela(tabela:str):
    db = get_db()
    if tabela == "produtos":
        temp = list(db.ler_tabela(tabela))
        data = []
        for c in temp:
            c = list(c)
            if len(c) > 7:
                c.pop(7)
                c.insert(7,f"http://127.0.0.1:8000/produtos/{c[0]}/imagens")
            data.append(c)

        return {"message":data}
    else:
        return {"message":db.ler_tabela(tabela)}

###################################################################
#                                                                 #
#                            Clientes                             #
#                                                                 #
###################################################################

@app.get("/procurar_cliente/{cliente_id}")
def procurar_cliente(cliente_id:int):
    db = get_db()
    dado = ["cliente_id",cliente_id]
    response = db.procurar_tabela(dado,tabelas[0])

    response = {
        "message":list(response)
    }
    return response

@app.post("/inserir_cliente")
def inserir_cliente(cliente:Cliente):
    db = get_db()
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
    db = get_db()
    response = db.remover_de_tabela(tabelas[0],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_cliente")
def alterar_cliente(id:int,coluna:str,dado):
    db = get_db()
    response = db.atualizar_tabela(tabela=tabelas[0],coluna=coluna,id=id,dado=dado,id_nome="cliente_id")
    return {"message":response}

###################################################################
#                                                                 #
#                            Produtos                             #
#                                                                 #
###################################################################

@app.get("/procurar_produto/{produto_id}")
def procurar_cliente(produto_id:int):
    db = get_db()
    dado = ["produto_id",produto_id]
    response = list(db.procurar_tabela(dado,tabelas[1]))
    response.pop(7)
    response.insert(8,f"http://127.0.0.1:8000/produtos/{produto_id}/imagens")
    return {
        "message":response
    }


@app.get('/produtos/{produto_id}/imagens')
async def pegar_imagem_produto(produto_id:int):
    db = get_db()
    produto = db.procurar_tabela(
        ["produto_id",produto_id],
        "produtos"
    )

    imagem = produto["imagem_byte"]
    tipo_imagem = produto["imagem_tipo"]

    return Response(
        content=imagem,
        media_type=tipo_imagem
    )

@app.post("/inserir_produto")
async def criar_produto(
    categoria_id:int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    disponivel: bool = Form(...),
    quantidade_disponivel: int = Form(...),
    imagem: UploadFile = File(...)
):
    imagem_bytes = await imagem.read()
    db = get_db()

    response = db.inserir_tabela('produtos',{
        "categoria_id": categoria_id,
        "disponivel":disponivel,
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "quantidade_disponivel": quantidade_disponivel,
        "imagem_byte": imagem_bytes,
        "imagem_nome":imagem.filename,
        "imagem_tipo": imagem.content_type
    })

    print(response)

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "quantidade_disponivel": quantidade_disponivel,
        "nome_imagem": imagem.filename,
        "tipo_imagem": imagem.content_type
    }

@app.delete("/remover_produto") #criar rota para remover produto
def remover_produto(id:int):
    db = get_db()
    response = db.remover_de_tabela(tabelas[1],indentificador_nome="produto_id",identificador=id)
    return {"message":response}

@app.patch("/alterar_produto")
def alterar_produto(id:int,coluna:str,dado):
    db = get_db()
    return{
        "message":db.atualizar_tabela(
            coluna=coluna,
            dado=dado,
            tabela=tabelas[1],
            id=id,
            id_nome="produto_id",
        )
        }

@app.patch("/alterar_imagem_produto/{id}")
async def alterar_imagem_produto(id: int, imagem: UploadFile = File(...)):
    db = get_db()
    imagem_bytes = await imagem.read()

    try:
        linhas = db.atualizar_imagem_produto(
            id, imagem_bytes, imagem.filename, imagem.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")

    if linhas == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return {"message": "Imagem atualizada com sucesso", "bytes": len(imagem_bytes)}

###################################################################
#                                                                 #
#                            Categorias                           #
#                                                                 #
###################################################################

@app.get("/procurar_categoria/{categoria_id}")
def procurar_cliente(categoria_id:int):
    db = get_db()
    dado = ["categoria_id",categoria_id]
    response = db.procurar_tabela(dado,tabelas[2])

    response = {
        "message":list(response)
    }
    return response



@app.post("/inserir_categoria") #criar rota para inserir categoria
def inserir_categoria(categoria:Categorias):
    db = get_db()
    dado = {
        "nome":categoria.nome}
    response = db.inserir_tabela(tabelas[2],dado)
    return {"message":response}

@app.delete("/remover_categoria") #criar rota para remover categoria
def remover_categoria(identificador_nome,identificador_):
    db = get_db()
    response = db.remover_de_tabela(tabelas[2],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_categoria")
def alterar_categoria(id:int,dado):
    db = get_db()
    return{
        "message":db.atualizar_tabela(
            coluna="nome",
            dado=dado,
            tabela=tabelas[2],
            id=id,
            id_nome="categoria_id"
        )
        }

###################################################################
#                                                                 #
#                            Pedidos                              #
#                                                                 #
###################################################################

@app.post("/inserir_pedido") #criar rota para inserir pedido
def inserir_pedido(pedido:Pedidos):
    db = get_db()
    dado = {
        "cliente_id":pedido.cliente_id,
        "data_pedido":pedido.data_pedido or datetime.now(),
        "status":pedido.status or "pendente",
        "valor_total":pedido.valortotal,
        "endereco_entrega":pedido.endereco_entrega,
        "forma_pagamento":pedido.forma_pagamento}
    response = db.inserir_tabela(tabelas[3],dado)
    return {"message":response}

@app.delete("/remover_pedido") #criar rota para remover pedido
def remover_pedido(identificador_nome,identificador_):  
    db = get_db()
    response = db.remover_de_tabela(tabelas[3],indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_pedido")
def alterar_pedido(id:int,coluna:str,dado):
    db = get_db()
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
    db = get_db()
    dado = {
        "pedido_id":item.pedido_id,
        "produto_id":item.produto_id,
        "quantidade":item.quantidade,
        "preco_unitario":item.preco_unitario}
    response = db.inserir_tabela("itenspedido",dado)
    return {"message":response}

@app.delete("/remover_item_pedido") #criar rota para remover item pedido
def remover_item_pedido(identificador_nome,identificador_):
    db = get_db()
    response = db.remover_de_tabela("itenspedido",indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_item_pedido")
def alterar_item_pedido(id:int,coluna:str,dado):
    db = get_db()
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
    db = get_db()
    dado = {
        "nome":admin.nome,
        "email":admin.email,
        "senha":admin.senha}
    response = db.inserir_tabela("admins",dado)
    return {"message":response}
@app.delete("/remover_admin") #criar rota para remover admin
def remover_admin(identificador_nome,identificador_):
    db = get_db()
    response = db.remover_de_tabela("admins",indentificador_nome=identificador_nome,identificador=identificador_)
    return {"message":response}

@app.patch("/alterar_admin")
def alterar_admin(id:int,coluna:str,dado):
    db = get_db()
    return{
            "message":db.atualizar_tabela(
                coluna=coluna,
                dado=dado,
                tabela="admins",
                id=id,
                id_nome="admin_id"
            )
            }
