# Iniciar o Ambiente Virtual
Write-Host "Ativando o ambiente virtual..."
.\venv\Scripts\Activate.ps1

# Instalar as dependências do requirements.txt
Write-Host "Instalando as dependências..."
pip install -r requirements.txt

# Rodar a aplicação
Write-Host "Iniciando o Eron..."
python run_all.py

# A instrução 'pause' é útil para que a janela não feche imediatamente após a execução, caso ocorra algum erro.
# pause