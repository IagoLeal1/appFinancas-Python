from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# Criação do banco na primeira execução
def init_db():
    with sqlite3.connect("financas.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,              -- Receita ou Despesa
                valor REAL NOT NULL,
                categoria TEXT NOT NULL
            )
        ''')
        conn.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tipo = request.form['tipo']
        valor = float(request.form['valor'])
        categoria = request.form['categoria']

        with sqlite3.connect("financas.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transacoes (tipo, valor, categoria) VALUES (?, ?, ?)", (tipo, valor, categoria))
            conn.commit()
        return redirect('/resultados')

    return render_template('index.html')


@app.route('/resultados')
def resultados():
    with sqlite3.connect("financas.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, valor, categoria FROM transacoes")
        transacoes = cursor.fetchall()

    receitas = [t for t in transacoes if t[0] == "Receita"]
    despesas = [t for t in transacoes if t[0] == "Despesa"]

    total_receitas = sum(t[1] for t in receitas)
    total_despesas = sum(t[1] for t in despesas)
    saldo = total_receitas - total_despesas

    # Agrupamento de despesas por categoria
    categorias = {}
    for t in despesas:
        cat = t[2]
        categorias[cat] = categorias.get(cat, 0) + t[1]

    return render_template(
        'resultados.html',
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        saldo=saldo,
        categorias=categorias
    )


@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []

    if request.method == 'POST':
        categoria = request.form['categoria']
        with sqlite3.connect("financas.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tipo, valor FROM transacoes WHERE categoria = ?", (categoria,))
            resultados = cursor.fetchall()

    return render_template('buscar.html', resultados=resultados)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
