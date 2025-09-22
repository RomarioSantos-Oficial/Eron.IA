# 📦 GUIA DE INSTALAÇÃO - ERON.IA

## 🚀 INSTALAÇÃO RÁPIDA

### 1. **Clonar o Repositório**
```bash
git clone https://github.com/RomarioSantos-Oficial/Eron.IA.git
cd Eron.IA
```

### 2. **Criar Ambiente Virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. **Instalar Dependências**
```bash
# Instalação básica (produção)
pip install -r requirements.txt

# Instalação completa (desenvolvimento)
pip install -r requirements-dev.txt

# Ou instalação via setup.py
pip install -e .
```

### 4. **Configurar Ambiente**
```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações (substitua pelos seus valores)
nano .env  # ou use seu editor preferido
```

### 5. **Executar Sistema**
```bash
# Executar ambos (web + telegram)
python run_all.py

# Ou executar separadamente:
python web/app.py        # Apenas web
python telegram_bot/bot_main.py  # Apenas telegram
```

---

## 🔧 CONFIGURAÇÃO DETALHADA

### **📋 Dependências por Categoria**

**🌐 Framework Web:**
- `Flask 3.0.0` - Framework principal
- `Werkzeug 3.0.1` - Utilitários web

**🤖 Telegram Bot:**
- `python-telegram-bot 20.7` - API do Telegram

**🔐 Segurança:**
- `cryptography 41.0.8` - Criptografia
- `python-dotenv 1.0.0` - Variáveis de ambiente

**📡 Comunicação:**
- `requests 2.31.0` - Requisições HTTP
- `urllib3 2.1.0` - Parsing de URLs

**📊 Dados:**
- `python-dateutil 2.8.2` - Manipulação de datas
- `jsonschema 4.20.0` - Validação JSON

### **⚙️ Configuração do .env**

Edite o arquivo `.env` com suas configurações:

```env
# API do modelo de IA
LM_STUDIO_API_URL=http://localhost:1234

# Token do Telegram Bot
TELEGRAM_BOT_TOKEN=seu_token_aqui

# Chave secreta do Flask
SECRET_KEY=sua_chave_secreta_aleatoria

# Configurações de email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_de_app
```

---

## 🛠️ AMBIENTES DE DESENVOLVIMENTO

### **Para Desenvolvedores:**
```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Ferramentas incluídas:
# - pytest (testes)
# - black (formatação)
# - flake8 (linting)
# - mypy (type checking)
# - sphinx (documentação)
```

### **Comandos Úteis:**
```bash
# Formatar código
black . && isort .

# Verificar qualidade do código
flake8 . && pylint src/

# Rodar testes
pytest --cov=src tests/

# Verificar segurança
bandit -r src/

# Gerar documentação
sphinx-build -b html docs/ docs/_build/
```

---

## 📋 REQUISITOS DO SISTEMA

### **🐍 Python:**
- **Mínimo:** Python 3.8
- **Recomendado:** Python 3.10+

### **💻 Sistema Operacional:**
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, CentOS)
- ✅ macOS 10.15+

### **💾 Recursos:**
- **RAM:** Mínimo 2GB, Recomendado 4GB+
- **Armazenamento:** 1GB livre para dados e logs
- **Rede:** Conexão para APIs (LM Studio, Telegram)

---

## 🚨 SOLUÇÃO DE PROBLEMAS

### **❌ Erro: "No module named 'telegram'"**
```bash
pip install python-telegram-bot==20.7
```

### **❌ Erro: "ModuleNotFoundError: No module named 'flask'"**
```bash
pip install Flask==3.0.0
```

### **❌ Erro: "Permission denied" no Windows**
```bash
# Executar como administrador ou usar:
python -m pip install --user -r requirements.txt
```

### **❌ Problemas com criptografia no Linux**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential libffi-dev python3-dev

# CentOS/RHEL
sudo yum install gcc openssl-devel libffi-devel python3-devel
```

### **❌ Erro: "SSL Certificate error"**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## 📊 VERIFICAÇÃO DA INSTALAÇÃO

### **✅ Teste Rápido:**
```bash
# Testar importações principais
python -c "import flask, telegram, cryptography, requests; print('✅ Dependências OK!')"

# Verificar versões
python -c "import sys; print(f'Python: {sys.version}')"
pip list | grep -E "(Flask|python-telegram-bot|cryptography)"
```

### **🔍 Diagnóstico Completo:**
```bash
# Executar script de diagnóstico
python -c "
import sys
import pkg_resources
import os

print('=== DIAGNÓSTICO ERON.IA ===')
print(f'Python: {sys.version}')
print(f'Plataforma: {sys.platform}')
print(f'Diretório: {os.getcwd()}')

required = ['flask', 'python-telegram-bot', 'cryptography', 'requests', 'python-dotenv']
for package in required:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f'✅ {package}: {version}')
    except:
        print(f'❌ {package}: NÃO ENCONTRADO')

print('=== ARQUIVOS ESSENCIAIS ===')
files = ['.env', 'web/app.py', 'telegram_bot/bot_main.py', 'src/']
for file in files:
    if os.path.exists(file):
        print(f'✅ {file}')
    else:
        print(f'❌ {file}: NÃO ENCONTRADO')
"
```

---

## 📞 SUPORTE

**🐛 Bug Reports:**
- GitHub Issues: https://github.com/RomarioSantos-Oficial/Eron.IA/issues

**📖 Documentação:**
- Wiki: https://github.com/RomarioSantos-Oficial/Eron.IA/wiki

**💬 Comunidade:**
- Discussions: https://github.com/RomarioSantos-Oficial/Eron.IA/discussions

---

**✨ Instalação concluída com sucesso? Execute `python run_all.py` e aproveite!**