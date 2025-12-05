from flask import Flask, render_template, request, redirect, Blueprint, session, flash, jsonify
import psycopg2
from datetime import datetime, timedelta

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

    cursor.execute("SELECT * FROM profissional")
    profissionais = cursor.fetchall()

    return render_template('Cliente/servicos.html', cliente=cliente, servicos=servicos, profissionais=profissionais)


@bp.route('/profissionais/<pagina>')
def profissionais(pagina):

    pagina = int(pagina)
    por_pagina = 6
    offset = (pagina - 1) * por_pagina
    cursor.execute("SELECT * FROM profissional LIMIT %s OFFSET %s", (por_pagina, offset))
    profissionais = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM profissional;")
    total_profissionais = cursor.fetchone()[0]
    total_paginas = (total_profissionais + por_pagina - 1) // por_pagina

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
                           horarios_por_profissional=horarios_por_profissional, cliente=cliente, pagina=pagina, total_paginas=total_paginas,)


@bp.route('/agendar/<id>')
def agenda(id):
    if 'id' not in session:
        return redirect('/login')
    cursor.execute('SELECT * FROM servico WHERE id = %s', (id,))
    servico = cursor.fetchone()

    id_profissioal = servico[1]
    cliente = getClient()

    cursor.execute('SELECT * FROM profissional WHERE id = %s', (id_profissioal,))
    profissional = cursor.fetchone()

    return render_template("agendamento.html", servico=servico, profissional=profissional, cliente=cliente)


@bp.route('/horarios-disponiveis')
def horarios_disponiveis():
    data = request.args.get('data')
    profissional_id = request.args.get('professional_id')
    servico_id = request.args.get('servico_id')

    try:
        # Converter data para objeto datetime
        data_obj = datetime.strptime(data, '%Y-%m-%d')

        # Mapear dia da semana para seu sistema (domingo=1, segunda=2, etc.)
        dias_semana = {
            0: 2,  # segunda
            1: 3,  # terça
            2: 4,  # quarta
            3: 5,  # quinta
            4: 6,  # sexta
            5: 7,  # sábado
            6: 1  # domingo
        }
        dia_semana = dias_semana[data_obj.weekday()]

        # Resto do código permanece igual...
        cursor.execute("""
            SELECT hora_inicio, hora_fim 
            FROM disponibilidade_profissional 
            WHERE profissional_id = %s AND dia_semana = %s
        """, (profissional_id, dia_semana))

        # ... resto do código

        disponibilidade = cursor.fetchone()
        print(f"DEBUG: Disponibilidade encontrada: {disponibilidade}")

        if not disponibilidade:
            print("DEBUG: Nenhuma disponibilidade encontrada para este dia")
            return jsonify([])

        # 2. Buscar horários já agendados
        cursor.execute("""
            SELECT horario 
            FROM agendamento 
            WHERE profissional_id = %s AND data_agendamento = %s AND status != 'cancelado'
        """, (profissional_id, data))

        agendamentos = cursor.fetchall()
        print(f"DEBUG: Agendamentos existentes: {agendamentos}")

        # 3. Buscar horários bloqueados
        cursor.execute("""
            SELECT hora_inicio, hora_fim 
            FROM horario_bloqueado 
            WHERE profissional_id = %s AND data_bloqueio = %s
        """, (profissional_id, data))

        horarios_bloqueados = cursor.fetchall()
        print(f"DEBUG: Horários bloqueados: {horarios_bloqueados}")

        # 4. Buscar duração do serviço
        cursor.execute("SELECT duracao_minutos FROM servico WHERE id = %s", (servico_id,))
        servico = cursor.fetchone()
        # Acesse por índice, não por chave
        duracao_servico = servico[0]
        print(f"DEBUG: Duração do serviço: {duracao_servico} minutos")

        # 5. Gerar horários disponíveis
        horarios_disponiveis = gerar_horarios_disponiveis(
            disponibilidade[0],  # hora_inicio (índice 0)
            disponibilidade[1],  # hora_fim (índice 1)
            agendamentos,
            horarios_bloqueados,
            duracao_servico
        )

        print(f"DEBUG: Horários disponíveis gerados: {horarios_disponiveis}")

        return jsonify(horarios_disponiveis)

    except Exception as e:
        print(f"DEBUG: Erro - {e}")
        import traceback
        traceback.print_exc()
        return jsonify([])


def gerar_horarios_disponiveis(hora_inicio, hora_fim, agendamentos, horarios_bloqueados, duracao_servico):
    """Gera lista de horários disponíveis considerando agendamentos e bloqueios"""
    horarios = []

    # Converter para objetos datetime para facilitar cálculos
    try:
        if isinstance(hora_inicio, str):
            inicio = datetime.strptime(hora_inicio, '%H:%M:%S')
        else:
            inicio = datetime.combine(datetime.today(), hora_inicio)

        if isinstance(hora_fim, str):
            fim = datetime.strptime(hora_fim, '%H:%M:%S')
        else:
            fim = datetime.combine(datetime.today(), hora_fim)
    except Exception as e:
        print(f"DEBUG: Erro ao converter horários - {e}")
        return []

    duracao = timedelta(minutes=duracao_servico)
    horario_atual = inicio

    while horario_atual + duracao <= fim:
        horario_str = horario_atual.strftime('%H:%M')
        horario_fim_calc = horario_atual + duracao

        # Verificar se este horário está livre
        agendado = esta_agendado(horario_atual.time(), horario_fim_calc.time(), agendamentos)
        bloqueado = esta_bloqueado(horario_atual.time(), horario_fim_calc.time(), horarios_bloqueados)

        if not agendado and not bloqueado:
            horarios.append(horario_str)

        horario_atual += timedelta(minutes=30)

    return horarios


def esta_agendado(horario_inicio, horario_fim, agendamentos):
    """Verifica se o horário está agendado considerando a duração"""
    for agendamento in agendamentos:
        agendamento_inicio = agendamento[0]
        if isinstance(agendamento_inicio, str):
            agendamento_inicio = datetime.strptime(agendamento_inicio, '%H:%M:%S').time()

        # Buscar duração do agendamento existente
        cursor.execute(
            "SELECT duracao_minutos FROM servico WHERE id = (SELECT servico_id FROM agendamento WHERE horario = %s LIMIT 1)",
            (agendamento_inicio,))
        duracao_agendamento = cursor.fetchone()
        if duracao_agendamento:
            duracao_agendamento = duracao_agendamento[0]
            agendamento_fim = (datetime.combine(datetime.today(), agendamento_inicio) + timedelta(
                minutes=duracao_agendamento)).time()

            # Verificar sobreposição
            if not (horario_fim <= agendamento_inicio or horario_inicio >= agendamento_fim):
                return True

    return False


def esta_bloqueado(horario_inicio, horario_fim, horarios_bloqueados):
    """Verifica se o horário está bloqueado"""
    for bloqueado in horarios_bloqueados:
        bloqueado_inicio = bloqueado[0]
        bloqueado_fim = bloqueado[1]

        if isinstance(bloqueado_inicio, str):
            bloqueado_inicio = datetime.strptime(bloqueado_inicio, '%H:%M:%S').time()
        if isinstance(bloqueado_fim, str):
            bloqueado_fim = datetime.strptime(bloqueado_fim, '%H:%M:%S').time()

        # Verificar sobreposição
        if not (horario_fim <= bloqueado_inicio or horario_inicio >= bloqueado_fim):
            return True

    return False

def bloquear_horario(profissional_id, data_bloqueio, hora_inicio, hora_fim, motivo="Agendamento"):
    """Insere um horário bloqueado na tabela"""
    cursor.execute("""
        INSERT INTO horario_bloqueado 
        (profissional_id, data_bloqueio, hora_inicio, hora_fim, motivo, data_criacao)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (profissional_id, data_bloqueio, hora_inicio, hora_fim, motivo))
    banco.commit()

@bp.route('/agendar', methods=['POST'])
def agendar():
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não logado'})

    data = request.json
    data_agendamento = data['data']
    horario = data['horario']
    profissional_id = data['profissional_id']
    servico_id = data['servico_id']
    cliente_id = session['id']

    try:
        # Buscar duração e preço do serviço
        cursor.execute("SELECT duracao_minutos, preco FROM servico WHERE id = %s", (servico_id,))
        servico = cursor.fetchone()
        duracao = servico[0]
        preco = servico[1]

        # Converter horário para time
        horario_time = datetime.strptime(horario, '%H:%M').time()

        # Calcular horário de fim
        horario_inicio = datetime.strptime(horario, '%H:%M')
        horario_fim = horario_inicio + timedelta(minutes=duracao)
        horario_fim_time = horario_fim.time()

        # Verificar se o horário ainda está disponível (PostgreSQL)
        cursor.execute("""
            SELECT id FROM agendamento 
            WHERE profissional_id = %s AND data_agendamento = %s 
            AND (
                (horario <= %s AND (horario + INTERVAL '%s minutes') > %s)
                OR (horario < (%s + INTERVAL '%s minutes') AND (horario + INTERVAL '%s minutes') > %s)
            )
            AND status != 'cancelado'
        """, (profissional_id, data_agendamento, horario_time, duracao, horario_time,
              horario_time, duracao, duracao, horario_time))

        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Horário já ocupado'})

        # Inserir agendamento
        cursor.execute("""
            INSERT INTO agendamento 
            (cliente_id, profissional_id, servico_id, data_agendamento, horario, status, valor_total, data_criacao)
            VALUES (%s, %s, %s, %s, %s, 'pendente', %s, NOW())
        """, (cliente_id, profissional_id, servico_id, data_agendamento, horario_time, preco))

        # Bloquear o horário na tabela horario_bloqueado
        cursor.execute("""
            INSERT INTO horario_bloqueado 
            (profissional_id, data_bloqueio, hora_inicio, hora_fim, motivo, data_criacao)
            VALUES (%s, %s, %s, %s, 'Agendamento', NOW())
        """, (profissional_id, data_agendamento, horario_time, horario_fim_time))

        banco.commit()

        return jsonify({'success': True, 'message': 'Agendamento realizado com sucesso'})

    except Exception as e:
        print(f"Erro ao agendar: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@bp.route('/agendamentosCliente')
def agendamentosCliente():
    if 'id' not in session:
        return redirect("/login")
    cliente_id = session['id']
    cursor.execute("SELECT * FROM agendamento WHERE id = %s", (cliente_id,))
    agendamentos = cursor.fetchall()
    cliente = getClient()

    cursor.execute("SELECT * FROM agendamento WHERE status IN (%s, %s)", ("pendente", "confirmado"))
    agendamentos_futuros = cursor.fetchall()

    cursor.execute("SELECT * FROM agendamento WHERE status IN (%s, %s)", ("realizado", "cancelado"))
    agendamentos_passados = cursor.fetchall()

    cursor.execute("SELECT * FROM servico")
    servicos = cursor.fetchall()

    cursor.execute("SELECT id, nome_completo, nome_estabelecimento FROM profissional ")
    profissionais = cursor.fetchall()
    return render_template("cliente/agendamentos.html", agendamentos=agendamentos,
                           cliente = cliente, agendamentos_futuros=agendamentos_futuros,
                           servicos = servicos, profissionais = profissionais, agendamentos_passados=agendamentos_passados)


@bp.route('/confirmarAgendamento/<int:id>')
def confirmar_agendamento(id):
    if 'id' not in session:
        return redirect('/login')

    cursor.execute("UPDATE agendamento SET status = 'confirmado' WHERE id = %s", (id,))
    banco.commit()

    flash('Agendamento confirmado com sucesso!', 'success')
    return redirect('/agendamentosCliente')


@bp.route('/cancelarAgendamento/<int:id>')
def cancelar_agendamento(id):
    if 'id' not in session:
        return redirect('/login')

    cursor.execute("UPDATE agendamento SET status = 'cancelado' WHERE id = %s", (id,))
    banco.commit()

    flash('Agendamento cancelado com sucesso!', 'success')
    return redirect('/agendamentosCliente')