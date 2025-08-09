from flask import Flask, request, jsonify, render_template
import psycopg2

app = Flask(__name__)

DATABASE = "bancodedados"
USER = "postgres"
PASSWORD = "MarioNeto2005"
HOST = "localhost"
PORT = "5432"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar_solicitacao', methods=['POST'])
def enviar_solicitacao():
    data = request.get_json()
    try:
        conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO solicitacoes (servico, titulo, descricao, telefone, atendido_por)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['servico'], data['titulo'], data['descricao'], data['telefone'] , data['atendido_por']))
        conn.commit()
        return jsonify({'message': 'Solicitação enviada com sucesso!'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
