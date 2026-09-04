from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

# 1. CONFIGURAÇÃO INICIAL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///livepoll.db'
app.config['SECRET_KEY'] = 'minha_chave_secreta_super_segura' # Necessário para o SocketIO

db = SQLAlchemy(app)
# Inicializamos o SocketIO passando nosso app Flask
socketio = SocketIO(app, cors_allowed_origins="*") 

# ==========================================
# 2. MODELOS DE BANCO DE DADOS (Revisão)
# ==========================================
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    # Relação com as opções
    options = db.relationship('Option', backref='poll', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0) # Começa com 0 votos
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)

# Cria o banco de dados e as tabelas caso não existam
with app.app_context():
    db.create_all()

# ==========================================
# 3. ROTAS DA API REST (Revisão)
# ==========================================
# Rota para servir a página HTML
@app.route('/')
def index():
    return render_template('index.html')

# Rota para criar uma enquete (POST) e listar enquetes (GET)
@app.route('/api/polls', methods=['GET', 'POST'])
def handle_polls():
    if request.method == 'POST':
        data = request.json
        # Cria a nova enquete
        new_poll = Poll(question=data['question'])
        db.session.add(new_poll)
        db.session.commit()
        
        # Cria as opções vinculadas a essa enquete
        for opt_text in data['options']:
            new_option = Option(text=opt_text, poll_id=new_poll.id)
            db.session.add(new_option)
        db.session.commit()
        
        return jsonify({"message": "Enquete criada!", "id": new_poll.id}), 201

    elif request.method == 'GET':
        polls = Poll.query.all()
        result = []
        for p in polls:
            options_data = [{"id": o.id, "text": o.text, "votes": o.votes} for o in p.options]
            result.append({"id": p.id, "question": p.question, "options": options_data})
        return jsonify(result), 200

# ==========================================
# 4. WEBSOCKETS (O Assunto Novo!)
# ==========================================

# O decorator @socketio.on escuta eventos específicos vindos do cliente
@socketio.on('submit_vote')
def handle_vote(data):
    """
    Esta função é chamada instantaneamente quando alguém vota.
    O cliente envia um JSON 'data' com o id da opção escolhida.
    """
    option_id = data.get('option_id')
    
    # Busca a opção no banco de dados e adiciona 1 voto
    option = Option.query.get(option_id)
    if option:
        option.votes += 1
        db.session.commit()
        
        # Aqui está a mágica do Tempo Real:
        # Emitimos um evento chamado 'vote_update' com os novos dados.
        # O argumento "broadcast=True" envia isso para TODOS os usuários conectados!
        emit('vote_update', {
            'poll_id': option.poll_id,
            'option_id': option.id,
            'new_votes': option.votes
        }, broadcast=True)

# ==========================================
# 5. INICIANDO O SERVIDOR
# ==========================================
if __name__ == '__main__':
    # Usamos socketio.run() em vez de app.run() para suportar os WebSockets
    socketio.run(app, debug=True)