"""
Sistema unificado de mensagens para ambas as plataformas (Web e Telegram)
Garante consistência na personalidade e apresentação do bot
"""

class UnifiedMessages:
    """Classe para centralizar e padronizar mensagens do sistema"""
    
    # Mensagens de boas-vindas
    WELCOME_MESSAGES = {
        'first_time': {
            'web': "🚀 **Bem-vindo ao Eron.IA!**\n\nEu sou seu assistente inteligente personalizado. Para começar, vamos configurar sua experiência!",
            'telegram': "🚀 *Bem-vindo ao Eron.IA!*\n\nEu sou seu assistente inteligente personalizado. Para começar, vamos configurar sua experiência!"
        },
        'returning': {
            'web': "👋 **Que bom te ver de novo!**\n\nEstou pronto para continuar nossa conversa.",
            'telegram': "👋 *Que bom te ver de novo!*\n\nEstou pronto para continuar nossa conversa."
        }
    }
    
    # Mensagens de personalização
    PERSONALIZATION_MESSAGES = {
        'start': {
            'web': "🎨 **Vamos personalizar sua experiência!**\n\nResponda algumas perguntas para que eu possa te atender melhor:",
            'telegram': "🎨 *Vamos personalizar sua experiência!*\n\nResponda algumas perguntas para que eu possa te atender melhor:"
        },
        'user_name': {
            'web': "👤 **Como você gostaria de ser chamado?**\n\nDigite seu nome ou apelido preferido:",
            'telegram': "👤 Como você gostaria de ser chamado?\n\nDigite seu nome ou apelido preferido:"
        },
        'bot_name': {
            'web': "🤖 **E quanto a mim? Como você gostaria que eu me chamasse?**\n\nEscolha um nome que você ache legal:",
            'telegram': "🤖 E quanto a mim? Como você gostaria que eu me chamasse?\n\nEscolha um nome que você ache legal:"
        },
        'personality': {
            'web': "🎭 **Como você gostaria que eu me comportasse?**\n\nPosso ser mais formal, casual, amigável...",
            'telegram': "🎭 Como você gostaria que eu me comportasse?\n\nPosso ser mais formal, casual, amigável..."
        },
        'complete': {
            'web': "✅ **Personalização concluída com sucesso!**\n\nAgora estou configurado do jeito que você gosta. Vamos conversar?",
            'telegram': "✅ *Personalização concluída com sucesso!*\n\nAgora estou configurado do jeito que você gosta. Vamos conversar?"
        }
    }
    
    # Mensagens de erro padronizadas
    ERROR_MESSAGES = {
        'general': {
            'web': "❌ **Ops! Algo deu errado.**\n\nTente novamente em alguns segundos.",
            'telegram': "❌ Ops! Algo deu errado.\n\nTente novamente em alguns segundos."
        },
        'not_found': {
            'web': "🔍 **Não encontrei essa informação.**\n\nPoderia reformular sua pergunta?",
            'telegram': "🔍 Não encontrei essa informação.\n\nPoderia reformular sua pergunta?"
        },
        'invalid_input': {
            'web': "⚠️ **Entrada inválida.**\n\nPor favor, verifique o que você digitou.",
            'telegram': "⚠️ Entrada inválida.\n\nPor favor, verifique o que você digitou."
        }
    }
    
    # Mensagens de confirmação
    CONFIRMATION_MESSAGES = {
        'reset': {
            'web': "🔄 **Tem certeza que deseja resetar tudo?**\n\nIsso apagará sua personalização atual.",
            'telegram': "🔄 Tem certeza que deseja resetar tudo?\n\nIsso apagará sua personalização atual."
        },
        'save': {
            'web': "💾 **Configurações salvas com sucesso!**\n\nSuas preferências foram atualizadas.",
            'telegram': "💾 Configurações salvas com sucesso!\n\nSuas preferências foram atualizadas."
        }
    }
    
    # Mensagens de ajuda
    HELP_MESSAGES = {
        'commands': {
            'web': """📋 **Comandos disponíveis:**
            
• **Personalizar** - Configure sua experiência
• **Preferências** - Ajuste estilo de conversa  
• **Limpar** - Reset completo do sistema
• **Emoções** - Visualize estado emocional
• **Ajuda** - Lista de comandos""",
            
            'telegram': """📋 *Comandos disponíveis:*

/start - Iniciar conversa
/personalize - Configurar experiência
/clear - Reset completo
/preferences - Ajustar preferências  
/emotions - Ver estado emocional
/help - Esta mensagem"""
        }
    }
    
    @staticmethod
    def get_message(category, message_type, platform='telegram', **kwargs):
        """
        Retorna mensagem formatada para a plataforma específica
        
        Args:
            category: Categoria da mensagem (ex: 'welcome', 'error')
            message_type: Tipo específico da mensagem
            platform: 'web' ou 'telegram'
            **kwargs: Variáveis para formatação da mensagem
        """
        try:
            message_dict = getattr(UnifiedMessages, f"{category.upper()}_MESSAGES")
            message = message_dict[message_type][platform]
            
            # Aplicar formatação se houver kwargs
            if kwargs:
                return message.format(**kwargs)
            return message
            
        except (AttributeError, KeyError):
            # Fallback para mensagem genérica
            return "Mensagem não encontrada." if platform == 'web' else "Mensagem não encontrada."
    
    @staticmethod
    def format_for_platform(text, platform='telegram'):
        """
        Formata texto para plataforma específica
        
        Args:
            text: Texto a ser formatado
            platform: 'web' ou 'telegram'
        """
        if platform == 'web':
            # Manter formatação markdown para web
            return text
        else:
            # Converter para formatação do Telegram
            text = text.replace('**', '*')  # Negrito
            text = text.replace('`', '`')   # Código (mantém igual)
            return text
    
    @staticmethod
    def get_personality_response(bot_name, user_name, message_type, platform='telegram'):
        """
        Gera resposta personalizada baseada no perfil do usuário
        
        Args:
            bot_name: Nome do bot
            user_name: Nome do usuário
            message_type: Tipo de resposta
            platform: Plataforma alvo
        """
        responses = {
            'greeting': {
                'web': f"👋 **Olá, {user_name}!**\n\nEu sou {bot_name}, seu assistente personalizado. Como posso ajudar hoje?",
                'telegram': f"👋 Olá, {user_name}!\n\nEu sou {bot_name}, seu assistente personalizado. Como posso ajudar hoje?"
            },
            'name_question': {
                'web': f"😊 **Meu nome é {bot_name}!**\n\nFoi você quem escolheu esse nome para mim.",
                'telegram': f"😊 Meu nome é {bot_name}!\n\nFoi você quem escolheu esse nome para mim."
            },
            'ready': {
                'web': f"🚀 **{bot_name} aqui, {user_name}!**\n\nEstou pronto para nossa conversa. O que você gostaria de saber?",
                'telegram': f"🚀 {bot_name} aqui, {user_name}!\n\nEstou pronto para nossa conversa. O que você gostaria de saber?"
            }
        }
        
        return responses.get(message_type, {}).get(platform, "Olá! Como posso ajudar?")

# Função de conveniência para uso direto
def get_unified_message(category, message_type, platform='telegram', **kwargs):
    """Função wrapper para fácil acesso às mensagens unificadas"""
    return UnifiedMessages.get_message(category, message_type, platform, **kwargs)