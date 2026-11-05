from datetime import datetime, timedelta
from random import choice, randint
from faker import Faker
from os import listdir
from database import Dbcontroller

class GenerateFakeData:
    def __init__(self):
        self.db = Dbcontroller()
        self.faker = Faker(locale="pt-br")
        
        self.db.limpar_tabela("produtos")
        self.db.limpar_tabela("clientes")
        self.db.limpar_tabela("categorias")
        self.db.limpar_tabela("admins")
        self.db.limpar_tabela('itenspedido')
        self.db.limpar_tabela('pedidos')
        
    def generate_clientes(self):
        print("-"*100)
        print("Gerando clientes!")
        print("-"*100)
        def generate_withoutclones(type:int):
            lista = []
            while True:
                match type:
                    case 0:
                        data = self.faker.name()
                    case 1:
                        data = self.faker.email()
                    case 2:
                        data = self.faker.password(length=10)
                    case 3:
                        phone = ""
                        for c in range(11):
                            phone += str(randint(0,9))
                        data = phone
                    case 4:
                        data = self.faker.address().replace("\n",' ')
                    case 5:
                        cpf = ""
                        for c in range(11):
                            cpf += str(randint(0,9))
                        data = cpf
                if data not in lista: lista.append(data)
                if len(lista) == 250: break
            return lista
        
        names = generate_withoutclones(0)
        email = generate_withoutclones(1)
        passworld = generate_withoutclones(2)
        phone = generate_withoutclones(3)
        address = generate_withoutclones(4)
        cpf = generate_withoutclones(5)

        clientes = []

        for c in range(len(names)):
            cliente = {}
            cliente["nome"] = names[c]
            cliente["email"] = email[c]
            cliente["senha"] = passworld[c]
            cliente["telefone"] = phone[c]
            cliente["endereco"] = address[c]
            cliente["cpf"] = cpf[c]
            clientes.append(cliente)
        
        for c in clientes:
            self.db.inserir_tabela("clientes", c)
            print(f"Cliente adicionado ao banco: {c['nome']}")

    def generate_categorias(self):
        print("!"*100)
        print("Gerando categorias!")
        print("!"*100)
        self.db.inserir_tabela("categorias", {"nome":"materiais"})
        self.db.inserir_tabela("categorias", {"nome":"padaria"})
        self.db.inserir_tabela("categorias", {"nome":"bebidas"})

    def generate_produtos(self):
        print("¨"*100)
        print("Gerando produtos!")
        print("¨"*100)

        descricao = "Lorem Ipsum is simply dummy text of the printing"

        categorias = self.db.ler_tabela("categorias")
    
        categoria_materiais = categorias[0][0]
        categoria_padaria = categorias[1][0]
        categoria_bebidas = categorias[2][0]

        # #############################################################################
        #                                  materiais                                  #
        # #############################################################################

        material_folder = "assets/material"
        material_filelist = listdir(material_folder)
        for c in material_filelist:
            material_object = {
                "categoria_id": categoria_materiais,
                "nome": c.split('.')[0].title(),
                "descricao": descricao,
                "preco": float(f"{randint(1,60)}.{randint(0,9)}"),
                "disponivel": True,
                "quantidade_disponivel": randint(1,20),
                "imagem_byte": open(material_folder + '/' + c, 'rb').read(),
                "imagem_nome": c,
                "imagem_tipo": f"image/{c.split('.')[1]}"
            }
            self.db.inserir_tabela('produtos', material_object)
            print(f"Produto adicionado! {material_object['nome']}")

        # #############################################################################
        #                                  padaria                                    #
        # #############################################################################
        
        padaria_folder = "assets/padaria"
        padaria_filelist = listdir(padaria_folder)
        for c in padaria_filelist:
            padaria_object = {
                "categoria_id": categoria_padaria,
                "nome": c.split('.')[0].title(),
                "descricao": descricao,
                "preco": float(f"{randint(1,60)}.{randint(0,9)}"),
                "disponivel": True,
                "quantidade_disponivel": randint(1,20),
                "imagem_byte": open(padaria_folder + '/' + c, 'rb').read(),
                "imagem_nome": c,
                "imagem_tipo": f"image/{c.split('.')[1]}"
            }
            self.db.inserir_tabela('produtos', padaria_object)
            print(f"Produto adicionado! {padaria_object['nome']}")
        
        # #############################################################################
        #                                  bebidas                                    #
        # #############################################################################
                
        bebidas_folder = "assets/bebidas"
        bebidas_filelist = listdir(bebidas_folder)

        for c in bebidas_filelist:
            bebidas_object = {
                "categoria_id": categoria_bebidas,
                "nome": c.split('.')[0].title(),
                "descricao": descricao,
                "preco": float(f"{randint(1,60)}.{randint(0,9)}"),
                "disponivel": True,
                "quantidade_disponivel": randint(1,20),
                "imagem_byte": open(bebidas_folder + '/' + c, 'rb').read(),
                "imagem_nome": c,
                "imagem_tipo": f"image/{c.split('.')[1]}"
            }
            self.db.inserir_tabela('produtos', bebidas_object)
            print(f"Produto adicionado! {bebidas_object['nome']}")      
    
    def generate_admins(self):
        print("#"*100)
        print("Gerando Administradores!")
        print("#"*100)
        
        self.db.inserir_tabela("admins", {
            "nome": "rafael",
            "email": "rafasdsm@gmail.com",
            "senha": "12345"
        })
        
        for _ in range(5):  # Cria 5 administradores falsos
            admin = {
                "nome": self.faker.name(),
                "email": self.faker.email(),
                "senha": self.faker.password(length=10)
            }
            self.db.inserir_tabela("admins", admin)
            print(f"Admin adicionado: {admin['nome']}")
    
    def generate_pedidos_e_itens(self, qtd_pedidos=300):
        print("$"*100)
        print("Gerando pedidos e itens de pedido!")
        print("$"*100)

        clientes = self.db.ler_tabela("clientes")
        produtos = self.db.ler_tabela("produtos")

        if not clientes or not produtos:
            print("Gere clientes e produtos antes de gerar pedidos!")
            return

        status_pagamento = ["pendente", "pago", "cancelado"]
        status_entrega = ["Em preparacao", "Em rota de entrega", "Entregue"]
        formas_pagamento = ["Pix", "Crédito", "Débito"]

        for _ in range(qtd_pedidos):
            cliente = choice(clientes)
            cliente_id = cliente[0]
            endereco_cliente = cliente[5]

            # Data aleatória nos últimos 365 dias
            data_pedido = datetime.now() - timedelta(
                days=randint(0, 365),
                hours=randint(0, 23),
                minutes=randint(0, 59)
            )

            # Escolhe de 1 a 5 produtos distintos para o pedido
            produtos_pedido = self.faker.random_elements(
                elements=produtos,
                length=randint(1, min(5, len(produtos))),
                unique=True
            )

            # Monta os itens e calcula o total antes de inserir o pedido
            itens = []
            total = 0
            for produto in produtos_pedido:
                quantidade = randint(1, 5)
                preco_unitario = produto[4]  # Índice 4 é o preço na tabela produtos
                total += quantidade * preco_unitario
                
                itens.append({
                    "produto_id": produto[0],
                    "quantidade": quantidade,
                    "preco_unitario": float(preco_unitario),
                })

            # CORREÇÃO AQUI: O dicionário do pedido agora é montado FORA do loop de produtos
            pedido = {
                "cliente_id": cliente_id,
                "data_pedido": data_pedido,
                "status": choice(status_entrega),
                "valor_total": round(total, 2),
                "endereco_entrega": endereco_cliente,
                "status_pagamento": choice(status_pagamento),
                "forma_pagamento": choice(formas_pagamento),
            }

            # Insere o pedido no banco
            self.db.inserir_tabela("pedidos", pedido)

            # Pega o ID do pedido recém-inserido (maior ID da tabela)
            todos_pedidos = self.db.ler_tabela("pedidos")
            pedido_id = max(p[0] for p in todos_pedidos)

            # Insere os itens vinculados ao pedido correto
            for item in itens:
                item["pedido_id"] = pedido_id
                self.db.inserir_tabela("itenspedido", item)

            print(f"Pedido {pedido_id} criado com {len(itens)} itens | total: R$ {total:.2f}")
            
    def generate_all(self):
        self.generate_clientes()
        print("\n"*3)
        self.generate_categorias()
        print("\n"*3)
        self.generate_produtos()
        print("\n"*3)
        self.generate_admins()
        print("\n"*3)
        self.generate_pedidos_e_itens()


if __name__ == "__main__":
    GenerateFakeData().generate_all()