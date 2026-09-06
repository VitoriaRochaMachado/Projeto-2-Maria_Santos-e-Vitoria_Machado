import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify
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

if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)

