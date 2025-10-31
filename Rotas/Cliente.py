from flask import Flask, render_template, request, redirect, Blueprint

bp = Blueprint('Cliente', __name__)

@bp.route('/editarCliente', methods=['GET', 'POST'])
def editarCliente():
    if request.method == 'GET':
        #parei aq
        return render_template('cliente/edicao.html')

@bp.route('/servicos')
def servicos():
    return render_template('Cliente/servicos.html')

@bp.route('/profissionais')
def profissionais():
    return render_template('Cliente/profissionais.html')