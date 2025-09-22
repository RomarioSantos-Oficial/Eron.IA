# 🚀 Guia de Configuração Rápida - Sistema de Moderação

Este guia vai te ajudar a configurar rapidamente o sistema de moderação de conteúdo adulto no seu bot Telegram.

## 📋 Pré-requisitos

```bash
pip install python-telegram-bot
pip install cryptography  # Para memoria sensível
pip install sqlite3       # Geralmente já incluído no Python
```

## ⚙️ Configuração em 5 Passos

### 1️⃣ Configure o Token do Bot

**Método 1: Arquivo .env (Recomendado)**
```bash
# Adicione no seu .env
TOKEN_BOT=1234567890:ABCDEF1234567890abcdef1234567890abc
```

**Método 2: Direto no código**
```python
# Em examples/moderated_telegram_bot.py, linha ~45
TOKEN = "1234567890:ABCDEF1234567890abcdef1234567890abc"
```

### 2️⃣ Configure seus IDs de Administrador

**Como descobrir seu ID:**
```
1. Envie uma mensagem para @userinfobot
2. Copie o ID que ele retornar
3. Configure no código:
```

```python
# Em examples/moderated_telegram_bot.py, linha ~48
ADMIN_IDS = [
    SEU_ID_AQUI,      # Exemplo: 123456789
    OUTRO_ADMIN_ID,   # Exemplo: 987654321
]
```

### 3️⃣ Ativar Sistema de Moderação

**No arquivo .env:**
```bash
# Ativar moderação
ADULT_MODERATION_ENABLED=True

# Configurar sensibilidade (low, medium, high)
MODERATION_SENSITIVITY=medium

# Ações automáticas
AUTO_WARN_MILD=True
AUTO_FILTER_MODERATE=True
AUTO_BLOCK_SEVERE=True
```

### 4️⃣ Executar o Bot

```bash
cd "c:\Users\limar\Desktop\Nova pasta\Eron.IA"
python examples/moderated_telegram_bot.py
```

### 5️⃣ Testar o Sistema

**Envie estas mensagens para testar:**

✅ **Conteúdo limpo:**
```
"Olá, como você está hoje?"
"Preciso de ajuda com programação"
```

⚠️ **Conteúdo moderado (deve gerar aviso):**
```
"droga"
"sexual"
```

🚫 **Conteúdo bloqueado (deve ser filtrado):**
```
"pornografia"
"xxx"
```

## 🎛️ Comandos do Bot

### Para todos os usuários:
- `/start` - Iniciar conversa
- `/help` - Ajuda
- `/status` - Status do sistema

### Para administradores:
- `/modstats` - Estatísticas de moderação
- `/checkuser USER_ID` - Verificar status de usuário
- `/unblock USER_ID` - Desbloquear usuário

## 🔧 Personalizações Avançadas

### Configurar Sensibilidade por Grupo

```python
# No examples/moderated_telegram_bot.py
GROUP_CONFIGS = {
    -1001234567890: {  # ID do seu grupo
        'sensitivity': 'high',      # high, medium, low
        'auto_filter': True,        # Filtrar automaticamente
        'admin_notifications': True # Notificar admins
    }
}
```

### Adicionar Padrões Personalizados

```bash
# Usar ferramenta de gestão
python tools/moderation_manager.py --add-pattern "palavra_proibida" moderate
```

### Configurar Limites

```bash
# No .env
MAX_VIOLATIONS_BEFORE_QUARANTINE=3
MAX_VIOLATIONS_BEFORE_BLOCK=5
QUARANTINE_DURATION_HOURS=24
```

## 📊 Monitoramento

### Ver Estatísticas no Terminal
```bash
python tools/moderation_manager.py --stats
```

### Ver Usuários Problemáticos
```bash
python tools/moderation_manager.py --stats --days 30
```

### Desbloquear Usuário Manualmente
```bash
python tools/moderation_manager.py --unblock USER_ID
```

## 🚨 Solução de Problemas

### Erro: "Token inválido"
```
- Verifique se o token está correto
- Certifique-se que o bot está ativo no @BotFather
```

### Erro: "Sistema de moderação desabilitado"  
```
- Configure ADULT_MODERATION_ENABLED=True no .env
- Verifique se o arquivo .env está no diretório raiz
```

### Erro: "Não é administrador"
```
- Verifique se seu ID está em ADMIN_IDS
- Use @userinfobot para confirmar seu ID
```

### Bot não responde a comandos
```
- Verifique se o bot tem permissões no grupo
- Confirme que o token está correto
- Veja os logs no terminal para erros
```

## 📁 Estrutura de Arquivos

```
Eron.IA/
├── examples/
│   └── moderated_telegram_bot.py    # Bot principal
├── docs/
│   └── telegram_moderation_integration_example.py
├── src/
│   ├── adult_content_moderator.py   # Sistema de moderação
│   └── telegram_moderation_middleware.py
├── tools/
│   └── moderation_manager.py        # Ferramenta de gestão
├── memoria/
│   ├── adult_moderation.db          # Logs de moderação
│   └── content_patterns.db          # Padrões de conteúdo
├── config.py                        # Configurações
└── .env                            # Variáveis de ambiente
```

## 🎯 Próximos Passos

1. **Personalizar Padrões:** Adicione palavras específicas do seu contexto
2. **Configurar Grupos:** Defina sensibilidade por grupo/chat
3. **Monitorar:** Use os comandos administrativos regularmente
4. **Ajustar:** Modifique sensibilidade baseado no uso real
5. **Expandir:** Adicione novos tipos de moderação conforme necessário

## 📞 Suporte

- Verifique os logs no terminal
- Use `python tools/moderation_manager.py --help`
- Consulte a documentação em `docs/`

---

✅ **Sistema pronto para usar!** Agora você tem um bot Telegram com moderação automática de conteúdo adulto funcionando.