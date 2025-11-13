from werkzeug.security import generate_password_hash, check_password_hash
import banco

def registrar_usuario(usuario, senha):
    if not usuario or not senha:
        return {"sucesso": False, "erro": "usuário e senha são obrigatórios"}, 400
    
    query_verificacao = "select * from usuario where nome = %s"
    if banco.executar_query(query_verificacao, (usuario,), fetch_one=True):
        return {"sucesso": False, "erro": "usuário já existe"}, 409
        
    senha_hash = generate_password_hash(senha)
    
    query_insercao = "insert into usuario (nome, senha) values (%s, %s)"
    id_usuario = banco.executar_query(query_insercao, (usuario, senha_hash), commit=True)
    
    if id_usuario:
        return {"sucesso": True, "id_usuario": id_usuario}, 201
    else:
        return {"sucesso": False, "erro": "erro ao registrar usuário"}, 500

def logar_usuario(usuario, senha):
    if not usuario or not senha:
        return {"sucesso": False, "erro": "usuário e senha são obrigatórios"}, 400
        
    query_usuario = "select * from usuario where nome = %s"
    usuario_comum = banco.executar_query(query_usuario, (usuario,), fetch_one=True)
    
    if usuario_comum and check_password_hash(usuario_comum['senha'], senha):
        return {
            "sucesso": True, 
            "usuario": {
                "id": usuario_comum['id_usuario'], 
                "nome": usuario_comum['nome']
            },
            "tipo": "comum"
        }, 200

    query_adm = "select * from adm where nome = %s"
    usuario_adm = banco.executar_query(query_adm, (usuario,), fetch_one=True)
    
    if usuario_adm and usuario_adm['senha'] == senha:
        return {
            "sucesso": True, 
            "usuario": {
                "id": usuario_adm['id_adm'], 
                "nome": usuario_adm['nome']
            },
            "tipo": "adm"
        }, 200
    
    return {"sucesso": False, "erro": "usuário ou senha inválidos"}, 401