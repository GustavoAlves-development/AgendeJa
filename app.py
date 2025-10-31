from flask import Flask, render_template, send_file, send_from_directory, request, session, redirect, flash
from Rotas import Cliente
from Rotas import Profissional
import psycopg2
import io

banco = psycopg2.connect(host='localhost',
                         dbname='AgendeJa',
                         user='postgres',
                         password='senai')
cursor = banco.cursor()
app = Flask(__name__)
app.secret_key = "viniciusEdu"
app.register_blueprint(Cliente.bp)
app.register_blueprint(Profissional.bp)


@app.route('/', methods=['GET'])
def Home():
    if 'id' in session:
        index = session['id']
        cursor.execute("SELECT * FROM cliente WHERE id = %s", (index,))
        cliente = cursor.fetchone()
        if cliente:
            return render_template('cliente/cliente.html', cliente=cliente)
        else:
            cursor.execute("SELECT * FROM profissional WHERE id = %s", (index,))
            profissional = cursor.fetchone()
            return render_template('profissional/gestao.html', profissional=profissional)
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
    return render_template('contato.html')


@app.get('/sobre')
def sobre():
    return render_template('sobre.html')


def recuperar_foto(id):
    cursor.execute("SELECT foto_perfil FROM cliente WHERE =?;", (id,))
    ft = cursor.fetchone()
    return ft[0]


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
        return send_from_directory("static/imagens/", "estudante.png")


if __name__ == '__main__':
    app.run()
