from flask import Flask, render_template, request, redirect, Blueprint, session, flash
import psycopg2

banco = psycopg2.connect(host='localhost',
                         dbname='AgendeJa',
                         user='postgres',
                         password='senai')
cursor = banco.cursor()

bp = Blueprint('Cliente', __name__)


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

@bp.route('/editarCliente', methods=['GET', 'POST'])
def editarCliente():
    cliente = getClient()
    if request.method == 'POST':
        foto_perfil = request.files['foto_perfil']
        foto_blob = foto_perfil.read()
        nome = request.form['nome']
        CPF = request.form['CPF']
        whatsapp = request.form['whatsapp']

        cep = request.form['cep']
        rua = request.form['rua']
        numero = request.form['numero']
        complemento = request.form['complemento']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']

        cursor.execute(
            "UPDATE cliente SET nome_completo = %s, cpf = %s, telefone = %s, foto_perfil = %s, cep = %s, rua = %s, numero_casa = %s, complemento = %s, bairro = %s, cidade = %s, estado = %s WHERE id = %s",
            (nome, CPF, whatsapp, foto_blob, cep, rua, numero, complemento, bairro, cidade, estado, cliente[0]))
        banco.commit()
        flash('Cliente editado')
        return redirect('/editarCliente')
    return render_template('cliente/edicao.html', cliente=cliente)


@bp.route('/servicos')
def servicos():
    cliente = getClient()
    cursor.execute("SELECT * FROM servico")
    servicos = cursor.fetchall()

    profissionais = getProfissional()

    return render_template('Cliente/servicos.html', cliente=cliente, servicos=servicos, profissionais=profissionais)


@bp.route('/profissionais')
def profissionais():
    cursor.execute('SELECT * FROM profissional')
    profissionais = cursor.fetchall()

    cursor.execute('SELECT profissional_id, preco FROM Servico')
    precos = cursor.fetchall()

    cursor.execute('SELECT * FROM disponibilidade_profissional')
    horarios_raw = cursor.fetchall()

    # Agrupar horários por profissional_id
    horarios_por_profissional = {}
    for horario in horarios_raw:
        prof_id = horario[1]  # profissional_id está na posição 1
        if prof_id not in horarios_por_profissional:
            horarios_por_profissional[prof_id] = []
        horarios_por_profissional[prof_id].append(horario)
    cliente = getClient()

    return render_template('cliente/profissionais.html', profissionais=profissionais, precos=precos,
                           horarios_por_profissional=horarios_por_profissional, cliente=cliente)

@bp.route('/agendar/<id>')
def agenda(id):
    cursor.execute('SELECT * FROM servico WHERE id = %s', (id,))
    servico = cursor.fetchone()

    id_profissioal = servico[1]

    cursor.execute('SELECT * FROM profissional WHERE id = %s', (id_profissioal,))
    profissional = cursor.fetchone()

    return render_template("agendamento.html", servico=servico, profissional=profissional)
