# Sistema de Gestão de Restaurantes - Flask

## Descrição
Sistema completo de gestão de restaurantes desenvolvido em Flask com as seguintes funcionalidades:

### Funcionalidades Implementadas

#### Autenticação e Autorização
- ✅ Sistema de login/logout
- ✅ Registro de novos usuários
- ✅ Redefinição de senha por email
- ✅ Controle de acesso (Admin/Cliente)

#### Painel de Administração
- ✅ Dashboard com estatísticas
- ✅ Gestão de produtos e categorias
- ✅ Gestão de pedidos (visualização e atualização de status)
- ✅ Gestão de funcionários
- ✅ Gestão de promoções e cupons de desconto

#### Interface do Cliente
- ✅ Página inicial com produtos em destaque
- ✅ Cardápio com filtros por categoria
- ✅ Carrinho de compras
- ✅ Sistema de checkout com múltiplas formas de pagamento
- ✅ Acompanhamento de pedidos em tempo real
- ✅ Histórico de pedidos
- ✅ Sistema de cupons de desconto

#### Recursos Técnicos
- ✅ Base de dados SQLite com SQLAlchemy
- ✅ Migrações de base de dados com Flask-Migrate
- ✅ Interface responsiva com Bootstrap
- ✅ Sistema de sessões para carrinho
- ✅ Validação de formulários
- ✅ Flash messages para feedback

## Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Extrair o arquivo zip**
   ```bash
   unzip restaurant_system_complete.zip
   cd restaurant_system
   ```

2. **Criar ambiente virtual**
   ```bash
   python -m venv venv
   ```

3. **Ativar ambiente virtual**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar base de dados**
   ```bash
   # Inicializar migrações (se necessário)
   flask db init
   
   # Aplicar migrações
   flask db upgrade
   ```

6. **Criar dados de teste (opcional)**
   ```bash
   python create_test_data.py
   ```

7. **Executar a aplicação**
   ```bash
   python src/main.py
   ```

8. **Acessar a aplicação**
   - Abrir navegador em: http://localhost:5000

## Credenciais de Teste

### Administrador
- **Usuário:** admin
- **Senha:** admin123

### Cliente
- **Usuário:** cliente
- **Senha:** cliente123

## Estrutura do Projeto

```
restaurant_system/
├── src/
│   ├── main.py                 # Arquivo principal da aplicação
│   ├── database.py             # Configuração da base de dados
│   ├── models/                 # Modelos de dados
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── employee.py
│   │   └── promotion.py
│   ├── routes/                 # Rotas da aplicação
│   │   ├── auth.py
│   │   ├── admin.py
│   │   └── client.py
│   ├── templates/              # Templates HTML
│   │   ├── admin/
│   │   └── client/
│   └── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── migrations/                 # Migrações da base de dados
├── requirements.txt            # Dependências Python
└── README_INSTALACAO.md        # Este arquivo
```

## Configuração de Email (Opcional)

Para ativar o envio de emails de redefinição de senha, edite o arquivo `src/main.py`:

```python
app.config["MAIL_USERNAME"] = "seu_email@gmail.com"
app.config["MAIL_PASSWORD"] = "sua_senha_de_app"
```

## Funcionalidades Principais

### Para Administradores
1. Acesse com credenciais de admin
2. Gerir produtos, categorias, pedidos e funcionários
3. Visualizar estatísticas no dashboard
4. Criar promoções e cupons

### Para Clientes
1. Registre-se ou faça login
2. Navegue pelo cardápio
3. Adicione produtos ao carrinho
4. Finalize pedidos
5. Acompanhe o status dos pedidos

## Suporte

Para dúvidas ou problemas, verifique:
1. Se todas as dependências foram instaladas
2. Se o ambiente virtual está ativado
3. Se as migrações foram aplicadas
4. Se a porta 5000 está disponível

## Tecnologias Utilizadas

- **Backend:** Flask, SQLAlchemy, Flask-Login, Flask-Mail, Flask-Migrate
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Base de Dados:** SQLite
- **Autenticação:** Flask-Login com hash de senhas
- **Email:** Flask-Mail (configuração opcional)

