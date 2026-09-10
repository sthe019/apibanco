from database import Dbcontroller
from faker import Faker

db = Dbcontroller()
tabela = "clientes"

def gerar_clientes(numero:int):
    fk = Faker('pt-br')
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

def gerar_clientes_tabela(numero:int):
    dados = gerar_clientes(numero)
    for c in dados:db.inserir_tabela(tabela,c)
    return print("Dados inseridos com sucesso!")

#gerar_clientes_tabela(200)