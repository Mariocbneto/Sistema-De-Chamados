from flask import Flask, request, jsonify, render_template
import psycopg2

app = Flask(__name__)

DATABASE = "bancodedados"
USER = "postgres"
PASSWORD = "MarioNeto2005"
HOST = "localhost"
PORT = "5432"

def get_db_connection():
    return psycopg2.connect(
        database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT
    )

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM solicitacoes GROUP BY status")
        counts = cursor.fetchall()
        cursor.close()
        conn.close()

        # Inicializa com zero para cada status esperado
        status_counts = {'Aberto': 0, 'Analise': 0, 'Fechado': 0}

        for status, count in counts:
            # Tratar possíveis variações no nome do status
            st = status.lower()
            if st == 'aberto':
                status_counts['Aberto'] = count
            elif st == 'analise' or st == 'análise':
                status_counts['Analise'] = count
            elif st == 'fechado':
                status_counts['Fechado'] = count

        return render_template('index.html', **status_counts)
    except Exception as e:
        return f"Erro ao carregar página inicial: {e}", 500

@app.route('/enviar_solicitacao', methods=['POST'])
def enviar_solicitacao():
    data = request.get_json()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO solicitacoes (servico, titulo, descricao, telefone, atendido_por, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['servico'],
            data['titulo'],
            data['descricao'],
            data['telefone'],
            data['atendido_por'],
            'Aberto'
        ))
        conn.commit()
        return jsonify({'message': 'Solicitação enviada com sucesso!'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/listar_chamados')
def listar_chamados():
    status = request.args.get('status', 'Aberto')  # valor padrão
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, status, data_criacao, telefone, servico, atendido_por
            FROM solicitacoes
            WHERE status = %s
            ORDER BY data_criacao DESC
        """, (status,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('Botoes.html', chamados=rows, status=status)
    except Exception as e:
        return f"Erro ao listar chamados: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
