# esocial Evt:
# github: https://github.com/akretion/esociallib.git

# app_recuperacao_flask_v2_jwt_async_ui

Flask + MariaDB com apuração GILRAT completa, **JWT**, **Celery** e **frontend simples**.

## Rodando
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="mysql+pymysql://usuario:senha@localhost:3306/recuperacao"
export JWT_SECRET_KEY="troque-isto"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"

# Inicializa app e tabelas
python app.py

# Cria admin
curl -X POST localhost:5000/auth/init_admin -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin"}'

# Worker Celery
celery -A tasks.celery worker --loglevel=info
```

Acesse `http://localhost:5000/login` para autenticar e usar a UI.


## Novidades v3
- JWT com **refresh token** (`POST /auth/refresh`) e expiração configurável via:
  - `JWT_ACCESS_TOKEN_EXPIRES_MIN` (padrão 60)
  - `JWT_REFRESH_TOKEN_EXPIRES_MIN` (padrão 30 dias)
- **Upload em lote (.zip)** em `/upload/lote`
- **Dashboard com gráficos** (Chart.js): Diferença vs Dif. Atualizada e Recolhido vs Devido.
- Botão de **refresh** do token disponível via função `refreshToken()` (pode ser acionado no console ou facilmente adicionado na UI).


## Novidades v4
- **XLSX** adicional nas exportações (além de CSV/PDF).
- **Botão "Renovar token"** na navbar (usa `/auth/refresh`).
- **Importação SELIC por URL** com Celery (`POST /selic/importar_csv_url` com `{ "url": "<csv>" }`).
- **Agendamento automático (opcional)**: defina `SELIC_CSV_URL` e execute `celery -A tasks.celery beat --loglevel=info` para importar **diariamente às 03:00** (horário do servidor).
