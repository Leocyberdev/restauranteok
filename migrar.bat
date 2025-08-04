@echo off
echo Iniciando migração do banco de dados...

REM Ativa o ambiente virtual (ajuste o caminho se for diferente)
call .venv\Scripts\activate.bat

REM Ir para a pasta onde está o main.py
cd src

REM Rodar com o caminho correto da aplicação
flask --app main db init
flask --app main db migrate -m "Migração automática"
flask --app main db upgrade

cd ..

echo Migração concluída com sucesso!
pause
