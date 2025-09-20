#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 VERIFICADOR DE MODO ADULTO
Sistema para identificar quando chat Web ou Telegram está no modo adulto
"""

import os
import sys
import sqlite3
from datetime import datetime

# Adicionar o diretório raiz ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_web_adult_mode(user_id: str) -> dict:
    """
    Verificar se usuário está no modo adulto na interface Web
    """
    try:
        # Conectar ao banco de perfis
        conn = sqlite3.connect('memoria/user_profiles.db')
        cursor = conn.cursor()
        
        # Buscar perfil do usuário
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        conn.close()
        
        if not profile:
            return {'web_adult_mode': False, 'reason': 'Usuário não encontrado'}
        
        # Verificar idade e habilitação
        user_age = int(profile[6]) if profile[6] and profile[6].isdigit() else 0
        age_eligible = user_age >= 18
        adult_enabled = bool(profile[15]) if len(profile) > 15 else False  # adult_mode_enabled
        
        return {
            'web_adult_mode': age_eligible and adult_enabled,
            'age_eligible': age_eligible,
            'adult_enabled': adult_enabled,
            'user_age': user_age,
            'platform': 'web'
        }
        
    except Exception as e:
        return {'web_adult_mode': False, 'error': str(e)}

def check_telegram_adult_mode(user_id: str) -> dict:
    """
    Verificar se usuário está no modo adulto no Telegram
    """
    try:
        # Importar sistema de verificação do Telegram
        from core.check import check_age
        from telegram_bot.handlers.adult_integration import is_advanced_adult_active
        
        # Verificar status básico
        adult_status = check_age(user_id)
        
        # Verificar sistema avançado
        advanced_active = is_advanced_adult_active(user_id)
        
        return {
            'telegram_adult_mode': adult_status.get('adult_mode_active', False),
            'advanced_system': advanced_active,
            'is_adult': adult_status.get('is_adult', False),
            'age_verified': adult_status.get('age_verified', False),
            'platform': 'telegram'
        }
        
    except Exception as e:
        return {'telegram_adult_mode': False, 'error': str(e)}

def check_unified_adult_mode(user_id: str) -> dict:
    """
    Verificar modo adulto em ambas as plataformas
    """
    web_status = check_web_adult_mode(user_id)
    telegram_status = check_telegram_adult_mode(user_id)
    
    return {
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'web': web_status,
        'telegram': telegram_status,
        'unified_adult_mode': web_status.get('web_adult_mode', False) or telegram_status.get('telegram_adult_mode', False)
    }

def get_adult_mode_indicators() -> dict:
    """
    Retornar indicadores para identificar modo adulto
    """
    return {
        'web_indicators': {
            'session_key': 'adult_mode_active',
            'url_patterns': ['/adult/', '/adult_dashboard', '/adult_config'],
            'database_field': 'adult_mode_enabled',
            'verification_route': '/age_verification'
        },
        'telegram_indicators': {
            'commands': ['/adult_mode', '/adult_config', '/adult_train', '/adult_status'],
            'context_key': 'adult_mode_active',
            'advanced_system': 'is_advanced_adult_active()',
            'personality_active': 'get_adult_personality_context()'
        },
        'common_indicators': {
            'age_requirement': 18,
            'database_tables': ['adult_profiles', 'adult_safety', 'adult_vocabulary'],
            'memory_keys': ['adult_mode', 'personality_type', 'intimacy_level']
        }
    }

def display_status(user_id: str):
    """
    Exibir status completo do modo adulto
    """
    status = check_unified_adult_mode(user_id)
    indicators = get_adult_mode_indicators()
    
    print("🔍 STATUS DO MODO ADULTO")
    print("=" * 50)
    print(f"👤 Usuário: {user_id}")
    print(f"⏰ Verificação: {status['timestamp']}")
    print()
    
    # Status Web
    web = status['web']
    print("🌐 INTERFACE WEB:")
    print(f"   🔞 Modo Adulto: {'✅ ATIVO' if web.get('web_adult_mode') else '❌ INATIVO'}")
    if 'user_age' in web:
        print(f"   👶 Idade: {web['user_age']} anos")
        print(f"   📅 Elegível: {'✅' if web.get('age_eligible') else '❌'}")
        print(f"   ⚙️  Habilitado: {'✅' if web.get('adult_enabled') else '❌'}")
    
    if 'error' in web:
        print(f"   ❌ Erro: {web['error']}")
    
    print()
    
    # Status Telegram
    telegram = status['telegram']
    print("📱 TELEGRAM BOT:")
    print(f"   🔞 Modo Adulto: {'✅ ATIVO' if telegram.get('telegram_adult_mode') else '❌ INATIVO'}")
    print(f"   🎯 Sistema Avançado: {'✅ ATIVO' if telegram.get('advanced_system') else '❌ INATIVO'}")
    if 'is_adult' in telegram:
        print(f"   👤 É Adulto: {'✅' if telegram.get('is_adult') else '❌'}")
        print(f"   ✅ Verificado: {'✅' if telegram.get('age_verified') else '❌'}")
    
    if 'error' in telegram:
        print(f"   ❌ Erro: {telegram['error']}")
    
    print()
    
    # Status Unificado
    print("🔄 STATUS UNIFICADO:")
    unified = status['unified_adult_mode']
    print(f"   🎯 Modo Adulto Ativo: {'✅ SIM' if unified else '❌ NÃO'}")
    
    # Indicadores
    print()
    print("📋 COMO IDENTIFICAR:")
    print("🌐 Web:")
    for pattern in indicators['web_indicators']['url_patterns']:
        print(f"   - URL contém: {pattern}")
    print(f"   - Session: {indicators['web_indicators']['session_key']}")
    
    print("📱 Telegram:")
    for command in indicators['telegram_indicators']['commands']:
        print(f"   - Comando: {command}")
    print(f"   - Context: {indicators['telegram_indicators']['context_key']}")

if __name__ == "__main__":
    print("🤖 ERON.IA - VERIFICADOR DE MODO ADULTO")
    print("=" * 50)
    
    # Teste com usuário exemplo
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = input("Digite o ID do usuário para verificar: ")
    
    if user_id:
        display_status(user_id)
    else:
        print("❌ ID de usuário não fornecido!")
        
        # Mostrar indicadores gerais
        indicators = get_adult_mode_indicators()
        print()
        print("📋 INDICADORES GERAIS:")
        print("🌐 Web - Verificar se:")
        print("   - URL contém '/adult/'")
        print("   - Session['adult_mode_active'] = True")
        print("   - Usuário tem >= 18 anos")
        print()
        print("📱 Telegram - Verificar se:")
        print("   - Usuário usou comandos /adult_*")
        print("   - is_advanced_adult_active() retorna True")
        print("   - Perfil adulto existe no banco")