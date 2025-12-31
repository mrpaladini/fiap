
# Importando as Bibliotecas que serão utilizadas


import pandas as pd
import csv
import time
from sqlalchemy import create_engine
from sqlalchemy import text
from flask import Flask
from flask import Flask, jsonify, request
import requests

pd.set_option('display.max_colwidth', None)

def get_db():

    # Conectando no Banco de Dados MySQL
    # variavaies do banco
    usuario = 'root'
    senha = "Password"
    host = '10.0.2.15'
    banco_de_dados = 'books' 
    tabela = 'books_final'
    # conectando
    engine = create_engine(f'mysql+mysqlconnector://{usuario}:{senha}@{host}/{banco_de_dados}')

    # Pesquisa para listar todos os livros
    # GET /api/v1/books: lista todos os livros disponíveis na base de dados.

    query = text("SELECT * FROM books_final")
    
    df_livro = pd.read_sql(query, con=engine)
        
    if not df_livro.empty:
        # print(df_livro)
        return df_livro
    else:
        return None

app = Flask(__name__)
@app.route('/')
def home():
    return "Você precisa de um endpoint valido para acessar esta API"


# items = []

@app.route('//api/v1/books',methods=['GET'])
def list_books():
    df = get_db()
    if df is None: return jsonify({"error": "Base de dados não encontrada"}), 500
    return jsonify(df.to_dict(orient='records')), 200

# Pesquisa para buscar por um livro especifico pelo ID

# GET /api/v1/books/{id}: retorna detalhes completos de um livro específico pelo ID.
# ID que você deseja buscar (parâmetro vindo do usuário ou variável)

@app.route('/api/v1/books/<int:book_id>',methods=['GET'])
def get_book(book_id):
    df = get_db()
    if book_id in df.index:
        return jsonify(df.loc[book_id].to_dict()), 200
    return jsonify({"error": "Livro inexistente"}), 404
    
    if df is None: return jsonify({"error": "Base de dados não encontrada"}), 500
    return jsonify(df.to_dict(orient='records')), 200


# Pesquisa buscando por titulo ou categoria
# GET /api/v1/books/search?title={title}&category={category}: busca livros por título e/ou categoria.

# Exemplo

# Book ID:  5
# Titulo:  The Requiem Red
# Categoria:  Young Adult
# Pontuação:  One
# Preço:   22.65
# Disponibilidade:  In stock (19 available)

# http://127.0.0.1:5000/api/v1/books/search?title=The Requiem Red&category=Young Adult

@app.route('/api/v1/books/search',methods=['GET'])
def serch_book():
    df = get_db()
    title = request.args.get('title')
    category = request.args.get('category')

    results = df

    if title:
        results = results[results['Title'].str.contains(title, case=False, na=False)]
    if category:
        results = results[results['Category'].str.contains(category, case=False, na=False)]
        
    return jsonify(results.to_dict(orient='records')), 200

# Lista todas as categorias
# GET /api/v1/categories: lista todas as categorias de livros disponíveis.

@app.route('//api/v1/categories',methods=['GET'])
def list_categoty():
    df = get_db()
    categories = df['Category'].unique().tolist()
    return jsonify({"categories": categories}), 200


# Verificar a saude da aplicação
#  GET /api/v1/health: Verifica status da API e conectividade [2]
@app.route('/api/v1/health', methods=['GET'])

def health():
    # Verificação do Banco de Dados SQL
    # Tenta realizar uma conexão simples para validar o status
    
    try:
        # Tenta conectar e executar uma consulta mínima

        # Conectando no Banco de Dados MySQL
        # variavaies do banco
        usuario = 'root'
        senha = "Password"
        host = '10.0.2.15'
        banco_de_dados = 'books' 
        tabela = 'books_final'
        # conectando
        engine = create_engine(f'mysql+mysqlconnector://{usuario}:{senha}@{host}/{banco_de_dados}')
        
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_status = "conectado"
    
    except Exception as e:
        # db_status = f"erro de conexão: {str(e)}"
        db_status = f"erro de conexão com banco de dados"

       # Verifica se o site de origem está acessível (Status 200)
    
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        
        if response.status_code == 200:
            portal_status = "Portal esta online"
        else:
            portal_status = f"indisponível (Status {response.status_code})"
    except Exception:
        portal_status = "Offline/erro de rede"

    # Resposta Consolidada
    # Retorna o status de ambos os componentes

    return jsonify({
        "status_api": "online",
        "database_sql": db_status,
        "portal_origem": portal_status
           
    }), 200 if db_status == "conectado" else 500


if __name__ == '__main__':
    app.run(debug=True)