# Web Directory

Esta pasta contém toda a interface web do projeto Eron.IA:

## Arquivos Principais

- `app.py` - Aplicação Flask principal (ARQUIVO PRINCIPAL DA WEB)
- `app_factory.py` - Factory pattern para criação da aplicação
- `app_new.py` - Nova versão da aplicação (em desenvolvimento)

## Subpastas

- `routes/` - Blueprints organizados por funcionalidade
  - `auth.py` - Rotas de autenticação
  - `chat.py` - Rotas do chat
  - `config.py` - Rotas de configuração
  - `main.py` - Rotas principais
- `services/` - Serviços específicos da web

## Como Executar

```bash
# Executar a aplicação web
python web/app.py

# Ou usar o sistema completo
python run_all.py
```

## Funcionalidades

- Interface web para chat com IA
- Sistema de login/registro
- Personalização do bot
- Configurações avançadas
- Sistema emocional
- Gerenciamento de preferências