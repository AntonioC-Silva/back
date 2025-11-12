from werkzeug.security import generate_password_hash, check_password_hash
import banco

def registrar_usuario(usuario, senha):
    if not usuario or not senha:
        return {"sucesso": False, "erro": "Usuário e senha são obrigatórios"}, 400
    
    query_verificacao = "SELECT * FROM usuario WHERE nome = %s"
    if banco.executar_query(query_verificacao, (usuario,), fetch_one=True):
        return {"sucesso": False, "erro": "Usuário já existe"}, 409
        
    senha_hash = generate_password_hash(senha)
    
    query_insercao = "INSERT INTO usuario (nome, senha) VALUES (%s, %s)"
    id_usuario = banco.executar_query(query_insercao, (usuario, senha_hash), commit=True)
    
    if id_usuario:
        return {"sucesso": True, "id_usuario": id_usuario}, 201
    else:
        return {"sucesso": False, "erro": "Erro ao registrar usuário"}, 500

def logar_usuario(usuario, senha):
    if not usuario or not senha:
        return {"sucesso": False, "erro": "Usuário e senha são obrigatórios"}, 400
        
    query = "SELECT * FROM usuario WHERE nome = %s"
    usuario_db = banco.executar_query(query, (usuario,), fetch_one=True)
    
    if usuario_db and check_password_hash(usuario_db['senha'], senha):
        return {
            "sucesso": True, 
            "usuario": {
                "id": usuario_db['id_usuario'], 
                "nome": usuario_db['nome']
            }
        }, 200
    else:
        return {"sucesso": False, "erro": "Usuário ou senha inválidos"}, 401