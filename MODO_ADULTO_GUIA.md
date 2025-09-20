# 🔍 Como Saber que o Chat está no Modo Adulto

## 🎯 **Resumo Rápido**

### 🌐 **Interface Web:**
- **URL contém:** `/adult/` (qualquer rota adulta)
- **Session:** `adult_mode_active = True`
- **Idade:** Usuário tem >= 18 anos

### 📱 **Telegram Bot:**
- **Comandos usados:** `/adult_mode`, `/adult_config`, `/adult_train`
- **Função:** `is_advanced_adult_active(user_id)` retorna `True`
- **Context:** `adult_mode_active = True`

---

## 🔍 **Métodos de Verificação Detalhados**

### 🌐 **Sistema Web**

#### ✅ **Verificação por URL:**
```python
# URLs que indicam modo adulto ativo
adult_urls = [
    '/adult/dashboard',
    '/adult/config', 
    '/adult/training',
    '/adult/age_verification',
    '/adult/api/chat'
]

def is_web_adult_active(current_url):
    return any(url in current_url for url in adult_urls)
```

#### ✅ **Verificação por Session:**
```python
# No Flask app
def check_web_adult_session():
    return session.get('adult_mode_active', False)
```

#### ✅ **Verificação por Database:**
```python
def check_web_adult_db(user_id):
    # Conectar user_profiles.db
    # Verificar: age >= 18 AND adult_mode_enabled = True
    return age_eligible and adult_enabled
```

### 📱 **Sistema Telegram**

#### ✅ **Verificação por Função:**
```python
from telegram_bot.handlers.adult_integration import is_advanced_adult_active

# Verificar se sistema avançado está ativo
adult_active = is_advanced_adult_active(user_id)
```

#### ✅ **Verificação por Context:**
```python
from telegram_bot.handlers.adult_integration import get_adult_personality_context

context = get_adult_personality_context(user_id)
adult_mode = context.get('adult_mode', False)
advanced_system = context.get('advanced_system', False)
```

#### ✅ **Verificação por Comandos:**
```python
# Comandos que indicam modo adulto
adult_commands = [
    '/adult_mode',      # Ativar sistema  
    '/adult_config',    # Configurações
    '/adult_train',     # Treinamento
    '/adult_status',    # Status
    '/devassa_off'      # Desativar
]
```

---

## 🔄 **Sistema Unificado de Verificação**

### 📋 **Script Pronto para Uso:**

Execute para verificar qualquer usuário:
```bash
python check_adult_mode.py [user_id]
```

### 🎯 **Função Unificada:**
```python
from check_adult_mode import check_unified_adult_mode

status = check_unified_adult_mode(user_id)
print(f"Modo adulto ativo: {status['unified_adult_mode']}")
```

---

## 🛡️ **Indicadores de Segurança**

### ✅ **Verificações Obrigatórias:**
1. **Idade >= 18 anos** (verificada no banco)
2. **Consentimento explícito** (adult_mode_enabled = True)
3. **Verificação ativa** (session/context ativo)

### 🔐 **Bancos de Dados:**
- **Perfis Normais:** `user_profiles.db`
- **Perfis Adultos:** `fast_learning.db`
- **Dados Sensíveis:** `sensitive_memory.db` (criptografado)

### 📊 **Tabelas de Controle:**
- `adult_profiles` - Configurações adultas
- `adult_safety` - Configurações de segurança
- `adult_vocabulary` - Vocabulário treinado

---

## 🚨 **Estados do Sistema**

### 🟢 **MODO ADULTO ATIVO:**
- Web: URL contém `/adult/` + session ativa
- Telegram: `is_advanced_adult_active()` = `True`
- Database: Perfil adulto existe e está ativo

### 🟡 **MODO ADULTO PARCIAL:**
- Idade elegível mas não habilitado
- Sistema básico ativo (sem personalidades avançadas)

### 🔴 **MODO ADULTO INATIVO:**
- Menor de idade
- Sistema não habilitado
- Sem verificação de idade

---

## 💡 **Dicas Práticas**

### 🔍 **Para Desenvolvedores:**
```python
# Verificação rápida no código
def is_adult_mode_active(user_id, platform='both'):
    if platform in ['web', 'both']:
        web_active = check_web_adult_mode(user_id)
    if platform in ['telegram', 'both']:
        telegram_active = check_telegram_adult_mode(user_id)
    
    return web_active or telegram_active
```

### 🎯 **Para Usuários:**
- **Web:** Acesse `/adult/dashboard` - se carregar, está ativo
- **Telegram:** Use `/adult_status` - mostra status completo

---

**✅ Sistema totalmente integrado e sincronizado entre Web e Telegram!**