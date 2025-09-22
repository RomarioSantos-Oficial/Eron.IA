"""
Exemplo de Integração - Sistema de Moderação com Telegram Bot
=============================================================

Demonstra como integrar o sistema de moderação com o bot do Telegram,
incluindo middleware, handlers e comandos administrativos.

Funcionalidades demonstradas:
- Interceptação automática de mensagens
- Comandos administrativos de moderação
- Relatórios em tempo real
- Configuração de bypass para administradores
- Handlers personalizados

Uso:
python docs/telegram_moderation_integration_example.py

Autor: Eron.IA System
Data: 2024
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai para imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.telegram_moderation_middleware import create_moderation_middleware, TelegramModerationHandler
    from src.adult_content_moderator import get_moderation_stats, is_user_blocked
    from tools.moderation_manager import ModerationManager
    from config import config
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    sys.exit(1)


# ============================================================================
# EXEMPLO 1: Configuração básica do middleware
# ============================================================================

def example_basic_middleware_setup():
    """Exemplo básico de configuração do middleware"""
    print("🛡️ EXEMPLO 1: Configuração Básica do Middleware")
    print("-" * 60)
    
    # IDs dos administradores que podem bypassar moderação
    admin_ids = [123456789, 987654321]  # Substitua por IDs reais
    
    # Criar middleware
    middleware = create_moderation_middleware(admin_ids=admin_ids)
    
    print(f"✅ Middleware criado:")
    print(f"   Moderação ativa: {middleware.enabled}")
    print(f"   Administradores: {len(middleware.bypass_admin_ids)}")
    
    # Exemplo de uso com python-telegram-bot
    print(f"\n💡 **Para integrar com seu bot:**")
    print("""
from telegram.ext import Application, MessageHandler, filters
from src.telegram_moderation_middleware import create_moderation_middleware

# Configurar aplicação
app = Application.builder().token("SEU_TOKEN").build()

# Criar middleware de moderação  
middleware = create_moderation_middleware(admin_ids=[SEU_ADMIN_ID])

# Adicionar handler ANTES dos handlers de mensagem
async def moderation_filter(update, context):
    # Verificar moderação
    can_proceed = await middleware.check_message(update, context)
    if not can_proceed:
        return  # Bloquear processamento
    
    # Continuar com lógica normal do bot
    return await your_message_handler(update, context)

# Registrar handler
app.add_handler(MessageHandler(filters.TEXT, moderation_filter))
""")


# ============================================================================
# EXEMPLO 2: Comandos administrativos de moderação
# ============================================================================

def example_admin_commands():
    """Exemplo de comandos administrativos para moderação"""
    print("\n🔧 EXEMPLO 2: Comandos Administrativos")
    print("-" * 60)
    
    # Simulação de comandos administrativos
    commands_example = """
# Comandos para adicionar ao seu bot

async def cmd_moderation_stats(update, context):
    \"\"\"Comando /modstats - Estatísticas de moderação\"\"\"
    user_id = update.effective_user.id
    
    # Verificar se é administrador
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Comando apenas para administradores")
        return
    
    # Obter estatísticas
    stats = get_moderation_stats(days=7)
    
    message = f'''📊 **ESTATÍSTICAS DE MODERAÇÃO (7 dias)**
    
📈 **Hoje:**
• Verificações: {stats['current_stats']['total_checks_today']:,}
• Bloqueios: {stats['current_stats']['blocks_today']:,}
• Avisos: {stats['current_stats']['warnings_today']:,}

🏷️ **Período:**
• Total de ações: {sum(stats['action_stats'].values()):,}
• Top violadores: {len(stats['top_violators'])}'''
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def cmd_unblock_user(update, context):
    \"\"\"Comando /unblock USER_ID - Desbloquear usuário\"\"\"
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Uso: /unblock USER_ID")
        return
    
    user_id = context.args[0]
    
    # Usar ModerationManager
    manager = ModerationManager()
    manager.unblock_user(user_id)
    
    await update.message.reply_text(f"✅ Usuário {user_id} desbloqueado")

async def cmd_check_user(update, context):
    \"\"\"Comando /checkuser USER_ID - Verificar status do usuário\"\"\"
    if update.effective_user.id not in ADMIN_IDS:
        return
        
    if not context.args:
        await update.message.reply_text("Uso: /checkuser USER_ID")
        return
    
    user_id = context.args[0]
    blocked = is_user_blocked(user_id)
    status = "🚫 Bloqueado" if blocked else "✅ Ativo"
    
    await update.message.reply_text(f"👤 Usuário {user_id}: {status}")

# Registrar comandos
app.add_handler(CommandHandler("modstats", cmd_moderation_stats))
app.add_handler(CommandHandler("unblock", cmd_unblock_user))  
app.add_handler(CommandHandler("checkuser", cmd_check_user))
"""
    
    print("💡 **Comandos administrativos sugeridos:**")
    print("   /modstats - Estatísticas de moderação")
    print("   /unblock USER_ID - Desbloquear usuário")
    print("   /checkuser USER_ID - Verificar status")
    print("   /patterns - Listar padrões ativos")
    print("   /testcontent TEXTO - Testar conteúdo")
    
    print(f"\n📝 **Código de exemplo salvo em:** telegram_admin_commands.py")


# ============================================================================
# EXEMPLO 3: Handler personalizado com moderação
# ============================================================================

def example_custom_handler():
    """Exemplo de handler personalizado integrado com moderação"""
    print("\n🎛️ EXEMPLO 3: Handler Personalizado")
    print("-" * 60)
    
    handler_example = """
from telegram.ext import MessageHandler, filters
from src.telegram_moderation_middleware import create_moderation_middleware

class ModeratedMessageHandler:
    \"\"\"Handler que inclui moderação automática\"\"\"
    
    def __init__(self, admin_ids=None):
        self.middleware = create_moderation_middleware(admin_ids)
        self.message_count = 0
    
    async def handle_message(self, update, context):
        \"\"\"Processa mensagem com moderação integrada\"\"\"
        
        # 1. Verificação de moderação
        can_proceed = await self.middleware.check_message(update, context)
        
        if not can_proceed:
            # Mensagem foi bloqueada pela moderação
            return
        
        # 2. Processar mensagem normalmente
        self.message_count += 1
        
        # Sua lógica normal do bot aqui
        user_name = update.effective_user.first_name
        message_text = update.message.text
        
        # Exemplo: resposta simples
        response = f"👋 Olá {user_name}! Recebi sua mensagem: {message_text[:50]}..."
        await update.message.reply_text(response)
        
        # Log da interação (opcional)
        print(f"Mensagem processada de {user_name}: {message_text[:30]}...")
    
    def get_handler(self):
        \"\"\"Retorna handler configurado para o bot\"\"\"
        return MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)

# Uso:
moderated_handler = ModeratedMessageHandler(admin_ids=[SEU_ADMIN_ID])
app.add_handler(moderated_handler.get_handler())
"""
    
    print("✨ **Vantagens do handler personalizado:**")
    print("   • Moderação transparente e automática")
    print("   • Fácil integração com lógica existente") 
    print("   • Logging e estatísticas integrados")
    print("   • Bypass automático para administradores")


# ============================================================================
# EXEMPLO 4: Configurações avançadas e personalização
# ============================================================================

def example_advanced_configuration():
    """Exemplo de configurações avançadas"""
    print("\n⚙️ EXEMPLO 4: Configurações Avançadas")
    print("-" * 60)
    
    print("🔧 **Configurações no .env:**")
    env_example = """
# Ativar/desativar moderação
ADULT_MODERATION_ENABLED=True

# Sensibilidade (low, medium, high)  
MODERATION_SENSITIVITY=medium

# Ações automáticas
AUTO_WARN_MILD=True
AUTO_FILTER_MODERATE=True
AUTO_BLOCK_SEVERE=True

# Durações
QUARANTINE_DURATION_HOURS=24
BLOCK_DURATION_HOURS=72

# Limites antes de ações
MAX_VIOLATIONS_BEFORE_QUARANTINE=3
MAX_VIOLATIONS_BEFORE_BLOCK=5
MAX_VIOLATIONS_BEFORE_BAN=10
"""
    
    print(env_example)
    
    print("📊 **Configuração personalizada no código:**")
    custom_config = """
# Configurações personalizadas por grupo/chat
CHAT_CONFIGS = {
    -1001234567890: {  # ID do grupo
        'sensitivity': 'high',
        'auto_filter': True,
        'admin_notifications': True
    },
    -1009876543210: {  # Outro grupo  
        'sensitivity': 'low',
        'auto_filter': False,
        'warnings_only': True
    }
}

# Aplicar configuração por chat
async def get_chat_config(chat_id):
    return CHAT_CONFIGS.get(chat_id, DEFAULT_CONFIG)
"""
    
    print(custom_config)


# ============================================================================
# EXEMPLO 5: Monitoramento e relatórios
# ============================================================================

def example_monitoring_reports():
    """Exemplo de monitoramento e relatórios"""
    print("\n📊 EXEMPLO 5: Monitoramento e Relatórios")
    print("-" * 60)
    
    # Mostrar estatísticas reais
    try:
        stats = get_moderation_stats(days=7)
        print("📈 **Estatísticas atuais (últimos 7 dias):**")
        
        current = stats['current_stats']
        print(f"   Verificações hoje: {current['total_checks_today']:,}")
        print(f"   Bloqueios hoje: {current['blocks_today']:,}")
        print(f"   Avisos hoje: {current['warnings_today']:,}")
        
        if stats['action_stats']:
            print(f"\n📋 **Ações por tipo:**")
            for action, count in sorted(stats['action_stats'].items(), key=lambda x: x[1], reverse=True)[:5]:
                severity, action_type = action.split('_', 1)
                print(f"   {severity} - {action_type}: {count:,}")
        
        if stats['top_violators']:
            print(f"\n🚨 **Top 3 violadores:**")
            for i, violator in enumerate(stats['top_violators'][:3], 1):
                print(f"   {i}. User {violator['user_id']}: {violator['violations']} violações")
    
    except Exception as e:
        print(f"   ❌ Erro ao obter estatísticas: {e}")
    
    print(f"\n💡 **Comandos para relatórios:**")
    print(f"   python tools/moderation_manager.py --stats --days 30")
    print(f"   python tools/moderation_manager.py --export-report")
    print(f"   python tools/moderation_manager.py --user USER_ID")


# ============================================================================
# FUNÇÃO PRINCIPAL - EXECUTA TODOS OS EXEMPLOS
# ============================================================================

def main():
    """Executa todos os exemplos de integração"""
    print("🚀 EXEMPLOS DE INTEGRAÇÃO - MODERAÇÃO TELEGRAM")
    print("=" * 70)
    
    # Verificar se sistema está configurado
    if not config.moderation['enabled']:
        print("⚠️ Sistema de moderação desabilitado no config")
        print("   Para ativar: ADULT_MODERATION_ENABLED=True no .env")
        print()
    
    # Executar exemplos
    example_basic_middleware_setup()
    example_admin_commands()
    example_custom_handler()
    example_advanced_configuration()
    example_monitoring_reports()
    
    print("\n" + "=" * 70)
    print("✅ **TODOS OS EXEMPLOS DEMONSTRADOS!")
    print("\n📖 **Próximos passos:**")
    print("   1. Configure os IDs de administrador")
    print("   2. Integre o middleware ao seu bot")
    print("   3. Teste com mensagens de diferentes severidades")
    print("   4. Configure padrões personalizados se necessário")
    print("   5. Configure monitoramento e alertas")
    
    print(f"\n🔗 **Arquivos relacionados:**")
    print(f"   src/adult_content_moderator.py - Sistema principal")
    print(f"   src/telegram_moderation_middleware.py - Middleware")
    print(f"   tools/moderation_manager.py - Utilitário de gestão")
    print(f"   config.py - Configurações")


if __name__ == "__main__":
    main()