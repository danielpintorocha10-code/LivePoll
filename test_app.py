import pytest
from app import app, db, socketio

# Esta "fixture" prepara o ambiente antes de cada teste rodar.
# Ela cria um banco de dados falso na memória (para não sujar o seu banco real)
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Banco temporário
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
        # Limpa o banco após o teste terminar
        with app.app_context():
            db.drop_all()

# ==========================================
# TESTE 1: Testando a API REST Tradicional
# ==========================================
def test_criar_enquete(client):
    """Verifica se a rota POST /api/polls cria uma enquete corretamente"""
    # Simulamos o envio de um JSON via POST (como fizemos no Postman)
    resposta = client.post('/api/polls', json={
        "question": "O pytest é legal?",
        "options": ["Sim", "Com certeza"]
    })
    
    # O status 201 significa "Criado com sucesso"
    assert resposta.status_code == 201
    assert b"Enquete criada!" in resposta.data

# ==========================================
# TESTE 2: Testando os WebSockets
# ==========================================
def test_voto_em_tempo_real(client):
    """Verifica se ao enviar um voto via Socket, o servidor devolve o placar atualizado"""
    
    # 1. Primeiro, criamos uma enquete usando a API
    client.post('/api/polls', json={
        "question": "Teste Sockets",
        "options": ["A", "B"]
    })
    
    # 2. Conectamos um "cliente fantasma" do SocketIO ao nosso app
    socket_client = socketio.test_client(app, flask_test_client=client)
    assert socket_client.is_connected()
    
    # 3. Disparamos o evento de voto (simulando o clique no botão do HTML)
    # A opção 1 foi a primeira que criamos
    socket_client.emit('submit_vote', {'option_id': 1})
    
    # 4. Capturamos o que o servidor enviou de volta (o broadcast)
    mensagens_recebidas = socket_client.get_received()
    
    # Verificamos se o servidor respondeu algo
    assert len(mensagens_recebidas) > 0
    
    # Verificamos se o evento disparado pelo servidor foi o 'vote_update'
    evento = mensagens_recebidas[0]
    assert evento['name'] == 'vote_update'
    
    # Verificamos se o placar computou 1 voto corretamente!
    dados = evento['args'][0]
    assert dados['new_votes'] == 1