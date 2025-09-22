#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir warnings PTB nos ConversationHandlers (versão precisa)
"""

import re
import os
import shutil

def fix_ptb_warnings():
    """Corrige warnings PTB adicionando per_message=True apenas nos ConversationHandlers"""
    
    file_path = "telegram_bot/telegram_bot_original.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    print(f"🔧 CORREÇÃO PTB WARNINGS - VERSÃO PRECISA")
    print("=" * 60)
    
    # Backup
    backup_path = f"{file_path}.backup_v3"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    
    # Lê o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_applied = 0
    
    # Padrão específico para ConversationHandler com fechamento correto
    # Procura por: nome_handler = ConversationHandler(... até encontrar )
    pattern = r'(\w+_handler\s*=\s*ConversationHandler\s*\([^}]*?}\s*,\s*fallbacks=\[[^\]]*?\]\s*)(,\s*allow_reentry=True)?\s*\)'
    
    def replace_conversation_handler(match):
        nonlocal fixes_applied
        
        handler_content = match.group(1)
        allow_reentry = match.group(2) if match.group(2) else ""
        
        # Verifica se já tem per_message
        if 'per_message=' in handler_content:
            return match.group(0)  # Não altera se já tem
        
        fixes_applied += 1
        
        # Reconstrói com per_message=True
        result = handler_content + allow_reentry + ',\n        per_message=True\n    )'
        return result
    
    # Aplica as correções
    new_content = re.sub(pattern, replace_conversation_handler, content, flags=re.DOTALL)
    
    if fixes_applied > 0:
        # Salva o arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {fixes_applied} ConversationHandlers corrigidos")
        print(f"📝 Arquivo atualizado: {file_path}")
        print("🎯 Parâmetro 'per_message=True' adicionado apenas aos ConversationHandlers!")
    else:
        print("⚠️  Nenhuma alteração necessária")
        
    print("\n" + "=" * 60)
    print("🏁 CORREÇÃO CONCLUÍDA")

if __name__ == "__main__":
    fix_ptb_warnings()