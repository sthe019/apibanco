from database import Dbcontroller
from faker import Faker
from random import randint

db = Dbcontroller()
tabela = "clientes"
fk = Faker('pt-br')

def gerar_clientes_tabela(quant:int):
    def gerar_clientes(numero:int):
        dados = []
        for c in range(numero):
            dados.append({
                "nome":fk.name(),
                "email":fk.email(),
                "senha":fk.password(length=10),
                "telefone":fk.cellphone_number().replace("+",'').replace(" ",'').replace("-",''),
                "endereco":fk.street_address(),
                "cpf":fk.cpf().replace(".",'').replace("-",'')
            })
        return dados

    dados = gerar_clientes(quant)
    for c in dados:db.inserir_tabela(tabela,c)
    return print("Dados inseridos com sucesso!")
