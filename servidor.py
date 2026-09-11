import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request, url_for
import os

load_dotenv()

app = Flask(__name__)
def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        with open("imoveis.sql", encoding="utf-8") as arquivo:
            comandos_sql = arquivo.read()

        cursor.execute(comandos_sql)

        # Processa todos os comandos/resultados do arquivo SQL
        while True:
            if cursor.with_rows:
                cursor.fetchall()

            if not cursor.nextset():
                break

        conn.commit()
        print("Tabelas criadas com sucesso.")

    except mysql.connector.Error as erro:
        conn.rollback()
        print(f"Erro ao criar as tabelas: {erro}")

    finally:
        cursor.close()
        conn.close()
        
@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM imoveis")

        imoveis = cursor.fetchall()

        return jsonify(imoveis), 200

    except mysql.connector.Error:
        return jsonify({
            "erro": "Erro ao consultar os imóveis"
        }), 500

    finally:
        cursor.close()
        conn.close()

@app.route("/imoveis/<int:id>", methods=["GET"])
def buscar_imovel(id):
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM imoveis WHERE id = %s",
        (id,)
    )

    imovel = cursor.fetchone()

    cursor.close()
    conn.close()

    if imovel is None:
        return jsonify({
            "erro": "Imóvel não encontrado"
        }), 404

    return jsonify(imovel), 200

CAMPOS_IMOVEL = [
    "logradouro",
    "tipo_logradouro",
    "bairro",
    "cidade",
    "cep",
    "tipo",
    "valor",
    "data_aquisicao"
]

@app.route("/imoveis", methods=["POST"])
def adicionar_imovel():
    dados = request.get_json()

    if dados is None:
        return jsonify({
            "erro": "É necessário enviar um JSON"
        }), 400

    campos_faltando = []

    for campo in CAMPOS_IMOVEL:
        if campo not in dados:
            campos_faltando.append(campo)

    if campos_faltando:
        return jsonify({
            "erro": "Campos faltando",
            "campos": campos_faltando
        }), 400

    conn = conectar_banco()
    cursor = conn.cursor()

    comando = """
        INSERT INTO imoveis (
            logradouro,
            tipo_logradouro,
            bairro,
            cidade,
            cep,
            tipo,
            valor,
            data_aquisicao
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        dados["logradouro"],
        dados["tipo_logradouro"],
        dados["bairro"],
        dados["cidade"],
        dados["cep"],
        dados["tipo"],
        dados["valor"],
        dados["data_aquisicao"]
    )

    cursor.execute(comando, valores)
    conn.commit()

    novo_id = cursor.lastrowid

    cursor.close()
    conn.close()

    resposta = {
        "id": novo_id,
        "logradouro": dados["logradouro"],
        "tipo_logradouro": dados["tipo_logradouro"],
        "bairro": dados["bairro"],
        "cidade": dados["cidade"],
        "cep": dados["cep"],
        "tipo": dados["tipo"],
        "valor": dados["valor"],
        "data_aquisicao": dados["data_aquisicao"]
    }

    return jsonify(resposta), 201

@app.route('/imovel/<id>', methods=['DELETE'])
def deletar_imovel(id):
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM imoveis WHERE id = %s", (int(id),))

        imovel_alterado = cursor.rowcount
        conn.commit()
        
        if imovel_alterado == 0:
            return jsonify({"erro": "Imóvel não encontrado"}), 404

        return jsonify({"Mensagem":"imóvel excluído com sucesso"}), 200
    
    finally:
        cursor.close()
        conn.close()

@app.route('/imovel/<tipo>', methods=['GET'])
def busca_tipo(tipo):
    conn = conectar_banco()
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE tipo = %s", (tipo,))
        imoveis = cursor.fetchall()
        lista_imoveis =[]

        for imovel in imoveis:
            lista_imoveis.append({
                'id':imovel[0],
                'logradouro': imovel[1],
                'tipo_logradouro': imovel[2],
                'bairro': imovel[3],
                'cidade': imovel[4],
                'cep': imovel[5],
                'tipo': imovel[6],
                'valor': imovel[7],
                'data_aquisicao': imovel[8]
            })
        return jsonify(lista_imoveis), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/imovel/<cidade>')
def busca_cidade(cidade):
    conn = conectar_banco()
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s", (cidade,))
        imoveis = cursor.fetchall()
        lista_imoveis =[]

        for imovel in imoveis:
            lista_imoveis.append({
                'id':imovel[0],
                'logradouro': imovel[1],
                'tipo_logradouro': imovel[2],
                'bairro': imovel[3],
                'cidade': imovel[4],
                'cep': imovel[5],
                'tipo': imovel[6],
                'valor': imovel[7],
                'data_aquisicao': imovel[8]
            })
        return jsonify(lista_imoveis), 200
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)

