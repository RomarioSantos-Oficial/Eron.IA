#!/usr/bin/env python3
"""
Script para corrigir as variáveis globais problemáticas no telegram_bot.py
Substitui sequential_setup_data, sequential_step e adult_access por context.user_data
"""

import re

def fix_global_variables():
    file_path = r"c:\Users\limar\Desktop\Nova pasta\Eron.IA\telegram_bot\telegram_bot.py"
    
    # Ler o arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituições padrão
    substitutions = [
        # sequential_setup_data[user_id] -> context.user_data['sequential_setup_data']
        (r'sequential_setup_data\[user_id\]', "context.user_data['sequential_setup_data']"),
        
        # sequential_step[user_id] -> context.user_data['sequential_step']
        (r'sequential_step\[user_id\]', "context.user_data['sequential_step']"),
        
        # adult_access[user_id] -> context.user_data['adult_access']
        (r'adult_access\[user_id\]', "context.user_data['adult_access']"),
        
        # sequential_step.get(user_id -> context.user_data.get('sequential_step'
        (r'sequential_step\.get\(user_id', "context.user_data.get('sequential_step'"),
        
        # adult_access.get(user_id -> context.user_data.get('adult_access'
        (r'adult_access\.get\(user_id', "context.user_data.get('adult_access'"),
        
        # user_id in sequential_step -> 'sequential_step' in context.user_data
        (r'user_id in sequential_step', "'sequential_step' in context.user_data"),
        
        # user_id in sequential_setup_data -> 'sequential_setup_data' in context.user_data
        (r'user_id in sequential_setup_data', "'sequential_setup_data' in context.user_data"),
        
        # del sequential_setup_data[user_id] -> context.user_data.pop('sequential_setup_data', None)
        (r'del sequential_setup_data\[user_id\]', "context.user_data.pop('sequential_setup_data', None)"),
        
        # del sequential_step[user_id] -> context.user_data.pop('sequential_step', None)
        (r'del sequential_step\[user_id\]', "context.user_data.pop('sequential_step', None)"),
    ]
    
    # Aplicar substituições
    for pattern, replacement in substitutions:
        content = re.sub(pattern, replacement, content)
    
    # Salvar o arquivo modificado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Variáveis globais corrigidas com sucesso!")
    print("Substituições realizadas:")
    for pattern, replacement in substitutions:
        count = len(re.findall(pattern, content))
        if count > 0:
            print(f"  - {pattern} -> {replacement} ({count} ocorrências)")

if __name__ == "__main__":
    fix_global_variables()