# 📊 LivePoll - Sistema de Enquetes em Tempo Real

Um projeto fullstack que une o modelo tradicional de APIs REST com a comunicação bidirecional em tempo real usando WebSockets. Desenvolvido para demonstrar a integração perfeita entre requisições HTTP padrão e eventos em tempo real no ecossistema Python.

## 🚀 Funcionalidades

*   **API RESTful:** Criação e listagem de enquetes via requisições HTTP (`GET` e `POST`).
*   **Tempo Real (WebSockets):** Os votos são computados e transmitidos via *broadcast* para todos os clientes conectados instantaneamente.
*   **Interface Reativa:** Frontend em HTML/CSS e Vanilla JS que atualiza a interface dinamicamente sem recarregar a página.
*   **Testes Automatizados:** Suíte de testes com `pytest` cobrindo tanto as rotas da API quanto os eventos do WebSocket.

## 🛠️ Tecnologias Utilizadas

*   **Backend:** Python 3, Flask
*   **Banco de Dados:** SQLite, Flask-SQLAlchemy (ORM)
*   **Tempo Real:** Flask-SocketIO (Baseado em Socket.IO)
*   **Frontend:** HTML5, CSS3, JavaScript (Fetch API + Socket.IO Client)
*   **Testes:** Pytest

## ⚙️ Como rodar o projeto localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/livepoll.git](https://github.com/SEU_USUARIO/livepoll.git)
   cd livepoll