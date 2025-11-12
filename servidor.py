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
    if not dados:
        return jsonify({"sucesso": False, "erro": "JSON inválido"}), 400
    resposta, status_code = autenticacao.logar_usuario(dados.get('usuario'), dados.get('senha'))
    return jsonify(resposta), status_code

@app.route('/api/registro', methods=['POST'])
def rota_registro():
    dados = request.get_json()
    if not dados:
        return jsonify({"sucesso": False, "erro": "JSON inválido"}), 400
    resposta, status_code = autenticacao.registrar_usuario(dados.get('usuario'), dados.get('senha'))
    return jsonify(resposta), status_code

@app.route('/api/filmes', methods=['POST'])
def rota_adicionar_filme():
    dados = request.get_json()
    if not dados:
        return jsonify({"sucesso": False, "erro": "JSON inválido"}), 400
    resposta, status_code = filmes.adicionar_filme(dados)
    return jsonify(resposta), status_code

@app.route('/api/filmes', methods=['GET'])
def rota_buscar_filmes():
    resposta, status_code = filmes.buscar_todos_filmes()
    return jsonify(resposta), status_code

@app.route('/api/filmes/pesquisa', methods=['GET'])
def rota_pesquisar_filmes():
    termo = request.args.get('q', '') 
    resposta, status_code = filmes.buscar_filmes_por_titulo(termo)
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