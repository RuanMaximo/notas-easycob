import os
import shutil
import psycopg2 as pg2
from dotenv import load_dotenv

load_dotenv()
conexao = os.getenv("CONEXAO")
conexao26 = os.getenv("CONEXAO26")

class Usuario:
    def login(usuario):
        con = pg2.connect(conexao)
        cur = con.cursor()
        sql = """ select login,senha,credencial,stat,id from usuarios_t where login = %s; """
        cur.execute(sql,(usuario,))
        result = cur.fetchone()
        cur.close()
        con.close()
        return result

    def criaUsuario(login,nome,senha,credencial):
        con = pg2.connect(conexao)
        cur = con.cursor()
        sql = "insert into usuarios_t (login,nome,senha,credencial,stat) values ( %s, %s, %s, %s, True);"
        cur.execute(sql,(login,nome,senha,credencial,))
        con.commit()
        cur.close()
        con.close()

    def resetaUsuario(nome1,senha):
        con = pg2.connect(conexao)
        cur = con.cursor()
        sql = "update usuarios_t set senha = %s,stat = True where nome = %s;"
        cur.execute(sql,(senha,nome1,))
        con.commit()
        cur.close()
        con.close()

    def buscaUsuario():
        con = pg2.connect(conexao)
        cur = con.cursor()
        sql = f'select nome from usuarios_t order by nome'
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        con.close()
        return result

    def trocasenha(login,senha):
        con = pg2.connect(conexao)
        cur = con.cursor()
        sql = "update usuarios_t set senha = %s,stat = False where login = %s; "
        cur.execute(sql,(senha,login,))
        con.commit()
        cur.close()
        con.close()

    def exclui(nome1):
        con = pg2.connect(conexao)
        cur = con.cursor()
        sql = "select nome,login,id from usuarios_t where nome = %s"
        cur.execute(sql,(nome1,))
        result = cur.fetchone()
        cur.close()
        con.close()

        nome = result[0]
        login = result[1]
        id = result[2]

        if nome != nome1:
            result = ['Ocorreu um erro!']
        else:
            con = pg2.connect(conexao)
            cur = con.cursor()
            sql = "delete from usuarios_t where id = %s"
            cur.execute(sql,(id,))
            con.commit()
            cur.close()
            con.close()

            pasta = f'app/blocos'
            caminho_nova_pasta = os.path.join(pasta, login)
            if os.path.exists(caminho_nova_pasta):
                shutil.rmtree(caminho_nova_pasta)
                result = "Usuario excluido!"
            else:
                result = "Pasta do usuario não encontrado"
    

    def consulta_cpf(nome,cpf):
        try:
            con = pg2.connect(conexao26)
            cur = con.cursor()
            sql = "select nome,cpf from tab_funcionario where cpf=%s and nome=%s; "
            cur.execute(sql,(cpf,nome,))
            resultado = cur.fetchone()
            cur.close()
            con.close()
            if resultado == None:
                con = pg2.connect(conexao26)
                cur = con.cursor()
                sql = "select nome,cpf from tab_estagiario where cpf=%s and nome=%s; "
                cur.execute(sql,(cpf,nome,))
                resultado = cur.fetchone()
                cur.close()
                con.close()
        except:
            resultado = None
        
        return resultado