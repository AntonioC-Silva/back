import banco
import time

def segundos_para_tempo_str(segundos):
    if not isinstance(segundos, int):
        try:
            segundos = int(segundos)
        except (ValueError, TypeError):
            return "00:00:00"
            
    return time.strftime('%H:%M:%S', time.gmtime(segundos))

def adicionar_filme(dados):
    try:
        titulo = dados.get('titulo')
        orcamento = dados.get('orcamento')
        diretor = dados.get('nomeDiretor') 
        duracao_segundos = dados.get('tempoDeDuracao')
        ano = dados.get('ano')
        elenco = dados.get('elenco') 
        generos = dados.get('genero') 
        produtora = dados.get('nomeProdutora') 
        poster_url = dados.get('poster')
        sinopse = dados.get('sinopse')

        tempo_de_duracao = segundos_para_tempo_str(duracao_segundos)

        sql = """
            INSERT INTO filme 
            (titulo, orcamento, tempo_de_duracao, ano, poster, sinopse, diretor, genero, produtora, atores)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (
            titulo, orcamento, tempo_de_duracao, ano, poster_url, sinopse,
            diretor, generos, produtora, elenco
        )
        
        filme_id = banco.executar_query(sql, valores, commit=True)
        
        if filme_id:
            return {"sucesso": True, "id_filme": filme_id}, 201
        else:
            return {"sucesso": False, "erro": "Falha ao inserir filme no banco"}, 500

    except Exception as e:
        print(f"Erro em adicionar_filme: {e}")
        return {"sucesso": False, "erro": str(e)}, 400

def buscar_todos_filmes():
    query = "SELECT id_filme, titulo, poster, ano, genero, diretor, sinopse FROM filme"
    filmes = banco.executar_query(query, fetch_all=True)
    
    if filmes is not None:
        return {"sucesso": True, "filmes": filmes}, 200
    else:
        return {"sucesso": False, "erro": "Não foi possível buscar os filmes"}, 500

def buscar_filmes_por_titulo(termo_busca):
    if not termo_busca:
        return {"sucesso": True, "filmes": []}, 200
        
    query = "SELECT id_filme, titulo, poster, ano FROM filme WHERE titulo LIKE %s"
    parametro_busca = f"%{termo_busca}%"
    
    filmes = banco.executar_query(query, (parametro_busca,), fetch_all=True)
    
    if filmes is not None:
        return {"sucesso": True, "filmes": filmes}, 200
    else:
        return {"sucesso": False, "erro": "Erro ao realizar a busca"}, 500