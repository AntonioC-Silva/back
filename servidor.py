import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import autenticacao
import filmes
import banco
from decimal import Decimal

class ConversorJsonCustomizado(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(ConversorJsonCustomizado, self).default(obj)

app = Flask(__name__, static_folder='../dist', static_url_path='/')
CORS(app) 

app.json_encoder = ConversorJsonCustomizado

@app.route('/api/login', methods=['POST'])
def rota_login():
    dados = request.get_json()
    resposta, status_code = autenticacao.logar_usuario(dados.get('usuario'), dados.get('senha'))
    return jsonify(resposta), status_code

@app.route('/api/registro', methods=['POST'])
def rota_registro():
    dados = request.get_json()
    resposta, status_code = autenticacao.registrar_usuario(dados.get('usuario'), dados.get('senha'))
    return jsonify(resposta), status_code

@app.route('/api/filmes', methods=['POST'])
def rota_adicionar_filme_pendente():
    dados = request.get_json()
    resposta, status_code = filmes.adicionar_filme_pendente(dados)
    return jsonify(resposta), status_code

@app.route('/api/filmes', methods=['GET'])
def rota_buscar_filmes_aprovados():
    resposta, status_code = filmes.buscar_filmes_aprovados()
    return jsonify(resposta), status_code

@app.route('/api/filmes/pendentes', methods=['GET'])
def rota_buscar_filmes_pendentes():
    resposta, status_code = filmes.buscar_filmes_pendentes()
    return jsonify(resposta), status_code

@app.route('/api/filmes/genero/<nome_genero>', methods=['GET'])
def rota_buscar_por_genero(nome_genero):
    resposta, status_code = filmes.buscar_filmes_por_genero(nome_genero)
    return jsonify(resposta), status_code

@app.route('/api/filmes/pesquisa', methods=['GET'])
def rota_pesquisar_filmes():
    termo = request.args.get('q', '') 
    resposta, status_code = filmes.buscar_filmes_por_titulo(termo)
    return jsonify(resposta), status_code

@app.route('/api/filme/remover/<int:id_filme>', methods=['DELETE'])
def rota_remover_filme(id_filme):
    resposta, status_code = filmes.remover_filme_aprovado(id_filme)
    return jsonify(resposta), status_code

@app.route('/api/filme-pendente/recusar/<int:id_pendente>', methods=['DELETE'])
def rota_recusar_filme(id_pendente):
    resposta, status_code = filmes.recusar_filme_pendente(id_pendente)
    return jsonify(resposta), status_code

@app.route('/api/filme/aprovar/<int:id_pendente>', methods=['POST'])
def rota_aprovar_filme(id_pendente):
    resposta, status_code = filmes.aprovar_filme_pendente(id_pendente)
    return jsonify(resposta), status_code

@app.route('/api/filme/<int:id_filme>', methods=['GET'])
def rota_buscar_filme_unico(id_filme):
    resposta, status_code = filmes.buscar_filme_por_id(id_filme)
    return jsonify(resposta), status_code

@app.route('/api/filme/<int:id_filme>', methods=['PUT'])
def rota_atualizar_filme(id_filme):
    dados = request.get_json()
    resposta, status_code = filmes.atualizar_filme(id_filme, dados)
    return jsonify(resposta), status_code

@app.route('/', defaults={'caminho': ''})
@app.route('/<path:caminho>')
def servir_frontend(caminho):
    if caminho != "" and os.path.exists(os.path.join(app.static_folder, caminho)):
        return send_from_directory(app.static_folder, caminho)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    if not os.path.exists('../dist'):
        os.makedirs('../dist')
        print("Pasta 'dist' criada. Lembre-se de rodar 'npm run build' no frontend.")
        
    print("Servidor rodando em http://localhost:8000")
    app.run(debug=True, port=8000)