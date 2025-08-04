# Sistema de Restaurante - Deploy no Render

Este projeto está configurado para funcionar tanto localmente quanto no Render com PostgreSQL.

## Configuração Local

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variáveis de ambiente:**
   - O arquivo `.env` já está configurado para desenvolvimento local
   - Edite o `.env` se necessário para configurar email

3. **Executar localmente:**
   ```bash
   python src/main.py
   ```
   - O projeto usará SQLite localmente
   - Acesse: http://localhost:5000

## Deploy no Render

### 1. Preparar o Repositório

1. **Inicializar Git (se ainda não foi feito):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Enviar para GitHub:**
   - Crie um repositório no GitHub
   - Adicione o remote e faça push:
   ```bash
   git remote add origin https://github.com/seu-usuario/seu-repositorio.git
   git branch -M main
   git push -u origin main
   ```

### 2. Configurar no Render

1. **Criar Web Service:**
   - Acesse [render.com](https://render.com)
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub

2. **Configurações do Service:**
   - **Name:** restaurante-app (ou nome de sua escolha)
   - **Environment:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT src.main:app`

3. **Variáveis de Ambiente:**
   Adicione as seguintes variáveis de ambiente no Render:
   
   ```
   DATABASE_URL=postgresql://restaurante_8v3r_user:KCIIkMKYwf8phyykr9pMOHZy1f1Pvtid@dpg-d27u2emuk2gs73ellrfg-a/restaurante_8v3r
   SECRET_KEY=seu_secret_key_aqui_mude_para_producao
   MAIL_SERVER=smtp.googlemail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=seu_email@gmail.com
   MAIL_PASSWORD=sua_senha_de_app
   ```

4. **Deploy:**
   - Clique em "Create Web Service"
   - O Render fará o build e deploy automaticamente

### 3. Configuração do Email (Opcional)

Para funcionalidade de email, configure:
- Use uma senha de aplicativo do Gmail (não sua senha normal)
- Ou configure outro provedor de email

### 4. Estrutura do Projeto

```
restaurante/
├── src/
│   ├── main.py              # Aplicação principal
│   ├── database.py          # Configuração do banco
│   ├── models/              # Modelos do banco de dados
│   ├── routes/              # Rotas da aplicação
│   ├── templates/           # Templates HTML
│   └── static/              # Arquivos estáticos
├── migrations/              # Migrações do banco
├── requirements.txt         # Dependências Python
├── Procfile                 # Configuração para Render
├── build.sh                 # Script de build
├── .env                     # Variáveis locais (não commitado)
├── .gitignore              # Arquivos ignorados pelo Git
└── README_DEPLOY.md        # Este arquivo
```

### 5. Funcionalidades

- **Ambiente Local:** SQLite para desenvolvimento
- **Ambiente Produção:** PostgreSQL no Render
- **Migrações:** Automáticas no deploy
- **Email:** Configurável via variáveis de ambiente
- **Autenticação:** Sistema de login/registro
- **Admin:** Painel administrativo
- **Cliente:** Interface para clientes

### 6. Troubleshooting

**Erro de migração:**
- As migrações são aplicadas automaticamente no build
- Se houver erro, verifique os logs no Render

**Erro de conexão com banco:**
- Verifique se a DATABASE_URL está correta
- Confirme que o banco PostgreSQL está ativo

**Erro de dependências:**
- Verifique se todas as dependências estão no requirements.txt
- Confirme a versão do Python no Render

### 7. Atualizações

Para atualizar o projeto:
1. Faça as alterações localmente
2. Teste localmente
3. Commit e push para GitHub
4. O Render fará redeploy automaticamente

## Contato

Para dúvidas sobre o deploy, verifique os logs no Render ou consulte a documentação oficial.

