import banco
import time
import random
import datetime

def segundos_para_tempo_str(segundos):
    if not isinstance(segundos, int):
        try:
            segundos = int(segundos)
        except (ValueError, TypeError):
            return "00:00:00"
            
    return time.strftime('%H:%M:%S', time.gmtime(segundos))

def buscar_ou_criar_id(cursor, tabela, valor_nome, sobrenome=''):
    if tabela == 'ator':
        query = f"select id_ator from ator where nome = %s and sobrenome = %s"
        cursor.execute(query, (valor_nome, sobrenome))
        resultado = cursor.fetchone()
        if resultado:
            return resultado['id_ator']
        else:
            query_insert = "insert into ator (nome, sobrenome) values (%s, %s)"
            cursor.execute(query_insert, (valor_nome, sobrenome))
            return cursor.lastrowid
    
    elif tabela == 'genero':
        query = f"select id_genero from genero where tipo = %s"
        cursor.execute(query, (valor_nome,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado['id_genero']
        else:
            query_insert = "insert into genero (tipo) values (%s)"
            cursor.execute(query_insert, (valor_nome,))
            return cursor.lastrowid
            
    elif tabela == 'diretor':
        partes = valor_nome.split(' ', 1)
        nome = partes[0]
        sobrenome = partes[1] if len(partes) > 1 else ''
        query = "select id_diretor from diretor where nome = %s and sobrenome = %s"
        cursor.execute(query, (nome, sobrenome))
        resultado = cursor.fetchone()
        if resultado:
            return resultado['id_diretor']
        else:
            query_insert = "insert into diretor (nome, sobrenome) values (%s, %s)"
            cursor.execute(query_insert, (nome, sobrenome))
            return cursor.lastrowid
    return None

def adicionar_filme_pendente(dados):
    try:
        sql = """
            insert into filme_pendente 
            (titulo, orcamento, diretor_nome, tempo_de_duracao, ano, poster, sinopse, elenco_string, genero_string)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            dados.get('titulo'),
            dados.get('orcamento'),
            dados.get('nomeDiretor'),
            dados.get('tempoDeDuracao'),
            dados.get('ano'),
            dados.get('poster'),
            dados.get('sinopse'),
            dados.get('elenco'),
            dados.get('genero')
        )
        
        filme_id = banco.executar_query(sql, valores, commit=True)
        
        if filme_id:
            return {"sucesso": True, "id_pendente": filme_id}, 201
        else:
            return {"sucesso": False, "erro": "falha ao inserir filme pendente"}, 500

    except Exception as e:
        print(f"Erro em adicionar_filme_pendente: {e}")
        return {"sucesso": False, "erro": str(e)}, 400

def buscar_filmes_aprovados():
    query = """
        select 
            f.id_filme, f.titulo, f.poster, f.ano, f.sinopse, f.elenco,
            d.nome as diretor_nome, d.sobrenome as diretor_sobrenome,
            group_concat(distinct g.tipo separator ', ') as generos
        from filme f
        left join diretor d on f.id_diretor = d.id_diretor
        left join filme_genero fg on f.id_filme = fg.id_filme
        left join genero g on fg.id_genero = g.id_genero
        group by f.id_filme
        order by f.id_filme desc
    """
    filmes = banco.executar_query(query, fetch_all=True)
    
    if filmes is not None:
        return {"sucesso": True, "filmes": filmes}, 200
    else:
        return {"sucesso": False, "erro": "não foi possível buscar os filmes"}, 500

def buscar_filmes_pendentes():
    query = "select * from filme_pendente order by id_pendente asc"
    filmes = banco.executar_query(query, fetch_all=True)
    if filmes is not None:
        return {"sucesso": True, "filmes": filmes}, 200
    else:
        return {"sucesso": False, "erro": "não foi possível buscar os filmes pendentes"}, 500

def buscar_filmes_por_genero(nome_genero):
    query = """
        select 
            f.id_filme, f.titulo, f.poster, f.ano, f.sinopse,
            group_concat(distinct g.tipo separator ', ') as generos
        from filme f
        inner join filme_genero fg on f.id_filme = fg.id_filme
        inner join genero g on fg.id_genero = g.id_genero
        where g.tipo = %s
        group by f.id_filme
        order by rand()
        limit 10
    """
    filmes = banco.executar_query(query, (nome_genero,), fetch_all=True)
    
    if filmes is not None:
        return {"sucesso": True, "filmes": filmes}, 200
    else:
        return {"sucesso": False, "erro": "não foi possível buscar os filmes por genero"}, 500

def buscar_filmes_por_titulo(termo_busca):
    if not termo_busca:
        return {"sucesso": True, "filmes": []}, 200
    query = "select id_filme, titulo, poster, ano from filme where titulo like %s"
    parametro_busca = f"%{termo_busca}%"
    filmes = banco.executar_query(query, (parametro_busca,), fetch_all=True)
    if filmes is not None:
        return {"sucesso": True, "filmes": filmes}, 200
    else:
        return {"sucesso": False, "erro": "erro ao realizar a busca"}, 500

def recusar_filme_pendente(id_pendente):
    query = "delete from filme_pendente where id_pendente = %s"
    banco.executar_query(query, (id_pendente,), commit=True)
    return {"sucesso": True, "mensagem": "filme recusado com sucesso"}, 200

def remover_filme_aprovado(id_filme):
    query = "delete from filme where id_filme = %s"
    banco.executar_query(query, (id_filme,), commit=True)
    return {"sucesso": True, "mensagem": "filme removido com sucesso"}, 200

def aprovar_filme_pendente(id_pendente):
    conexao = banco.conectar_banco()
    if conexao is None:
        return {"sucesso": False, "erro": "falha na conexao com banco"}, 500
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("select * from filme_pendente where id_pendente = %s", (id_pendente,))
        filme_pendente = cursor.fetchone()
        if not filme_pendente:
            return {"sucesso": False, "erro": "filme pendente não encontrado"}, 404

        tempo_de_duracao_str = segundos_para_tempo_str(filme_pendente['tempo_de_duracao'])
        id_diretor = buscar_ou_criar_id(cursor, 'diretor', filme_pendente['diretor_nome'])

        sql_filme = """
            insert into filme (titulo, orcamento, id_diretor, tempo_de_duracao, ano, poster, sinopse, elenco)
            values (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores_filme = (
            filme_pendente['titulo'], filme_pendente['orcamento'], id_diretor,
            tempo_de_duracao_str, filme_pendente['ano'], filme_pendente['poster'],
            filme_pendente['sinopse'], filme_pendente['elenco_string']
        )
        cursor.execute(sql_filme, valores_filme)
        id_filme_novo = cursor.lastrowid

        generos_lista = [g.strip() for g in filme_pendente['genero_string'].split(',')]
        for nome_genero in generos_lista:
            if nome_genero:
                id_genero = buscar_ou_criar_id(cursor, 'genero', nome_genero)
                if id_genero:
                    cursor.execute("insert into filme_genero (id_filme, id_genero) values (%s, %s)", (id_filme_novo, id_genero))

        elenco_lista = [a.strip() for a in filme_pendente['elenco_string'].split(',')]
        for nome_completo in elenco_lista:
            if nome_completo:
                partes = nome_completo.split(' ', 1)
                nome = partes[0]
                sobrenome = partes[1] if len(partes) > 1 else ''
                id_ator = buscar_ou_criar_id(cursor, 'ator', nome, sobrenome)
                if id_ator:
                    cursor.execute("insert into filme_ator (id_filme, id_ator) values (%s, %s)", (id_filme_novo, id_ator))

        cursor.execute("delete from filme_pendente where id_pendente = %s", (id_pendente,))
        
        conexao.commit()
        return {"sucesso": True, "id_filme_novo": id_filme_novo}, 201

    except Exception as e:
        conexao.rollback()
        print(f"Erro em aprovar_filme_pendente: {e}")
        return {"sucesso": False, "erro": str(e)}, 500
    finally:
        cursor.close()
        conexao.close()

def buscar_filme_por_id(id_filme):
    query = """
        SELECT 
            f.id_filme, f.titulo, f.orcamento, f.tempo_de_duracao, f.ano, f.poster, f.sinopse, f.elenco,
            CONCAT(d.nome, ' ', d.sobrenome) as diretor_nome,
            GROUP_CONCAT(DISTINCT g.tipo SEPARATOR ', ') as generos
        FROM filme f
        LEFT JOIN diretor d ON f.id_diretor = d.id_diretor
        LEFT JOIN filme_genero fg ON f.id_filme = fg.id_filme
        LEFT JOIN genero g ON fg.id_genero = g.id_genero
        WHERE f.id_filme = %s
        GROUP BY f.id_filme
    """
    filme = banco.executar_query(query, (id_filme,), fetch_one=True)
    if filme:
        if isinstance(filme.get('tempo_de_duracao'), datetime.timedelta):
            total_seg = int(filme['tempo_de_duracao'].total_seconds())
            filme['tempo_de_duracao'] = f"{total_seg // 3600:02d}:{(total_seg % 3600) // 60:02d}:{total_seg % 60:02d}"
        
        return {"sucesso": True, "filme": filme}, 200
    else:
        return {"sucesso": False, "erro": "Filme não encontrado"}, 404

def atualizar_filme(id_filme, dados):
    try:
        query = """
            UPDATE filme 
            SET 
                titulo = %s, 
                sinopse = %s, 
                elenco = %s, 
                poster = %s, 
                ano = %s
            WHERE id_filme = %s
        """
        valores = (
            dados.get('titulo'),
            dados.get('sinopse'),
            dados.get('elenco'),
            dados.get('poster'),
            dados.get('ano'),
            id_filme
        )
        banco.executar_query(query, valores, commit=True)
        return {"sucesso": True, "mensagem": "Filme atualizado com sucesso"}, 200
    except Exception as e:
        print(f"Erro em atualizar_filme: {e}")
        return {"sucesso": False, "erro": str(e)}, 500