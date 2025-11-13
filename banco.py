import mysql.connector
from decimal import Decimal
import json

CONFIG_BANCO = {
    'host': "localhost",
    'user': "root",
    'password': "senai", 
    'database': "webserver"
}

def conectar_banco():
    try:
        return mysql.connector.connect(**CONFIG_BANCO)
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco: {err}")
        return None

def executar_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    conexao = conectar_banco()
    if conexao is None:
        return None
        
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        
        if commit:
            conexao.commit()
            return cursor.lastrowid
            
        resultado = None
        if fetch_one:
            resultado = cursor.fetchone()
        elif fetch_all:
            resultado = cursor.fetchall()
            
        return resultado
        
    except mysql.connector.Error as err:
        print(f"Erro na query: {err}")
        conexao.rollback()
        return None
    finally:
        cursor.close()
        conexao.close()

def conversor_json(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(f"Objeto do tipo {o.__class__.__name__} não é serializável em JSON")