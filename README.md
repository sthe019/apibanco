# 🛒 API Banco — Loja com API REST, SQL Server e Interface Desktop

Projeto de uma **loja virtual** composta por três partes integradas:

1. Uma **API REST** em **Python (FastAPI)**;
2. Um banco de dados **Microsoft SQL Server** (banco `site`), com criação e carga de dados automatizadas por script **PowerShell**;
3. Uma **interface desktop para Windows** (`INTERFACE/loja_app.exe`, aplicativo **Flutter**) que consome a API.

> Projeto acadêmico — UNIP, 4º semestre (PIM).
> Acompanhamento: [Kanban no Trello](https://trello.com/invite/b/6aa0a5736922504031281750/ATTId61a1befb7ce7742c3822a4ee859d15978FFF31F/unip-4-semestre)
> Repositório: [rafasdsm/apibanco](https://github.com/rafasdsm/apibanco) · Release: [`release`](https://github.com/rafasdsm/apibanco/releases/tag/release)

---

## 📑 Sumário

1. [Descrição e objetivos](#-descrição-e-objetivos)
2. [Tecnologias](#-tecnologias)
3. [Pré-requisitos](#-pré-requisitos)
4. [Instalação e execução passo a passo](#-instalação-e-execução-passo-a-passo)
5. [Script PowerShell de inicialização do banco (`iniciar.ps1`)](#-script-powershell-de-inicialização-do-banco-iniciarps1)
6. [Exemplos práticos de chamadas e testes da API](#-exemplos-práticos-de-chamadas-e-testes-da-api)
7. [Estrutura das pastas (`api` e `frontend`)](#-estrutura-das-pastas-api-e-frontend)
8. [Solução de problemas](#-solução-de-problemas)
9. [Observações de segurança](#-observações-de-segurança)

---

## 🎯 Descrição e objetivos

O **API Banco** implementa o back-end de uma loja (com produtos de **materiais**, **padaria** e **bebidas**), expondo operações de cadastro, consulta, alteração e remoção por meio de uma API REST. Os dados ficam em um banco SQL Server e podem ser consumidos pela interface desktop incluída no projeto ou por qualquer cliente HTTP (navegador, curl, Postman, PowerShell).

### Objetivos

- Disponibilizar uma **API REST** com documentação interativa automática (Swagger/OpenAPI) para **clientes, categorias, produtos, pedidos, itens de pedido e administradores**.
- **Armazenar as imagens dos produtos diretamente no banco** (`varbinary(max)`), entregando-as por uma rota HTTP dedicada.
- **Relacionar as tabelas entre si** por chaves estrangeiras (ex.: ao fazer um pedido, saber *quem* comprou e *quais itens*).
- **Automatizar o ambiente**: criar o ambiente virtual Python, instalar dependências, criar o banco, gerar dados de exemplo (com a biblioteca *Faker*) e iniciar a aplicação com um único script.
- Fornecer uma **interface gráfica** (frontend) pronta para uso, ligada à API.

### Modelo de dados

| Tabela        | Principais colunas                                                                                              |
|---------------|-----------------------------------------------------------------------------------------------------------------|
| `clientes`    | `cliente_id`, `nome`, `email` (único), `senha`, `telefone`, `endereco`, `cpf` (único)                           |
| `categorias`  | `categoria_id`, `nome`                                                                                          |
| `produtos`    | `produto_id`, `categoria_id` (FK), `nome`, `descricao`, `preco`, `disponivel`, `quantidade_disponivel`, `imagem_byte`, `imagem_nome`, `imagem_tipo` |
| `pedidos`     | `pedido_id`, `cliente_id` (FK), `data_pedido`, `status`, `valor_total`, `endereco_entrega`, `forma_pagamento`, `status_pagamento` |
| `itenspedido` | `item_id`, `pedido_id` (FK), `produto_id` (FK), `quantidade`, `preco_unitario`                                  |
| `admins`      | `admin_id`, `nome`, `email`, `senha`                                                                            |

---

## 🧰 Tecnologias

| Camada          | Tecnologia                                                            |
|-----------------|-----------------------------------------------------------------------|
| API             | Python 3, **FastAPI**, **Uvicorn**, **Pydantic**, `python-multipart`  |
| Acesso a dados  | **mssql-python** (conexão com SQL Server via Windows Authentication)  |
| Banco de dados  | **Microsoft SQL Server** (instância `SQLEXPRESS`)                     |
| Dados de teste  | **Faker** (`pt-BR`)                                                   |
| Automação       | **PowerShell** (`iniciar.ps1`) e Batch (`run.bat`)                    |
| Interface       | **Flutter** (aplicativo Windows — `INTERFACE/loja_app.exe`)           |

---

## ✅ Pré-requisitos

- **Windows 10/11** (a interface é um executável Windows e a conexão com o banco usa autenticação do Windows).
- **Python 3.10+**, com o comando **`python3`** disponível no `PATH` (os scripts do projeto usam `python3`).
- **Microsoft SQL Server** (Express é suficiente), com a instância `SQLEXPRESS` e a autenticação do Windows habilitada.
- **`sqlcmd`** (SQL Server Command Line Utilities) disponível no `PATH`.
- **PowerShell 5.1+** (já incluso no Windows) ou PowerShell 7+.
- *(Opcional)* SQL Server Management Studio (SSMS) para inspecionar o banco.

> 💡 No Windows, se `python3` não for reconhecido, instale o Python pela [página oficial](https://www.python.org/downloads/) marcando **Add Python to PATH**, ou crie um alias/cópia `python3.exe` apontando para o seu `python.exe`.

---

## 🚀 Instalação e execução passo a passo

### Caminho rápido (recomendado)

1. **Baixe e extraia** o projeto:
   - pela [release](https://github.com/rafasdsm/apibanco/releases/tag/release) (arquivo `.zip` em *Assets*), ou
   - com Git: `git clone https://github.com/rafasdsm/apibanco.git`
2. **Confira o arquivo `banco.txt`** (veja a [configuração](#2-configure-a-conexão-com-o-banco-bancotxt)).
3. Abra o **PowerShell na pasta do projeto** e execute:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\iniciar.ps1
   ```

O script cuida de todo o restante: cria o ambiente virtual, instala as dependências, cria o banco (se necessário), gera os dados de exemplo, abre a interface e inicia a API. Detalhes na [seção do script](#-script-powershell-de-inicialização-do-banco-iniciarps1).

### Passo a passo manual

#### 1. Crie e ative o ambiente virtual

```powershell
cd C:\caminho\para\apibanco
python3 -m venv venv
.\venv\Scripts\Activate.ps1
```

> Se o PowerShell bloquear a ativação: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

#### 2. Configure a conexão com o banco (`banco.txt`)

O arquivo `banco.txt` usa o formato `chave=valor`, uma chave por linha:

```text
server=localhost\SQLEXPRESS
database=site
```

| Chave      | Descrição                                                        |
|------------|------------------------------------------------------------------|
| `server`   | Servidor/instância do SQL Server (ex.: `localhost\SQLEXPRESS`)   |
| `database` | Nome do banco (o projeto usa o banco **`site`**)                 |

> A conexão utiliza **Windows Authentication** (`Trusted_Connection=yes`); não há usuário nem senha neste arquivo.

#### 3. Instale as dependências

```powershell
python3 -m pip install -r requisitos.txt
```

#### 4. Crie o banco e popule os dados

Use o [script PowerShell](#-script-powershell-de-inicialização-do-banco-iniciarps1) **ou** faça manualmente:

```powershell
sqlcmd -S ".\SQLEXPRESS" -E -C -b -d master -i site.sql
python3 generate_data.py
```

#### 5. Inicie a API

```powershell
python3 run.py
```

A API sobe em **http://127.0.0.1:8000** (com *reload* automático).

| Recurso                   | URL                              |
|---------------------------|----------------------------------|
| API (raiz)                | http://127.0.0.1:8000/           |
| Swagger UI (interativo)   | http://127.0.0.1:8000/docs       |
| ReDoc                     | http://127.0.0.1:8000/redoc      |

#### 6. Abra a interface

Com a API em execução, execute `INTERFACE\loja_app.exe` (duplo clique ou pelo PowerShell):

```powershell
Start-Process .\INTERFACE\loja_app.exe
```

> Mantenha a API ligada enquanto utiliza a interface.

---

## 🗄️ Script PowerShell de inicialização do banco (`iniciar.ps1`)

O `iniciar.ps1` é a versão PowerShell do `run.bat`. Ele executa, em ordem:

| # | Etapa | O que faz |
|---|-------|-----------|
| 1 | Verifica o Python | Confirma que `python3` está no `PATH` |
| 2 | Ambiente virtual | Cria a pasta `venv` se ela não existir |
| 3 | Ativação | Ativa o `venv` (`Activate.ps1`) |
| 4 | Dependências | Executa `pip install -r requisitos.txt` |
| 5 | Configuração | Lê `server` e `database` do `banco.txt` (se o servidor for `localhost`, usa `.\SQLEXPRESS`) |
| 6 | Verifica o banco | Conecta ao `master` com `sqlcmd` e checa se o banco `site` já existe |
| 7 | Cria e popula | **Somente se o banco não existir:** executa `site.sql` e `generate_data.py` |
| 8 | Inicia | Abre `INTERFACE\loja_app.exe` (se existir) e executa `run.py` |

### Como executar

1. Abra o **PowerShell** na pasta do projeto (onde estão `iniciar.ps1`, `banco.txt` e `site.sql`):

   ```powershell
   cd C:\caminho\para\apibanco
   ```

2. Execute o script liberando a política de execução apenas para esta chamada:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\iniciar.ps1
   ```

   *Alternativa:*

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\iniciar.ps1
   ```

3. Acompanhe as mensagens `[INFO]`. Em caso de falha, o script mostra `[ERRO]` e aguarda **Enter** antes de fechar.

> ⚠️ **O banco só é criado e populado na primeira execução.** Se o banco `site` já existir, as etapas 6 e 7 são puladas e os dados existentes são mantidos.

### Recriar o banco do zero

O `generate_data.py` **limpa as tabelas** antes de inserir novos dados. Para recriar tudo, apague o banco `site` (no SSMS ou com o comando abaixo) e execute o script novamente:

```powershell
sqlcmd -S ".\SQLEXPRESS" -E -C -Q "DROP DATABASE [site]"
powershell -ExecutionPolicy Bypass -File .\iniciar.ps1
```

### Dados gerados automaticamente

- **Categorias:** `materiais`, `padaria` e `bebidas`;
- **Produtos:** criados a partir das imagens da pasta `assets/` (armazenadas no banco);
- **Clientes e administradores fictícios** (Faker `pt-BR`) e um administrador padrão para testes;
- **Pedidos** (300 por padrão) com seus respectivos itens, relacionando clientes e produtos.

### Alternativa em Batch

O arquivo `run.bat` faz exatamente o mesmo fluxo para quem preferir o Prompt de Comando: basta executá-lo com duplo clique.

---

## 🧪 Exemplos práticos de chamadas e testes da API

Os exemplos assumem a API em `http://127.0.0.1:8000`. Você pode testar pelo **Swagger (`/docs`)**, por **curl** ou pelo **PowerShell**.

### Resumo das rotas

| Método   | Rota                                 | Descrição                                      |
|----------|--------------------------------------|------------------------------------------------|
| `GET`    | `/`                                  | Lista as tabelas do banco                      |
| `GET`    | `/ler_tabela/{tabela}`               | Lista todos os registros de uma tabela         |
| `GET`    | `/procurar_cliente/{cliente_id}`     | Busca cliente por ID                           |
| `POST`   | `/inserir_cliente`                   | Cadastra cliente (JSON)                        |
| `PATCH`  | `/alterar_cliente`                   | Altera uma coluna do cliente                   |
| `DELETE` | `/remover_cliente`                   | Remove cliente                                 |
| `GET`    | `/procurar_produto/{produto_id}`     | Busca produto por ID                           |
| `GET`    | `/produtos/{produto_id}/imagens`     | Retorna a imagem do produto                    |
| `POST`   | `/inserir_produto`                   | Cadastra produto com imagem (`multipart/form-data`) |
| `PATCH`  | `/alterar_produto`                   | Altera uma coluna do produto                   |
| `DELETE` | `/remover_produto`                   | Remove produto                                 |
| `GET`    | `/procurar_categoria/{categoria_id}` | Busca categoria por ID                         |
| `POST`   | `/inserir_categoria`                 | Cadastra categoria (JSON)                      |
| `PATCH`  | `/alterar_categoria`                 | Altera o nome da categoria                     |
| `DELETE` | `/remover_categoria`                 | Remove categoria                               |
| `POST`   | `/inserir_pedido`                    | Cadastra pedido (JSON)                         |
| `PATCH`  | `/alterar_pedido`                    | Altera uma coluna do pedido                    |
| `DELETE` | `/remover_pedido`                    | Remove pedido                                  |
| `POST`   | `/inserir_item_pedido`               | Adiciona item a um pedido (JSON)               |
| `PATCH`  | `/alterar_item_pedido`               | Altera uma coluna do item                      |
| `DELETE` | `/remover_item_pedido`               | Remove item de pedido                          |
| `POST`   | `/inserir_admin`                     | Cadastra administrador (JSON)                  |
| `PATCH`  | `/alterar_admin`                     | Altera uma coluna do administrador             |
| `DELETE` | `/remover_admin`                     | Remove administrador                           |

> No PowerShell, use `curl.exe` (e não apenas `curl`, que é um alias de `Invoke-WebRequest`).

### 1. Testar se a API está no ar

```powershell
curl.exe http://127.0.0.1:8000/
```

Resposta esperada (nomes das tabelas do banco):

```json
{ "message": [["admins"], ["categorias"], ["clientes"], ["itenspedido"], ["pedidos"], ["produtos"]] }
```

### 2. Listar registros

```powershell
curl.exe http://127.0.0.1:8000/ler_tabela/clientes
curl.exe http://127.0.0.1:8000/ler_tabela/produtos
```

> Em `produtos`, o campo binário da imagem é substituído pela URL `http://127.0.0.1:8000/produtos/{id}/imagens`.

### 3. Clientes

**Cadastrar** (`POST` com JSON):

```powershell
curl.exe -X POST http://127.0.0.1:8000/inserir_cliente `
  -H "Content-Type: application/json" `
  -d '{\"nome\":\"Maria Silva\",\"email\":\"maria@email.com\",\"senha\":\"123456\",\"telefone\":\"11999990000\",\"endereco\":\"Rua das Flores, 100\",\"cpf\":\"12345678900\"}'
```

**Buscar por ID:**

```powershell
curl.exe http://127.0.0.1:8000/procurar_cliente/1
```

**Alterar uma coluna** (parâmetros na *query string*):

```powershell
curl.exe -X PATCH "http://127.0.0.1:8000/alterar_cliente?id=1&coluna=telefone&dado=11988887777"
```

**Remover** (informa a coluna identificadora e o valor):

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/remover_cliente?identificador_nome=cliente_id&identificador_=1"
```

### 4. Categorias

```powershell
curl.exe -X POST http://127.0.0.1:8000/inserir_categoria -H "Content-Type: application/json" -d '{\"nome\":\"Doces\"}'
curl.exe http://127.0.0.1:8000/procurar_categoria/1
curl.exe -X PATCH "http://127.0.0.1:8000/alterar_categoria?id=1&dado=Materiais"
```

### 5. Produtos (com upload de imagem)

O cadastro usa **`multipart/form-data`**, pois envia a imagem junto com os dados:

```powershell
curl.exe -X POST http://127.0.0.1:8000/inserir_produto `
  -F "categoria_id=2" `
  -F "nome=Pão de queijo" `
  -F "descricao=Pão de queijo fresco" `
  -F "preco=7.50" `
  -F "disponivel=true" `
  -F "quantidade_disponivel=30" `
  -F "imagem=@.\assets\padaria\brownie.png"
```

**Buscar o produto e baixar/visualizar a imagem:**

```powershell
curl.exe http://127.0.0.1:8000/procurar_produto/1
curl.exe http://127.0.0.1:8000/produtos/1/imagens --output produto1.png
```

Ou abra no navegador: `http://127.0.0.1:8000/produtos/1/imagens`.

**Alterar e remover:**

```powershell
curl.exe -X PATCH "http://127.0.0.1:8000/alterar_produto?id=1&coluna=preco&dado=9.90"
curl.exe -X DELETE "http://127.0.0.1:8000/remover_produto?id=1"
```

### 6. Pedidos e itens do pedido

```powershell
curl.exe -X POST http://127.0.0.1:8000/inserir_pedido `
  -H "Content-Type: application/json" `
  -d '{\"cliente_id\":1,\"endereco_entrega\":\"Rua das Flores, 100\",\"status\":\"pendente\",\"valortotal\":15.00,\"forma_pagamento\":\"pix\"}'

curl.exe -X POST http://127.0.0.1:8000/inserir_item_pedido `
  -H "Content-Type: application/json" `
  -d '{\"pedido_id\":1,\"produto_id\":1,\"quantidade\":2,\"preco_unitario\":7.50}'
```

> O campo `data_pedido` é opcional: se omitido, a API usa a data/hora atual.
> Os IDs de `cliente_id`, `pedido_id` e `produto_id` precisam existir (há chaves estrangeiras no banco).

### 7. Administradores

```powershell
curl.exe -X POST http://127.0.0.1:8000/inserir_admin `
  -H "Content-Type: application/json" `
  -d '{\"nome\":\"Admin\",\"email\":\"admin@email.com\",\"senha\":\"admin123\"}'
```

### 8. Exemplos nativos em PowerShell

```powershell
# GET
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ler_tabela/clientes" -Method Get

# POST (JSON)
$body = @{ nome = "Doces" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/inserir_categoria" `
  -Method Post -ContentType "application/json" -Body $body

# PATCH
Invoke-RestMethod -Uri "http://127.0.0.1:8000/alterar_cliente?id=1&coluna=telefone&dado=11988887777" -Method Patch
```

### 9. Scripts de teste do projeto

```powershell
python3 test.py    # insere clientes fictícios (Faker) usando a camada de banco
python3 generate_data.py   # recria os dados de exemplo (limpa as tabelas antes!)
```

> ⚠️ `generate_data.py` executa `DELETE` em todas as tabelas antes de popular. Não rode em um banco com dados que você queira manter.

---

## 📂 Estrutura das pastas (`api` e `frontend`)

O projeto não possui pastas literalmente chamadas `api/` e `frontend/`: a **API** fica na **raiz** do projeto e o **frontend** fica na pasta **`INTERFACE/`**. O mapeamento é este:

```text
apibanco/
│
├── ── API (back-end, na raiz do projeto) ──────────────────────────────
├── main.py                    # Rotas (endpoints) da API FastAPI
├── modelos.py                 # Modelos Pydantic: Cliente, Produtos, Categorias, Pedidos, itenspedido, admins
├── database.py                # Classe Dbcontroller: conexão e CRUD no SQL Server
├── run.py                     # Sobe a API com Uvicorn em 127.0.0.1:8000
├── banco.txt                  # Configuração do banco (server e database)
├── requisitos.txt             # Dependências Python (pip)
├── site.sql                   # Script SQL: cria o banco "site", tabelas e chaves estrangeiras
├── generate_data.py           # Gera dados fictícios (clientes, produtos, admins, pedidos e itens)
├── regenarete_database.py     # Rotina auxiliar para recriar o banco e os dados
├── test.py                    # Script de teste (insere clientes fictícios)
├── iniciar.ps1                # Script PowerShell de inicialização do ambiente e do banco
├── run.bat                    # Equivalente em Batch do iniciar.ps1
├── code.txt                   # Anotações/trechos de script auxiliares
├── aula sexta possivel pim.txt# Anotações de planejamento do PIM
│
├── assets/                    # Imagens usadas para popular os produtos do banco
│   ├── material/              #   café, açúcar, farinha de trigo, fermento em pó, leite
│   ├── padaria/               #   baguete, baguete de alho, brownie, pão de fermentação natural
│   └── bebidas/               #   suco de laranja, chá mate, capuccino
│
├── INTERFACE/                 # ── FRONTEND (aplicativo desktop Flutter para Windows) ──
│   ├── loja_app.exe           #   Executável da interface da loja
│   ├── flutter_windows.dll    #   Runtime do Flutter
│   ├── dartjni.dll            #   Biblioteca nativa de apoio (Dart/JNI)
│   ├── file_selector_windows_plugin.dll  # Plugin para seleção de arquivos
│   └── data/                  #   Recursos do app (app.so, icudtl.dat, flutter_assets/)
│
└── README.md                  # Este arquivo
```

### Resumo

| Camada | Local | Função |
|--------|-------|--------|
| **API** | Raiz do projeto (`main.py`, `modelos.py`, `database.py`, `run.py`) | Expõe as rotas REST, valida os dados e acessa o SQL Server |
| **Banco de dados** | `site.sql`, `banco.txt`, `generate_data.py` | Esquema, configuração de conexão e carga inicial |
| **Automação** | `iniciar.ps1`, `run.bat` | Preparam ambiente, banco e iniciam a aplicação |
| **Recursos** | `assets/` | Imagens dos produtos gravadas no banco pelo `generate_data.py` |
| **Frontend** | `INTERFACE/` | Aplicativo desktop (`loja_app.exe`) que consome a API |

---

## 🛠️ Solução de problemas

| Problema | Causa provável / solução |
|----------|--------------------------|
| `Python3 nao encontrado no PATH` | Instale o Python e garanta o comando `python3` no `PATH` (ou crie um alias para `python.exe`). |
| `sqlcmd nao encontrado no PATH` | Instale o *SQL Server Command Line Utilities* e reabra o terminal. |
| `Nao foi possivel conectar ao SQL Server` | Confirme que o serviço do SQL Server está ativo, que o `server` do `banco.txt` está correto (`localhost\SQLEXPRESS`) e que seu usuário Windows tem acesso. |
| `running scripts is disabled on this system` | Use `powershell -ExecutionPolicy Bypass -File .\iniciar.ps1`. |
| `Form data requires "python-multipart"` | Rode `python3 -m pip install -r requisitos.txt` com o `venv` ativo. |
| Interface não carrega dados | Verifique se a API está em execução em `127.0.0.1:8000`. |
| Imagem do produto não aparece | As URLs de imagem apontam para `http://127.0.0.1:8000/produtos/{id}/imagens`; mantenha a API nesse endereço. |
| Porta 8000 ocupada | Encerre o processo que a utiliza ou altere a porta em `run.py`. |

---

## 🔒 Observações de segurança

Este é um projeto **educacional**. Antes de qualquer uso real, considere:

- **Senhas em texto puro** nas tabelas `clientes` e `admins` — use hash (ex.: `bcrypt`).
- **SQL montado por concatenação** em parte das rotas de busca e atualização — migre para consultas parametrizadas (prevenção de *SQL Injection*).
- **Sem autenticação/autorização** nas rotas da API (ex.: JWT).
- O `generate_data.py` cria um **administrador padrão para testes**; altere ou remova essas credenciais fora do ambiente de desenvolvimento.
- Nomes de colunas e tabelas são recebidos via parâmetros nas rotas genéricas (`/ler_tabela`, `PATCH`, `DELETE`); restrinja-os a uma lista permitida.

---

## 📜 Créditos

Projeto acadêmico (UNIP — 4º semestre). Repositório: [rafasdsm/apibanco](https://github.com/rafasdsm/apibanco), fork de [sthe019/apibanco](https://github.com/sthe019/apibanco).
