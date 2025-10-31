from flask import Flask, render_template, send_file, send_from_directory, request, session, Blueprint
import psycopg2
import io

banco = psycopg2.connect(host='localhost',
                         dbname='AgendeJa',
                         user='postgres',
                         password='senai')
cursor = banco.cursor()

bp = Blueprint('Profissional', __name__)

@bp.route('/gestao')
def gestao():
    return render_template('profissional/gestao.html')