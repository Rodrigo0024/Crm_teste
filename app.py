import secrets #A biblioteca secrets é usada para gerar números, tokens e senhas criptograficamente seguros em Pyth
from flask import Flask, render_template, request, redirect, url_for, flash #importando funções do flask
from flask_mysqldb import MySQL


# Configuração inicial do Flask
app = Flask(__name__)
chave_secreta = secrets.token_hex(32)#gera uma string hexadecimal aleatória e segura criptograficamente.



# Configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Altere para o seu usuário MySQL
app.config['MYSQL_PASSWORD'] = 'geladeira12'  # Altere para a sua senha MySQL
app.config['MYSQL_DB'] = 'crm_db'
app.secret_key = chave_secreta


mysql = MySQL(app)


# Rota principal - Lista de clientes
@app.route('/')
def index():
    cur = mysql.connection.cursor() #cria um objeto "cursor" a partir da conexão com o banco de dados MySQL
    cur.execute("SELECT * FROM clients") #seleciona tudo da tabela clients
    clients = cur.fetchall() # O método `.fetchall()` retorna uma lista de tuplas, onde cada tupla representa uma linha do resultado da consulta.
    cur.close()#fecha o cursor
    return render_template('index.html', clients=clients)#A linha acima renderiza um template HTML chamado 'index.html' e passa os dados armazenados na variável `clients` para o template.

# Adicionar cliente
@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST': #se o metodo for igual a post
        name = request.form['name']# está recebendo os dados do formulario nome
        email = request.form['email']#recebendo os dados do formulario email
        phone = request.form['phone']#recebendo os dados do formulario email
        address = request.form['address']#recebendo os dados do formulario endereço
        informacoes = request.form['adicionais']

        cur = mysql.connection.cursor() #cria um cursor
        cur.execute(
            "INSERT INTO clients (name, email, phone, address, adicionais) VALUES (%s, %s, %s, %s, %s)",
            (name, email, phone, address, informacoes)
        )#insere novos registros na tabela clientes
        mysql.connection.commit()#confirma as alterações feitas no banco de dados
        cur.close()

        flash('Cliente adicionado com sucesso!', 'success') #exibe uma mensagem 
        return redirect(url_for('index'))#redireciona o usuario para a rota associada a função index
    return render_template('add_client.html') #renderiza o template add_cliente

# Editar cliente
@app.route('/edit_client/<int:id>', methods=['GET', 'POST']) # Essa rota aceita um parâmetro dinâmico `id` (um número inteiro)
def edit_client(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        informacoes = request.form['adicionais']

        cur.execute(
            "UPDATE clients SET name=%s, email=%s, phone=%s, address=%s, adicionais=%s WHERE id=%s",
            (name, email, phone, address, informacoes, id)
        )
        mysql.connection.commit()
        cur.close()

        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM clients WHERE id=%s", (id,))
    client = cur.fetchone()# O método `.fetchone()` retorna uma única tupla contendo os valores da linh
    cur.close()
    return render_template('edit_client.html', client=client)

# Excluir cliente
@app.route('/delete_client/<int:id>')
def delete_client(id):
    cur = mysql.connection.cursor()
      # Remove todos os registros na tabela sales_pipeline associados ao cliente
    cur.execute("DELETE FROM sales_pipeline WHERE client_id=%s", (id,))
    mysql.connection.commit()
    cur.execute("DELETE FROM clients WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Cliente excluído com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_pipeline/<int:id>', methods=['POST'])
def delete_pipeline(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sales_pipeline WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Item do pipeline excluído com sucesso!', 'success')
    return redirect(url_for('pipeline'))
# Pipeline de vendas
@app.route('/pipeline')
def pipeline():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sales_pipeline")
    pipeline = cur.fetchall()
    cur.close()
    return render_template('pipeline.html', pipeline=pipeline)

# Adicionar item ao pipeline
@app.route('/add_pipeline', methods=['GET', 'POST'])
def add_pipeline():
        # Recupera a lista de clientes para preencher o menu suspenso
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM clients")
    clients = cur.fetchall()
    if request.method == 'POST':
        client_id = request.form['client_id']
        stage = request.form['stage']
        value = request.form['value']
        probability = request.form['probability']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO sales_pipeline (client_id, stage, value, probability) VALUES (%s, %s, %s, %s)",
            (client_id, stage, value, probability)
        )
        mysql.connection.commit()
        cur.close()

        flash('Item adicionado ao pipeline!', 'success')
        return redirect(url_for('pipeline'))

    return render_template('add_pipeline.html', clients=clients)
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO projects (title, start_date, end_date, status) VALUES (%s, %s, %s, %s)",
            (title, start_date, end_date, status)
        )
        mysql.connection.commit()
        cur.close()

        flash('Projeto adicionado com sucesso!', 'success')
        return redirect(url_for('projects'))

    return render_template('add_project.html')
@app.route('/edit_pipeline/<int:id>', methods=['GET', 'POST'])
def edit_pipeline(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        client_id = request.form.get('client_id', '')
        stage = request.form.get('stage', '')
        value = request.form.get('value', 0.0)
        probability = request.form.get('probability', 0)

        # Validação básica (opcional)
        if not client_id or not stage or not value or not probability:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('edit_pipeline', id=id))

        # Atualize os dados do pipeline
        cur.execute(
            "UPDATE sales_pipeline SET client_id=%s, stage=%s, value=%s, probability=%s WHERE id=%s",
            (client_id, stage, value, probability, id)
        )
        mysql.connection.commit()
        cur.close()

        flash('Item do pipeline atualizado com sucesso!', 'success')
        return redirect(url_for('pipeline'))

    # Recupera o item do pipeline para edição
    cur.execute("""
        SELECT sp.id, c.name, sp.stage, sp.value, sp.probability
        FROM sales_pipeline sp
        JOIN clients c ON sp.client_id = c.id
        WHERE sp.id = %s
    """, (id,))
    pipeline_item = cur.fetchone()

    # Recupera a lista de clientes para preencher o menu suspenso
    cur.execute("SELECT id, name FROM clients")
    clients = cur.fetchall()
    cur.close()

    return render_template('edit_pipeline.html', pipeline_item=pipeline_item, clients=clients)
# Projetos
@app.route('/projects')
def projects():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.close()
    return render_template('projects.html', projects=projects)
@app.route('/delete_project/<int:id>', methods=['POST'])
def delete_project(id):
    cur = mysql.connection.cursor()

    # Remove todos os registros na tabela messages associados ao projeto
    cur.execute("DELETE FROM messages WHERE project_id=%s", (id,))
    mysql.connection.commit()

    # Agora, pode excluir o projeto
    cur.execute("DELETE FROM projects WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('projects'))

@app.route('/edit_project/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']

        cur.execute(
            "UPDATE projects SET title=%s, start_date=%s, end_date=%s, status=%s WHERE id=%s",
            (title, start_date, end_date, status, id)
        )
        mysql.connection.commit()
        cur.close()

        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('projects'))

    cur.execute("SELECT * FROM projects WHERE id=%s", (id,))
    project = cur.fetchone()
    cur.close()

    return render_template('edit_project.html', project=project)
# Mensagens (comunicação em equipe)
@app.route('/messages')
def messages():
    cur = mysql.connection.cursor()

    # Recupera as mensagens com o nome do projeto
    cur.execute("""
        SELECT m.id, p.title AS project_title, m.content, m.timestamp
        FROM messages m
        JOIN projects p ON m.project_id = p.id
        ORDER BY m.timestamp DESC
    """)
    messages = cur.fetchall()

    # Recupera a lista de projetos para o menu suspenso
    cur.execute("SELECT id, title FROM projects")
    projects = cur.fetchall()
    cur.close()

    # Exiba os dados no terminal para depuração
    print("Projetos:", projects)

    return render_template('messages.html', messages=messages, projects=projects)
@app.route('/add_message', methods=['POST'])
def add_message():
 
    # Obtém os dados do formulário
    content = request.form['content']
    project_id = request.form['project_id']

    # Validação básica (opcional)
    if not content or not project_id:
        flash('Por favor, preencha todos os campos.', 'danger')
        return redirect(url_for('messages'))

    # Insere a mensagem no banco de dados
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO messages (project_id, content) VALUES (%s, %s)",
        (project_id, content)
    )
    mysql.connection.commit()
    cur.close()

    # Exibe uma mensagem de sucesso
    flash('Mensagem enviada com sucesso!', 'success')

    # Redireciona de volta para a página de mensagens
    return redirect(url_for('messages'))
if __name__ == '__main__':
    app.run(debug=True)