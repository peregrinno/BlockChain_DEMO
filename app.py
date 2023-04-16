from flask import Flask, render_template, request
import sqlite3
import hashlib
import json
import datetime

app = Flask(__name__)


# função para criar o hash de um bloco
def hash_block(block):
    block_str = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_str).hexdigest()

# função para adicionar um novo bloco ao blockchain
def add_block(data):
    conn = sqlite3.connect('blockchain.db')
    c = conn.cursor()

    # obter o último bloco do blockchain, ou definir valores iniciais se o blockchain estiver vazio
    c.execute('SELECT * FROM blockchain ORDER BY id_index DESC LIMIT 1')
    last_block = c.fetchone()
    if last_block is None:
        id_index = 1
        previous_hash = ''
    else:
        id_index = last_block[0] + 1
        previous_hash = last_block[4]

    # criar um novo bloco
    timestamp = str(datetime.datetime.now())
    block = {'id_index': id_index, 'timestamp': timestamp, 'data': data, 'previous_hash': previous_hash}
    block['hash'] = hash_block(block)

    # inserir o novo bloco no banco de dados
    c.execute('INSERT INTO blockchain VALUES (?, ?, ?, ?, ?)',
              (block['id_index'], block['timestamp'], block['data'], block['previous_hash'], block['hash']))
    conn.commit()
    conn.close()

# função para verificar a integridade do blockchain
def validate_blockchain():
    conn = sqlite3.connect('blockchain.db')
    c = conn.cursor()
    
    # obter todos os blocos do blockchain
    c.execute('SELECT * FROM blockchain')
    blocks = c.fetchall()
    
    # verificar a integridade de cada bloco
    for i in range(1, len(blocks)):
        current_block = blocks[i]
        previous_block = blocks[i-1]
        
        # verificar se o hash do bloco atual é válido
        if current_block[4] != hash_block({'id_index': current_block[0], 'timestamp': current_block[1],
                                           'data': current_block[2], 'previous_hash': current_block[3]}):
            return False
        
        # verificar se o hash do bloco anterior é válido
        if previous_block[4] != hash_block({'id_index': previous_block[0], 'timestamp': previous_block[1],'data': previous_block[2], 'previous_hash': previous_block[3]}):
            return False

    return True

@app.route('/')
def index():
    conn = sqlite3.connect('blockchain.db')
    c = conn.cursor()
    # obter todos os blocos do blockchain
    c.execute('SELECT * FROM blockchain')
    blocks = c.fetchall()

    conn.close()
    year = 2023

    return render_template('index.html', blocks=blocks, year=year)

@app.route('/add', methods=['POST'])
def add():
    data = request.form['data']
    add_block(data)
    return index()

@app.route('/validate')
def validate():
    valid = validate_blockchain()
    return render_template('validate.html', valid=valid)

if __name__ == '__main__':
    app.run(debug=True)