from flask import Flask, render_template, send_file, send_from_directory, request, session, redirect, flash
from Rotas import Cliente
from Rotas import Profissional
import psycopg2
import io
from PIL import Image

banco = psycopg2.connect(host='localhost',
                         dbname='AgendeJa',
                         user='postgres',
                         password='senai')
cursor = banco.cursor()
app = Flask(__name__)
app.secret_key = "viniciusEdu"
app.register_blueprint(Cliente.bp)
app.register_blueprint(Profissional.bp)

def getClient():
    if 'id' not in session:
        return None
    cursor.execute('SELECT * FROM cliente WHERE id = %s', (session['id'],))
    cliente = cursor.fetchone()
    return cliente


def getProfissional():
    if 'id' not in session:
        return None
    cursor.execute('SELECT * FROM profissional WHERE id = %s', (session['id'],))
    profissional = cursor.fetchone()
    return profissional

@app.route('/', methods=['GET'])
def Home():
    if 'id' in session:
        index = session['id']
        if session.get('user_type') == 'cliente':
            cursor.execute("SELECT * FROM cliente WHERE id = %s", (index,))
            cliente = cursor.fetchone()
            return render_template('cliente/cliente.html', cliente=cliente)
        else:
            return redirect('/gestao')
    return render_template('cliente/cliente.html')


@app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        # Verifica na tabela cliente
        cursor.execute('SELECT id, senha FROM cliente WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            if password == user[1]:
                session['id'] = user[0]
                session['user_type'] = 'cliente'
                return redirect('/')
            else:
                error = 'Senha incorreta'
        else:
            # Verifica na tabela profissional
            cursor.execute('SELECT id, senha FROM profissional WHERE email = %s', (email,))
            profissional = cursor.fetchone()

            if profissional:
                if password == profissional[1]:
                    session['id'] = profissional[0]
                    session['user_type'] = 'profissional'
                    return redirect('/')
                else:
                    error = 'Senha incorreta'
            else:
                error = 'Email não encontrado'

        return render_template('login.html', error=error)

    else:
        if 'id' in session:
            return redirect('/')
        return render_template('login.html')


@app.route('/cadastro', methods=['GET'])
def Cadastro():
    cursor.execute('SELECT tipo_servico FROM profissional')
    servicos = cursor.fetchall()
    return render_template('cadastro.html', categorias=servicos)


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastro():
    # Coletar dados do formulário
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    senha = request.form['senha']
    confirmar_senha = request.form['confirmarSenha']
    tipo_usuario = request.form['tipo-status']  # 'cliente' ou 'profissional'

    # Validações básicas
    if senha != confirmar_senha:
        return render_template('cadastro.html', error="As senhas não coincidem")

    # Verificar se email já existe
    cursor.execute('SELECT id FROM cliente WHERE email = %s', (email,))
    if cursor.fetchone():
        return render_template('cadastro.html', error="Email já cadastrado como cliente")

    cursor.execute('SELECT id FROM profissional WHERE email = %s', (email,))
    if cursor.fetchone():
        return render_template('cadastro.html', error="Email já cadastrado como profissional")

    try:
        if tipo_usuario == 'cliente':
            # Inserir na tabela cliente
            cursor.execute('''
                        INSERT INTO cliente (nome_completo, email, telefone, senha) 
                        VALUES (%s, %s, %s, %s)
                    ''', (nome, email, telefone, senha))
            banco.commit()

            flash("Cadastrado com sucesso!")
            return redirect('/login')

        elif tipo_usuario == 'profissional':
            # Obter tipo de profissional
            tipo_profissional = request.form.get('tipo-profissional')

            # Se selecionou "Outro", usar o campo de texto
            if tipo_profissional == 'Outro':
                tipo_profissional = request.form.get('tipo-profissional-outro')

            # Inserir na tabela profissional
            cursor.execute('''
                        INSERT INTO profissional (nome_completo, email, telefone, senha, tipo_servico) 
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (nome, email, telefone, senha, tipo_profissional))

            banco.commit()
            flash("Cadastrado com sucesso!")
            return redirect('/login')

    except Exception as e:
        banco.rollback()
        return render_template('cadastro.html', error=f"Erro ao cadastrar: {str(e)}")


@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')


@app.get('/contato')
def contato():
    user_type = session.get('user_type')
    print(user_type)

    if user_type == 'cliente':
        cliente = getClient()
        profissional = None
    elif user_type == 'profissional':
        profissional = getProfissional()
        cliente = None
    else:
        # Usuário não logado
        cliente = None
        profissional = None
    return render_template('contato.html', cliente=cliente, profissional=profissional)


@app.get('/sobre')
def sobre():
    user_type = session.get('user_type')
    print(user_type)

    if user_type == 'cliente':
        cliente = getClient()
        profissional = None
    elif user_type == 'profissional':
        profissional = getProfissional()
        cliente = None
    else:
        # Usuário não logado
        cliente = None
        profissional = None

    # SEMPRE passe ambas as variáveis
    return render_template('sobre.html', cliente=cliente, profissional=profissional)


def recuperar_foto(id):
    cursor.execute("SELECT foto_perfil FROM cliente WHERE id = %s;", (id,))
    ft = cursor.fetchone()
    if ft:
        return ft[0]
    else:
        return None


def recuperar_foto_profissional(id):
    cursor.execute("SELECT foto_perfil FROM profissional WHERE id = %s;", (id,))
    ft = cursor.fetchone()
    if ft:
        return ft[0]
    else:
        return None


def recuperar_foto_capa_profissional(id):
    cursor.execute("SELECT foto_capa FROM profissional WHERE id = %s;", (id,))
    ft = cursor.fetchone()
    if ft:
        return ft[0]
    else:
        return None

def recuperar_fotoServico(id):
    cursor.execute("SELECT imagem_servico FROM servico WHERE id = %s;", (id,))
    ft = cursor.fetchone()
    if ft:
        return ft[0]
    else:
        return None
@app.route('/imagem/<id>')
def imagem(id):
    foto_blob = recuperar_foto(id)
    if foto_blob:
        return send_file(
            io.BytesIO(foto_blob),
            mimetype='image/jpeg',
            download_name=f"imagem_{id}.jpeg"
        )
    else:
        return send_from_directory("static/imgs/", "perfil_padrao.png")


@app.route('/imagemProfissional/<id>')
def imagemProfissional(id):
    foto_blob = recuperar_foto_profissional(id)
    if foto_blob:
        return send_file(
            io.BytesIO(foto_blob),
            mimetype='image/jpeg',
            download_name=f"imagem_{id}.jpeg"
        )
    else:
        return send_from_directory("static/imgs/", "perfil_padrao.png")


@app.route('/imagemCapaProfissional/<id>')
def imagemCapaProfissional(id):
    foto_blob = recuperar_foto_capa_profissional(id)
    if foto_blob:
        return send_file(
            io.BytesIO(foto_blob),
            mimetype='image/jpeg',
            download_name=f"imagem_{id}.jpeg"
        )
    else:
        return send_from_directory("static/imgs/", "capa_padrao.jpg")


@app.route('/imagemServico/<id>')
def imagemServico(id):
    foto_blob = recuperar_fotoServico(id)

    if foto_blob:
        try:
            # Detecta tipo de imagem
            img = Image.open(io.BytesIO(foto_blob))
            mime = Image.MIME[img.format]  # ex: "image/png", "image/jpeg", etc.

            return send_file(
                io.BytesIO(foto_blob),
                mimetype=mime
            )

        except Exception as e:
            print("Erro ao detectar MIME:", e)

    # fallback único, consistente
    return send_from_directory("static/imgs/", "servico-padrao.jpg")



# Filtro para remover argumentos da query string
@app.template_filter('remove_arg')
def remove_arg_filter(args, arg_to_remove):
    """Remove um argumento dos parâmetros da requisição"""
    if not args:
        return ''

    new_args = args.copy()
    if arg_to_remove in new_args:
        del new_args[arg_to_remove]

    # Reconstruir a query string
    return '?' + '&'.join([f"{key}={value}" for key, value in new_args.items()]) if new_args else ''


if __name__ == '__main__':
    app.run()
