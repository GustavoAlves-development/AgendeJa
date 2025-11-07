from flask import Flask, render_template, send_file, send_from_directory, request, session, Blueprint, redirect, flash
import psycopg2
import io

banco = psycopg2.connect(host='localhost',
                         dbname='AgendeJa',
                         user='postgres',
                         password='senai')
cursor = banco.cursor()

bp = Blueprint('Profissional', __name__)


def getProfissional():
    if 'id' not in session:
        return None
    cursor.execute('SELECT * FROM profissional WHERE id = %s', (session['id'],))
    profissional = cursor.fetchone()
    return profissional


@bp.route('/editarProfissional', methods=['GET', 'POST'])
def editarProfissional():
    profissional = getProfissional()
    if request.method == 'POST':
        # Informações Básicas
        nome = request.form['nome']
        estabelecimento = request.form.get('estabelecimento', '')  # Campo opcional
        CPF = request.form['CPF']
        telefone = request.form['telefone']
        email = request.form['email']
        anos_experiencia = request.form.get('anos', '')  # Campo opcional

        # Localização
        foto_perfil = request.files['foto-perfil']
        foto_perfil_blob = foto_perfil.read()

        foto_capa = request.files['foto-capa']
        foto_capa_blob = foto_capa.read()

        cep = request.form['cep']
        rua = request.form['rua']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']
        complemento = request.form.get('complemento', '')  # Campo opcional

        # Sobre Mim
        descricao = request.form.get('descricao')

        # Redes Sociais
        instagram = request.form.get('instagram', '')  # Campo opcional
        facebook = request.form.get('facebook', '')  # Campo opcional
        whatsapp = request.form.get('whatsapp', '')  # Campo opcional
        tiktok = request.form.get('tiktok', '')  # Campo opcional

        # Aqui você faria o UPDATE no banco de dados
        cursor.execute("""
            UPDATE profissional SET 
                nome_completo = %s,
                nome_estabelecimento = %s,
                cpf = %s,
                telefone = %s,
                email = %s,
                anos_experiencia = %s,
                foto_perfil = %s,
                foto_capa = %s,
                cep = %s,
                rua = %s,
                bairro = %s,
                cidade = %s,
                estado = %s,
                complemento = %s,
                descricao_profissional = %s,
                instagram = %s,
                facebook = %s,
                whatsapp = %s,
                tiktok = %s
            WHERE id = %s
        """, (
            nome, estabelecimento, CPF, telefone, email, anos_experiencia,
            foto_perfil_blob,foto_capa_blob,
            cep, rua, bairro, cidade, estado, complemento, descricao,
            instagram, facebook, whatsapp, tiktok, profissional[0]
        ))

        banco.commit()
        flash("Profissional atualizado!")
        return redirect('/editarProfissional')
    return render_template("profissional/editar.html", profissional=profissional)


@bp.route('/gestao')
def gestao():
    profissional = getProfissional()
    cursor.execute("""
            SELECT id, profissional_id, nome, descricao, duracao_minutos, preco 
            FROM servico WHERE profissional_id = %s
        """, (profissional[0],))
    servicos = cursor.fetchall()
    return render_template('profissional/gestao.html', profissional=profissional, servicos=servicos)


@bp.route('/servicosProfissional', methods=['GET', 'POST'])
def servicosProfissional():
    profissional = getProfissional()
    if request.method == 'POST':
        servico_id = request.form.get('servicoId')
        nome = request.form['nomeServico']
        descricao = request.form['descricaoServico']
        duracao = request.form['duracaoServico']
        preco = request.form['precoServico']

        if servico_id:  # Se tem ID, é atualização
            cursor.execute("""
                    UPDATE servico 
                    SET nome = %s, descricao = %s, duracao_minutos = %s, preco = %s 
                    WHERE id = %s
                """, (nome, descricao, duracao, preco, servico_id))
            flash('Serviço atualizado com sucesso!')
        else:  # Se não tem ID, é criação
            cursor.execute("""
                    INSERT INTO servico (nome, descricao, duracao_minutos, preco, profissional_id) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome, descricao, duracao, preco, profissional[0]))
            flash('Serviço adicionado com sucesso!')
        banco.commit()
        return redirect('/servicosProfissional')
    cursor.execute("SELECT * FROM servico WHERE profissional_id = %s", (profissional[0],))
    servicos = cursor.fetchall()
    return render_template('profissional/servicos.html', profissional=profissional, servicos=servicos)


@bp.route("/delServico/<id>")
def delServico(id):
    cursor.execute("DELETE FROM servico WHERE id = %s", (id,))
    banco.commit()
    flash("Servico Excluido!")
    return redirect('/servicosProfissional')


@bp.route('/agendamentos')
def agendamentos():
    profissional = getProfissional()
    cursor.execute("SELECT * FROM disponibilidade_profissional WHERE profissional_id = %s", (profissional[0],))
    horariosDisponiveis = cursor.fetchall()
    return render_template('profissional/agendamentos.html', horariosDisponiveis=horariosDisponiveis)


def deletar_horarios_existentes(profissional_id):
    cursor.execute("DELETE FROM disponibilidade_profissional WHERE profissional_id = %s", (profissional_id,))
    banco.commit()


def salvar_horario(profissional_id, dia_semana, hora_inicio, hora_fim):
    cursor.execute(
        "INSERT INTO disponibilidade_profissional (profissional_id, dia_semana, hora_inicio, hora_fim) VALUES (%s, %s, %s, %s)",
        (profissional_id, dia_semana, hora_inicio, hora_fim))
    banco.commit()


@bp.route("/salvarHorarios", methods=['POST'])
def salvarHorarios():
    try:
        profissional = getProfissional()
        profissional_id = profissional[0]

        #limpar os horários existentes deste profissional
        deletar_horarios_existentes(profissional_id)
        dias_semana = {
            'domingo': 1,
            'segunda': 2,
            'terca': 3,
            'quarta': 4,
            'quinta': 5,
            'sexta': 6,
            'sabado': 7,

        }

        # Para cada dia da semana, verificar se está ativo e salvar os horários
        for dia_nome, dia_numero in dias_semana.items():
            dia_ativa = request.form.get(f'{dia_nome}_ativa')

            # Se o checkbox estiver marcado (value="true")
            if dia_ativa == 'true':
                hora_inicio = request.form.get(f'{dia_nome}_inicio')
                hora_fim = request.form.get(f'{dia_nome}_termino')

                # Validar se os horários foram preenchidos
                if hora_inicio and hora_fim:
                    # Inserir no banco de dados
                    salvar_horario(profissional_id, dia_numero, hora_inicio, hora_fim)

        flash("Horários atualizados!")
        return redirect('/agendamentos')

    except Exception as e:
        # Em caso de erro, retornar mensagem de erro
        flash(f"Erro: {e}")
        return redirect('/agendamentos')

@bp.route("/individual/<id>")
def individual(id):
    cursor.execute("SELECT * FROM profissional WHERE id = %s", (id,))
    profissional = cursor.fetchall()

    cursor.execute('SELECT * FROM disponibilidade_profissional')
    horarios_raw = cursor.fetchall()

    # Agrupar horários por profissional_id
    horarios_por_profissional = {}
    for horario in horarios_raw:
        prof_id = horario[1]  # profissional_id está na posição 1
        if prof_id not in horarios_por_profissional:
            horarios_por_profissional[prof_id] = []
        horarios_por_profissional[prof_id].append(horario)

    cursor.execute("SELECT * FROM servico WHERE profissional_id = %s", (profissional[0][0],))
    servicos = cursor.fetchall()

    return render_template("profissional/individual.html", profissional=profissional[0], horarios_por_profissional=horarios_por_profissional, servicos=servicos)