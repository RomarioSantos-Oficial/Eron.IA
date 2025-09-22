#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir warnings PTB nos ConversationHandlers
"""

import re
import os
import shutil

def fix_ptb_warnings():
    """Corrige warnings PTB adicionando per_message=True"""
    
    file_path = "telegram_bot/telegram_bot_original.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    print(f"🔧 INICIANDO CORREÇÃO DE WARNINGS PTB")
    print("=" * 60)
    
    # Backup
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    
    # Lê o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procura por ConversationHandlers sem per_message=True
    pattern = r'(\w+_handler\s*=\s*ConversationHandler\s*\([^)]*?)\)'
    
    fixes_applied = 0
    
    def replace_handler(match):
        nonlocal fixes_applied
        handler_content = match.group(1)
        
        # Verifica se já tem per_message
        if 'per_message=' in handler_content:
            return match.group(0)  # Não altera se já tem
        
        # Adiciona per_message=True antes do fechamento
        fixes_applied += 1
        return handler_content + ',\n        per_message=True\n    )'
    
    # Aplica as correções
    new_content = re.sub(pattern, replace_handler, content, flags=re.DOTALL)
    
    if fixes_applied > 0:
        # Salva o arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {fixes_applied} ConversationHandlers corrigidos")
        print(f"📝 Arquivo atualizado: {file_path}")
        print("🎯 Parâmetro 'per_message=True' adicionado com sucesso!")
        
        # Lista dos handlers encontrados
        handlers = re.findall(r'(\w+_handler)\s*=\s*ConversationHandler', content)
        if handlers:
            print("\n🔍 Handlers encontrados:")
            for handler in handlers:
                print(f"  • {handler}")
    else:
        print("⚠️  Nenhuma alteração necessária")
        print("   Todos os ConversationHandlers já possuem per_message definido")
    
    print("\n" + "=" * 60)
    print("🏁 CORREÇÃO CONCLUÍDA")

if __name__ == "__main__":
    fix_ptb_warnings()