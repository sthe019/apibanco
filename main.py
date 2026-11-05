from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from database import Dbcontroller
from modelos import *
from datetime import datetime

def get_db():
    return Dbcontroller()

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
    return {"message": db.ler_banco()}


@app.get('/ler_tabela/{tabela}')
def read_tabela(tabela: str):
    db = get_db()
    resultado = db.ler_tabela(tabela)
    
    # Se ocorrer erro no banco, retorna a mensagem de erro
    if isinstance(resultado, str):
        return {"message": resultado}

    data = []
    for row in resultado:
        c = list(row)
        # Tratamento específico para produtos para evitar serialização de bytes em JSON
        if tabela == "produtos":
            # Procura e remove colunas de bytes (tipo bytes) se existirem na linha
            for i, val in enumerate(c):
                if isinstance(val, bytes):
                    c[i] = None  # Remove o binário bruto do JSON
            
            # Ajusta ou adiciona o link da imagem se houver ID na primeira coluna
            if len(c) > 0:
                produto_id = c[0]
                c.append(f"http://127.0.0.1:8000/produtos/{produto_id}/imagens")
                
        data.append(c)

    return {"message": data}


###################################################################
#                                                                 #
#                            Clientes                             #
#                                                                 #
###################################################################

@app.get("/procurar_cliente/{cliente_id}")
def procurar_cliente(cliente_id: int):
    db = get_db()
    dado = ["cliente_id", cliente_id]
    response = db.procurar_tabela(dado, tabelas[0])
    if isinstance(response, str):
        raise HTTPException(status_code=404, detail=response)
    return {"message": list(response)}


@app.post("/inserir_cliente")
def inserir_cliente(cliente: Cliente):
    db = get_db()
    dado = {
        "nome": cliente.nome,
        "email": cliente.email,
        "senha": cliente.senha,
        "telefone": cliente.telefone,
        "endereco": cliente.endereco,
        "cpf": cliente.cpf
    }
    response = db.inserir_tabela(tabelas[0], dado)
    return {"message": response}


@app.delete("/remover_cliente")
def remover_cliente(identificador_nome: str, identificador_: str):
    db = get_db()
    response = db.remover_de_tabela(tabelas[0], indentificador_nome=identificador_nome, identificador=identificador_)
    return {"message": response}


@app.patch("/alterar_cliente")
def alterar_cliente(id: int, coluna: str, dado: str):
    db = get_db()
    response = db.atualizar_tabela(tabela=tabelas[0], coluna=coluna, dado=dado, id=id, id_nome="cliente_id")
    return {"message": response}


###################################################################
#                                                                 #
#                            Produtos                             #
#                                                                 #
###################################################################

@app.get("/procurar_produto/{produto_id}")
def procurar_produto(produto_id: int):  # Função renomeada para evitar conflito
    db = get_db()
    dado = ["produto_id", produto_id]
    response = db.procurar_tabela(dado, tabelas[1])
    if isinstance(response, str):
        raise HTTPException(status_code=404, detail=response)
    
    response_list = list(response)
    # Remove bytes da resposta JSON se estiver presente
    for i, val in enumerate(response_list):
        if isinstance(val, bytes):
            response_list[i] = None

    response_list.append(f"http://127.0.0.1:8000/produtos/{produto_id}/imagens")
    return {"message": response_list}


@app.get('/produtos/{produto_id}/imagens')
async def pegar_imagem_produto(produto_id: int):
    db = get_db()
    # O método procurar_tabela retorna a tupla/linha do banco de dados
    produto = db.procurar_tabela(["produto_id", produto_id], "produtos")
    
    if isinstance(produto, str) or not produto:
        raise HTTPException(status_code=404, detail="Produto ou imagem não encontrado")

    # Mapeamento exato das colunas da tabela produtos com base no seu script SQL:
    # 0: produto_id, 1: categoria_id, 2: nome, 3: descricao, 4: preco, 
    # 5: disponivel, 6: quantidade_disponivel, 7: imagem_byte, 8: imagem_nome, 9: imagem_tipo
    try:
        imagem = produto[7]       # Coluna imagem_byte
        tipo_imagem = produto[9]  # Coluna imagem_tipo
    except (IndexError, TypeError):
        raise HTTPException(status_code=500, detail="Erro ao extrair dados binários da imagem do banco")

    if not imagem:
        raise HTTPException(status_code=404, detail="Imagem não cadastrada para este produto")

    return Response(content=imagem, media_type=tipo_imagem or "image/jpeg")

@app.post("/inserir_produto")
async def criar_produto(
    categoria_id: int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
    preco: float = Form(...),
    disponivel: bool = Form(...),
    quantidade_disponivel: int = Form(...),
    imagem: UploadFile = File(...)
):
    imagem_bytes = await imagem.read()
    db = get_db()

    response = db.inserir_tabela('produtos', {
        "categoria_id": categoria_id,
        "disponivel": disponivel,
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "quantidade_disponivel": quantidade_disponivel,
        "imagem_byte": imagem_bytes,
        "imagem_nome": imagem.filename,
        "imagem_tipo": imagem.content_type
    })

    return {
        "message": response,
        "nome": nome,
        "preco": preco,
        "quantidade_disponivel": quantidade_disponivel,
        "nome_imagem": imagem.filename
    }


@app.delete("/remover_produto")
def remover_produto(id: int):
    db = get_db()
    response = db.remover_de_tabela(tabelas[1], indentificador_nome="produto_id", identificador=id)
    return {"message": response}


@app.patch("/alterar_produto")
def alterar_produto(id: int, coluna: str, dado: str):
    db = get_db()
    return {
        "message": db.atualizar_tabela(
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
#                           Categorias                            #
#                                                                 #
###################################################################

@app.get("/procurar_categoria/{categoria_id}")
def procurar_categoria(categoria_id: int):  # Renomeado para evitar conflito
    db = get_db()
    dado = ["categoria_id", categoria_id]
    response = db.procurar_tabela(dado, tabelas[2])
    if isinstance(response, str):
        raise HTTPException(status_code=404, detail=response)
    return {"message": list(response)}


@app.post("/inserir_categoria")
def inserir_categoria(categoria: Categorias):
    db = get_db()
    dado = {"nome": categoria.nome}
    response = db.inserir_tabela(tabelas[2], dado)
    return {"message": response}


@app.delete("/remover_categoria")
def remover_categoria(identificador_nome: str, identificador_: str):
    db = get_db()
    response = db.remover_de_tabela(tabelas[2], indentificador_nome=identificador_nome, identificador=identificador_)
    return {"message": response}


@app.patch("/alterar_categoria")
def alterar_categoria(id: int, dado: str):
    db = get_db()
    return {
        "message": db.atualizar_tabela(
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

@app.post("/inserir_pedido")
def inserir_pedido(pedido: Pedidos):
    db = get_db()
    dado = {
        "cliente_id": pedido.cliente_id,
        "data_pedido": pedido.data_pedido or datetime.now(),
        "status": pedido.status or "pendente",
        "valor_total": pedido.valortotal,
        "endereco_entrega": pedido.endereco_entrega,
        "forma_pagamento": pedido.forma_pagamento
    }
    response = db.inserir_tabela(tabelas[3], dado)
    return {"message": response}


@app.delete("/remover_pedido")
def remover_pedido(identificador_nome: str, identificador_: str):  
    db = get_db()
    response = db.remover_de_tabela(tabelas[3], indentificador_nome=identificador_nome, identificador=identificador_)
    return {"message": response}


@app.patch("/alterar_pedido")
def alterar_pedido(id: int, coluna: str, dado: str):
    db = get_db()
    return {
        "message": db.atualizar_tabela(
            coluna=coluna,
            dado=dado,
            tabela=tabelas[3],
            id=id,
            id_nome="pedido_id"
        )
    }


@app.post("/inserir_item_pedido")
def inserir_item_pedido(item: itenspedido):
    db = get_db()
    dado = {
        "pedido_id": item.pedido_id,
        "produto_id": item.produto_id,
        "quantidade": item.quantidade,
        "preco_unitario": item.preco_unitario
    }
    response = db.inserir_tabela("itenspedido", dado)
    return {"message": response}


@app.delete("/remover_item_pedido")
def remover_item_pedido(identificador_nome: str, identificador_: str):
    db = get_db()
    response = db.remover_de_tabela("itenspedido", indentificador_nome=identificador_nome, identificador=identificador_)
    return {"message": response}


@app.patch("/alterar_item_pedido")
def alterar_item_pedido(id: int, coluna: str, dado: str):
    db = get_db()
    return {
        "message": db.atualizar_tabela(
            coluna=coluna,
            dado=dado,
            tabela="itenspedido",
            id=id,
            id_nome="item_id"  # Corrigido de item_pedido_id para item_id conforme a modelagem SQL
        )
    }


@app.post("/inserir_admin")
def inserir_admin(admin: admins):
    db = get_db()
    dado = {
        "nome": admin.nome,
        "email": admin.email,
        "senha": admin.senha
    }
    response = db.inserir_tabela("admins", dado)
    return {"message": response}


@app.delete("/remover_admin")
def remover_admin(identificador_nome: str, identificador_: str):
    db = get_db()
    response = db.remover_de_tabela("admins", indentificador_nome=identificador_nome, identificador=identificador_)
    return {"message": response}


@app.patch("/alterar_admin")
def alterar_admin(id: int, coluna: str, dado: str):
    db = get_db()
    return {
        "message": db.atualizar_tabela(
            coluna=coluna,
            dado=dado,
            tabela="admins",
            id=id,
            id_nome="admin_id"
        )
    }
