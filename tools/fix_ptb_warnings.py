#!/usr/bin/env python3
"""
🔧 CORREÇÃO DE WARNINGS PTB - TELEGRAM BOT
Fix para os warnings dos ConversationHandlers
"""

import re
import os

def corrigir_warnings_ptb():
    """Corrige warnings dos ConversationHandlers no Telegram Bot"""
    
    print('🔧 INICIANDO CORREÇÃO DE WARNINGS PTB')
    print('=' * 60)
    
    arquivo_bot = 'telegram_bot/telegram_bot_original.py'
    
    if not os.path.exists(arquivo_bot):
        print(f'❌ Arquivo {arquivo_bot} não encontrado!')
        return False
    
    print(f'📝 Lendo arquivo: {arquivo_bot}')
    
    # Ler arquivo
    with open(arquivo_bot, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Lista de ConversationHandlers para corrigir
    handlers_para_corrigir = [
        'personalization_handler',
        'change_user_age_handler', 
        'change_user_gender_handler',
        'change_bot_gender_handler',
        'change_language_handler',
        'change_topics_handler'
    ]
    
    alteracoes = 0
    
    for handler in handlers_para_corrigir:
        print(f'🔍 Procurando: {handler}')
        
        # Padrão para encontrar ConversationHandler sem per_message
        padrao = rf'({handler}\s*=\s*ConversationHandler\([^)]*?)(\s*allow_reentry=True\s*\))'
        
        def substituir(match):
            nonlocal alteracoes
            grupo1 = match.group(1)
            grupo2 = match.group(2)
            
            # Verificar se já tem per_message
            if 'per_message=' not in grupo1:
                # Adicionar per_message=True antes do fechamento
                if 'allow_reentry=True' in grupo2:
                    novo = grupo1 + ',\n        per_message=True' + grupo2
                else:
                    novo = grupo1 + ',\n        per_message=True\n    )'
                alteracoes += 1
                print(f'  ✅ Corrigido: {handler}')
                return novo
            return match.group(0)
        
        conteudo = re.sub(padrao, substituir, conteudo, flags=re.DOTALL)
    
    # Padrão alternativo para handlers sem allow_reentry
    handlers_simples = ['change_user_gender_handler', 'change_bot_gender_handler', 
                       'change_language_handler', 'change_topics_handler']
    
    for handler in handlers_simples:
        padrao_simples = rf'({handler}\s*=\s*ConversationHandler\([^)]*?fallbacks=[^)]*?\]\s*)\)'
        
        def substituir_simples(match):
            nonlocal alteracoes
            grupo = match.group(1)
            if 'per_message=' not in grupo:
                novo = grupo + ',\n        per_message=True\n    )'
                alteracoes += 1
                print(f'  ✅ Corrigido (simples): {handler}')
                return novo
            return match.group(0)
        
        conteudo = re.sub(padrao_simples, substituir_simples, conteudo, flags=re.DOTALL)
    
    # Corrigir também handlers adultos se existirem
    if 'adult_activation_handler' in conteudo:
        padrao_adult = r'(adult_activation_handler\s*=\s*ConversationHandler\([^}]*}[^)]*?fallbacks=[^)]*?\]\s*)\)'
        
        def substituir_adult(match):
            nonlocal alteracoes
            grupo = match.group(1)
            if 'per_message=' not in grupo:
                novo = grupo + ',\n            per_message=True\n        )'
                alteracoes += 1
                print('  ✅ Corrigido: adult_activation_handler')
                return novo
            return match.group(0)
        
        conteudo = re.sub(padrao_adult, substituir_adult, conteudo, flags=re.DOTALL)
    
    if alteracoes > 0:
        # Fazer backup
        backup_file = arquivo_bot + '.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(arquivo_bot, 'r', encoding='utf-8') as original:
                f.write(original.read())
        print(f'💾 Backup criado: {backup_file}')
        
        # Salvar arquivo corrigido
        with open(arquivo_bot, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f'\\n✅ CORREÇÕES APLICADAS!')
        print(f'📊 Total de alterações: {alteracoes}')
        print(f'💾 Arquivo atualizado: {arquivo_bot}')
        print(f'🔙 Backup disponível: {backup_file}')
        
    else:
        print('\\n⚠️  Nenhuma alteração necessária ou handlers não encontrados')
    
    return alteracoes > 0

def verificar_resultado():
    """Verifica se as correções foram aplicadas"""
    print('\\n🔍 VERIFICANDO RESULTADO')
    print('=' * 40)
    
    arquivo_bot = 'telegram_bot/telegram_bot_original.py'
    
    with open(arquivo_bot, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Contar ocorrências de per_message=True
    count_per_message = conteudo.count('per_message=True')
    count_conversation_handler = conteudo.count('ConversationHandler(')
    
    print(f'📊 ConversationHandlers encontrados: {count_conversation_handler}')
    print(f'✅ Com per_message=True: {count_per_message}')
    
    if count_per_message >= 5:  # Esperamos pelo menos 5 handlers corrigidos
        print('🎉 Correção aplicada com sucesso!')
        return True
    else:
        print('⚠️  Algumas correções podem não ter sido aplicadas')
        return False

if __name__ == '__main__':
    if corrigir_warnings_ptb():
        verificar_resultado()
        print('\\n🚀 Execute o sistema novamente para ver os warnings eliminados!')
    else:
        print('\\n❌ Nenhuma correção foi aplicada')