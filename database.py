from mssql_python import connect

class Dbcontroller:
    def __init__(self):
        self.db = self.connect_database()

    def open_text(self):
        data = {}
        with open("banco.txt",'r') as file:
            for c in file.readlines():
                data[c.split("=")[0]] = c.split("=")[1].replace("\n","")
            file.close()

        return data

    
    def connect_database(self):
        try:
            data = self.open_text()

            conn_str = (
                f"Server={data['server']};"
                f"Database={data['database']};"
                f"Trusted_Connection=yes;"
                f"Encrypt=no;"
            )

            db = connect(conn_str)
            print("Sucesso ao conectar ao banco!")
            return db

        except Exception as err:
            print(f"Erro ao se conectar ao banco: {err}")
            raise


    def ler_banco(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            temp = cursor.fetchall()
            tabelas = []
            for c in temp:tabelas.append(list(c))
            return tabelas
        except Exception as err:
            print(f"Incapaz de realizar listagem da tabela!\n{err}")
            return f"Incapaz de realizar listagem da tabela!: {err}"
        finally:
            cursor.close()

    def procurar_tabela(self,identificador:list,tabela:str):
        cursor = self.db.cursor()
        query = f"select * from site.dbo.{tabela} where {identificador[0]} = {identificador[1]};"
        try:
            cursor.execute(query)
            response = cursor.fetchall()[0]
            return response
        except Exception as e:
            response = f"Error: {e}"
            return response
        finally:
            cursor.close()


    def ler_tabela(self,tabela:str):
        cursor = self.db.cursor()
        query = f"SELECT * FROM {tabela}"
        try:
            cursor.execute(query)
            temp = cursor.fetchall()
            data = []
            for c in temp:data.append(list(c))
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
        sql = f"DELETE FROM {tabela} WHERE {indentificador_nome} = ?"

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
        placeholders = ", ".join(["?"] * len(dados))
        valores = tuple(dados.values())
        
        query_insercao = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"   
        
        try:
            cursor.execute(query_insercao, valores)
            self.db.commit()
            return f"Sucesso ao inserir na tabela {tabela} os dados: {dados}"
        except Exception as e:
            self.db.rollback()
            return f"Erro ao inserir na tabela {tabela} os dados: {dados} | Erro: {e}"
        finally:
            cursor.close()

    def atualizar_imagem_produto(self, produto_id: int, imagem_bytes: bytes, nome: str, tipo: str):
        query = """
            UPDATE produtos
            SET imagem_byte = ?, imagem_nome = ?, imagem_tipo = ?
            WHERE produto_id = ?
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(query, (imagem_bytes, nome, tipo, produto_id))
            self.db.commit()
            return cursor.rowcount
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()
