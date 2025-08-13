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

        status_counts = {'Aberto': 0, 'Analise': 0, 'Fechado': 0}
        for status, count in counts:
            st = status.lower()
            if st == 'aberto':
                status_counts['Aberto'] = count
            elif st in ['analise', 'análise']:
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
    status = request.args.get('status', 'Aberto')
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

@app.route('/chamado/<int:id_chamado>')
def ver_chamado(id_chamado):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, descricao, telefone, servico, atendido_por, status, data_criacao
            FROM solicitacoes
            WHERE id = %s
        """, (id_chamado,))
        chamado = cursor.fetchone()
        cursor.close()
        conn.close()

        if not chamado:
            return "Chamado não encontrado", 404

        return render_template('detalhe_chamado.html', chamado=chamado)
    except Exception as e:
        return f"Erro ao carregar detalhes do chamado: {e}", 500

@app.route('/atribuir/<int:id_chamado>', methods=['POST'])
def atribuir_chamado(id_chamado):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE solicitacoes
            SET status = 'Analise'
            WHERE id = %s
        """, (id_chamado,))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template("mensagem.html", mensagem="Chamado atribuído com sucesso!")
    except Exception as e:
        return f"Erro ao atribuir chamado: {e}", 500

@app.route('/detalhes_chamado/<int:id_chamado>')
def detalhes_chamado(id_chamado):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, descricao, status, data_criacao, telefone, servico, atendido_por
            FROM solicitacoes
            WHERE id = %s
        """, (id_chamado,))
        chamado = cursor.fetchone()
        cursor.close()
        conn.close()

        if chamado is None:
            return f"Chamado com ID {id_chamado} não encontrado.", 404

        return render_template('detalhes_chamado.html', chamado=chamado)
    except Exception as e:
        return f"Erro ao buscar detalhes do chamado: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
