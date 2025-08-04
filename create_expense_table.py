#!/usr/bin/env python3
import sqlite3
import os

# Caminho para o banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'restaurant.db')

# Conectar ao banco de dados
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Dropar a tabela se existir
cursor.execute('DROP TABLE IF EXISTS expense')

# Criar a tabela expense
cursor.execute('''
    CREATE TABLE expense (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description VARCHAR(120) NOT NULL,
        amount FLOAT NOT NULL,
        expense_type VARCHAR(50) NOT NULL,
        date DATE NOT NULL
    )
''')

# Confirmar as mudanças
conn.commit()
conn.close()

print("Tabela 'expense' criada com sucesso!")

