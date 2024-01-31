from flask import Flask, render_template, request,redirect, session, flash, url_for
from app.controler import Usuario
from cryptography.fernet import Fernet
import datetime
import traceback
import base64
import os
import hashlib

caminho_chave = f'app/chave.key'
with open(caminho_chave,'rb') as arquivo:
    key = arquivo.read()

cipher_suite = Fernet(key)

def init_app(app):
    @app.route('/')
    def index():
        title = 'EasyNotes'

        if 'usuario_logado' not in session or session['usuario_logado'] is None or session['stat'] is True:
            return redirect(url_for('login'))
        else:
            caminhos_arquivos_ordenados = []
            conteudos_arquivos_ordenados = []
            try:
                login = session['usuario_logado']
                usuarios = Usuario.buscaUsuario()
                caminhos_arquivos = []
                conteudos_arquivos = []

                for diretorio, _, arquivos in os.walk(f'app/blocos/{login}'):
                    for arquivo in arquivos:
                        caminho_completo = os.path.join(diretorio, arquivo)
                        caminhos_arquivos.append(caminho_completo)

                        with open(caminho_completo, 'rb') as arquivo:
                            conteudo_encryptado = arquivo.read()
                        conteudo_en = cipher_suite.decrypt(conteudo_encryptado).decode('utf-8')
                        conteudos_arquivos.append(conteudo_en)
                        caminhos_arquivos_ordenados = sorted(caminhos_arquivos, key=os.path.getctime, reverse=True)
                        conteudos_arquivos_ordenados = [conteudos_arquivos[caminhos_arquivos.index(caminho)] for caminho in caminhos_arquivos_ordenados]
            except Exception as e:
                print("teste")

            return render_template('index.html', arquivos=zip(caminhos_arquivos_ordenados, conteudos_arquivos_ordenados), usuarios=usuarios, title=title)

    @app.route("/bloco/<string:caminho>")
    def bloco(caminho):
        title = 'EasyNotes | Editar'
        
        if 'usuario_logado' not in session or session['usuario_logado']== None or session['stat']== True:
            return redirect(url_for('login'))
        else:
            caminho = caminho
            login = session['usuario_logado']
            with open(f'app/blocos/{login}/{caminho}','rb') as arquivo:
                conteudo_encryptado = arquivo.read()
            conteudo_en = cipher_suite.decrypt(conteudo_encryptado)
            conteudo = conteudo_en.decode()

        return render_template('bloco.html',conteudo=conteudo,titulo=caminho, title=title)
    
    @app.route('/salvar',methods=['GET','POST'])
    def salvar():
        texto = request.form['texto']
        titulo = request.form['titulo']
        titulo_novo = request.form['titulo_novo']
        cor = request.form['cor']
        cor_antiga = request.form['cor_antiga']
        login = session['usuario_logado']
        caminho = f'app/blocos/{login}'
        data = titulo.split('*')[1]

        if texto == '':
            print("primeira regra")
            nome = titulo_novo
            titulo_formatado = f'{nome}&{cor}*{data}'
            for file in os.listdir(caminho):
                if file == titulo:
                    original_path = os.path.join(caminho, titulo)
                    new_path = os.path.join(caminho, titulo_formatado)
                    os.rename(original_path, new_path)
                    flash("Anotação salva!", "success")

        elif cor == cor_antiga and titulo.split('&')[0] == titulo_novo and texto != None:
            print("segunda regra")
            nome = titulo
            titulo_formatado = titulo
            texto_encryptado = cipher_suite.encrypt(texto.encode())
            with open(f'{caminho}/{titulo}','wb') as arquivo:
                arquivo.write(texto_encryptado)
                flash("Anotação salva!", "success")

        else:
            print("terceira regra")
            texto_encryptado = cipher_suite.encrypt(texto.encode())
            with open(f'{caminho}/{titulo}','wb') as arquivo:
                arquivo.write(texto_encryptado)
            nome = titulo_novo
            titulo_formatado = f'{nome}&{cor}*{data}'
            for file in os.listdir(caminho):
                if file == titulo:
                    original_path = os.path.join(caminho, titulo)
                    new_path = os.path.join(caminho, titulo_formatado)
                    os.rename(original_path, new_path)
                    flash("Anotação salva!", "success")

        if 'save_and_exit' in request.form:
            return redirect(url_for('index'))

        return redirect(url_for('bloco',caminho=titulo_formatado))
    
    
    @app.route('/novo',methods=['POST'])
    def novo():
        try:
            data_atual = datetime.datetime.today()
            date = data_atual.strftime('%d-%m-%Y às %H:%M:%S')
            login = session['usuario_logado']
            cor = request.form['cor']
            nome = request.form['nome'].split('/')[0]
            texto = request.form['texto']
            texto_encryptado = cipher_suite.encrypt(texto.encode())
            filename = f'app//blocos//{login}//{nome}&{cor}*{date}.txt'

            with open(filename, 'wb') as f:
                f.write(texto_encryptado)
                flash("Anotação criada!", "success")

        except Exception as e:
            return f"Erro ao salvar o arquivo: {str(e)}"
        else:
            return redirect(url_for('index'))
        
 
    @app.route('/exclui',methods=['POST'])
    def exclui():
        login = session['usuario_logado']
        nome = request.form['nome']
        pasta = f'app//blocos//{login}'
        print(repr(pasta))
        print(repr(nome))
        dir = os.listdir(pasta)
        for file in dir:
            if file == (f"{nome}"):
                print('foi apagado')
                os.remove(os.path.join(pasta,file))
                flash("Anotação excluída!", "success")

        return redirect(url_for('index'))

    
##################################################################################################
#----------------------------- ROTA DE LOGIN E LOGICA DE GERENCIA --------------------------------
    @app.route('/login')
    def login():
        title = 'EasyNotes | Login'

        proxima = request.args.get('proxima')

        return render_template('login.html',proxima=proxima, title=title)

    @app.route('/autentificacao')
    def autentificacao():
        title = 'EasyNotes | Alterar senha'

        if 'usuario_logado' not in session or session['usuario_logado']== None and session['stat']== False:
            return redirect(url_for('login'))
        else:
            proxima = request.args.get('proxima')

        return render_template('autentificacao.html',proxima=proxima, title=title)
    
    @app.route('/alterpass', methods=['POST',])
    def alterpass():
        login = request.form['login']
        senha = request.form['senha']
        senha1 = request.form['senha1']
        title = 'EasyNotes | Alterar a senha'

        if senha == senha1:
            senha  = hashlib.sha256(request.form['senha'].encode()).hexdigest()
            Usuario.trocasenha(login,senha)
            session['usuario_logado'] = login
            flash("Senha alterada!", "success")
            return redirect(url_for('index'))
        else:
            flash("As senhas não são iguais.", "danger")

        return render_template('autentificacao.html', title=title)

    @app.route('/autenticar', methods=['POST'])
    def autenticar():
        usuario = request.form['usuario'].lower()
        senha  = hashlib.sha256(request.form['senha'].encode()).hexdigest()

        credencial = Usuario.login(usuario)
        if credencial:
            login = credencial[0]
            password = credencial[1]
            nivel = credencial[2]
            stat = credencial[3]
        else:
            flash("Esse usuário não existe!", "danger")
            return redirect(url_for('login'))

        if stat == True and senha == password:
            inicial = login.capitalize()[0]
            session['usuario_logado'] = login
            session['credencial'] = nivel
            session['inicial'] = inicial
            session['stat'] = stat
            flash(f"Altere a sua senha.", "success")
            return redirect(url_for('autentificacao'))
        else:      
            if usuario == login:
                if senha == password:
                    inicial = login.capitalize()[0]
                    session['usuario_logado'] = login
                    session['credencial'] = nivel
                    session['inicial'] = inicial
                    session['stat'] = stat
                    pasta = f'app/blocos'
                    caminho_nova_pasta = os.path.join(pasta, usuario)
                    if not os.path.exists(caminho_nova_pasta):
                        os.makedirs(caminho_nova_pasta)
                    flash('Bem-vindo(a), ' + session['usuario_logado'].title() + '!', "success")
                    return redirect(url_for('index'))
                else:
                    flash('Usuário ou senha incorretos.', "danger")
                    return redirect(url_for('login'))

    @app.route('/logoff')
    def logoff():
        session['usuario_logado'] = None
        flash('Logoff realizado.', "info")

        return redirect(url_for('login'))


    @app.route('/gerenciausuario',methods=['GET','POST'])
    def gerenciausuario():
        try:
            verificar = request.form['verificar']
            login = request.form['login'].lower()
            nome = request.form['nome2'].upper()
            credencial = request.form['tratamento'].lower()
            nome1 = request.form['nome1']
            senha = hashlib.sha256(b'123456').hexdigest()
            if verificar == 'adicionar':
                Usuario.criaUsuario(login,nome,senha,credencial)
                flash("Novo usuário adicionado.","success")
            elif verificar == 'resetar':
                Usuario.resetaUsuario(nome1,senha)
                flash(f"A senha do(a) {nome1} foi alterada.","success")
            elif verificar == 'excluir':
                Usuario.exclui(nome1)
                flash(f"Excluído: {nome1}.","success")

        except Exception as e:
            traceback.print_exc()
            flash("Ocorreu um erro. Tente novamente.","danger")
        
        return redirect(url_for('index'))
    
#--------------------------------------- FIM ---------------------------------------
####################################################################################
    
    @app.route('/alteracao')
    def alteracao():
        title = 'EasyNotes | Esqueci minha senha'

        proxima = request.args.get('proxima')

        return render_template('alteracao.html', title=title)
    
    @app.route('/confirmausuario', methods=['GET','POST'])
    def confirmausuario():
        nome = request.form['nome'].strip().upper()
        cpf = request.form['cpf'].strip()
        resultado = Usuario.consulta_cpf(nome,cpf)
        if resultado != None:
            senha = hashlib.sha256(b'123456').hexdigest()
            Usuario.resetaUsuario(nome,senha)
            flash("Senha resetada para '123456' ","success")

            return redirect(url_for('login'))
        else:
            flash("Não foi possível resetar.","danger")

        return redirect(url_for('alteracao'))