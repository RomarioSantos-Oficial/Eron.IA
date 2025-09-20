# 🔒 SEGURANÇA E PRIVACIDADE - ERON.IA

## ⚠️ DADOS SENSÍVEIS PROTEGIDOS

Este projeto protege automaticamente os seguintes tipos de dados dos usuários:

### 📊 DADOS PESSOAIS
- ✅ **Perfis de usuários** (`user_profiles.db`)
- ✅ **Conversas e histórico** (pasta `memoria/`)
- ✅ **Preferências pessoais** (`preferences.db`)
- ✅ **Estados emocionais** (`emotions.db`)
- ✅ **Conhecimento personalizado** (`knowledge.db`)
- ✅ **Memória sensível** (`sensitive_memory.db`)

### 🔑 CHAVES E CREDENCIAIS
- ✅ **Tokens do Telegram** 
- ✅ **Chaves de criptografia** (`*.key`)
- ✅ **Variáveis de ambiente** (`.env`)
- ✅ **Configurações de API**

### 💾 ARQUIVOS DE SISTEMA
- ✅ **Logs com dados pessoais** (`*.log`)
- ✅ **Backups** (pasta `backup/`)
- ✅ **Uploads de usuários** (`uploads/`)
- ✅ **Sessões ativas** (`sessions/`)

## 🛡️ COMO CONTRIBUIR COM SEGURANÇA

### 1. **NUNCA FAÇA COMMIT DE:**
```
❌ Arquivos .env com valores reais
❌ Bancos de dados com dados pessoais
❌ Tokens ou chaves de API
❌ Logs de conversas reais
❌ Backups com informações de usuários
```

### 2. **SEMPRE VERIFIQUE ANTES DE COMMITAR:**
```bash
# Verificar arquivos que serão enviados
git status

# Verificar conteúdo dos arquivos
git diff --cached

# Se houver dados sensíveis, remover do stage
git reset HEAD arquivo_sensivel.db
```

### 3. **USE O ARQUIVO .env.example:**
- Copie `.env.example` para `.env`
- Configure suas variáveis locais
- NUNCA commite o arquivo `.env` real

### 4. **CONFIGURAÇÃO SEGURA:**
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas configurações (não committar!)
nano .env
```

## 🔍 VERIFICAÇÃO DE SEGURANÇA

### Comando para verificar vazamentos:
```bash
# Verificar se há arquivos sensíveis no git
git ls-files | grep -E '\.(db|key|log|env)$'

# Se retornar algo, REMOVER imediatamente:
git rm --cached arquivo_sensivel.db
git commit -m "Remove arquivo sensível do repositório"
```

### Em caso de vazamento acidental:
```bash
# Remover arquivo do histórico (CUIDADO!)
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch arquivo_sensivel.db' \
--prune-empty --tag-name-filter cat -- --all

# Forçar push (apaga histórico)
git push origin --force --all
```

## 📋 CHECKLIST DE SEGURANÇA

Antes de fazer qualquer commit:

- [ ] ✅ Arquivo `.gitignore` está atualizado
- [ ] ✅ Não há arquivos `.db` sendo commitados
- [ ] ✅ Não há arquivos `.env` com dados reais
- [ ] ✅ Não há logs com conversas pessoais
- [ ] ✅ Não há tokens ou chaves expostas
- [ ] ✅ Pasta `memoria/` está sendo ignorada
- [ ] ✅ Arquivos `*.key` estão sendo ignorados

## 🚨 EM CASO DE EMERGÊNCIA

Se você acidentalmente commitou dados sensíveis:

1. **PARE** - Não faça push se ainda não fez
2. **REMOVA** o arquivo do stage/commit imediatamente
3. **CONTATE** o administrador do repositório
4. **DOCUMENTE** o incidente para melhorar a segurança

## 📞 CONTATO PARA QUESTÕES DE SEGURANÇA

Para reportar problemas de segurança ou vazamento de dados:
- **Email**: [seu-email-de-seguranca]
- **Issue privada**: Marque como "security" no GitHub

---

**⚠️ LEMBRE-SE: A privacidade dos usuários é nossa responsabilidade!**