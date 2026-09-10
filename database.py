import mysql.connector

class Dbcontroller:
    def __init__(self):
        self.db = self.connect()

    def open_text(self):
        data = {}
        with open("banco.txt",'r') as file:
            for c in file.readlines():
                data[c.split("=")[0]] = c.split("=")[1].replace("\n","")
            file.close()

        return data

    def connect(self):
        try:
            data = self.open_text()
            db = self.db = mysql.connector.connect(
                    host="localhost",
                    user=data["user"],
                    password=data["password"],
                    database=data["database"]
                )
            print("Sucesso ao conectar ao banco!")
            return db
        except Exception as err:
            print(f"Erro ao se conectar ao banco: {err}")
            return f"Erro ao se conectar ao banco: {err}"

    def ler_banco(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()
            return tabelas
        except Exception as err:
            print(f"Incapaz de realizar listagem da tabela!\n{err}")
            return f"Incapaz de realizar listagem da tabela!: {err}"
        finally:
            cursor.close()

    def ler_tabela(self,tabela:str):
        cursor = self.db.cursor()
        query = f"SELECT * FROM {tabela}"
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except Exception as e:
            return f"Error: {e}"
        finally:cursor.close()

    def limpar_tabela(self, tabela):
            cursor = self.db.cursor()
            
            query_insercao = f"DELETE FROM {tabela}"
            
            try:
                cursor.execute(query_insercao)
                self.db.commit()
                return f"Sucesso ao limpar a tabela {tabela}"
            except Exception as e:
                self.db.rollback()
                return f"Erro ao limpar a tabela {tabela}| Erro: {e}"
            finally:
                cursor.close()

    def remover_de_tabela(self, tabela, indentificador_nome, identificador):
        cursor = self.db.cursor()
        sql = f"DELETE FROM {tabela} WHERE {indentificador_nome} = %s" # ou ? dependendo do banco

        try:
            cursor.execute(sql, (identificador,))
            self.db.commit()
            return "Item removido do banco"
        except:
            self.db.rollback()
            return "Erro ao remover o item do banco!"
        finally:
            cursor.close()

    def inserir_tabela(self, tabela, dados: dict):
        cursor = self.db.cursor()

        
        colunas = ", ".join(dados.keys())
        placeholders = ", ".join(["%s"] * len(dados))
        valores = tuple(dados.values())
        
        query_insercao = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"   
        print(query_insercao)
        
        try:
            cursor.execute(query_insercao, valores)
            self.db.commit()
            return f"Sucesso ao inserir na tabela {tabela} os dados: {dados}"
        except Exception as e:
            self.db.rollback()
            return f"Erro ao inserir na tabela {tabela} os dados: {dados} | Erro: {e}"
        finally:
            cursor.close()

    def atualizar_tabela(self, tabela,id_nome:str, id: int, coluna: str,dado):
        query = f"UPDATE {tabela} SET {coluna} = '{dado}' WHERE {id_nome}= '{id}'"
        cursor = self.db.cursor()

        try:
            cursor.execute(query)
            self.db.commit()
            return "Dados alterados com sucesso!"

        except Exception as e:
            self.db.rollback()
            return f"Erro!: {e}"

        finally:
            cursor.close()