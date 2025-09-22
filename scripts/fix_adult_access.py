#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE CORREÇÃO - ATIVAR MODO ADULTO MANUALMENTE
=================================================

Este script força a ativação do modo adulto para um usuário específico
quando há problemas de sincronização entre os sistemas.
"""

import sqlite3
import os

def fix_adult_access(user_id):
    """Corrige acesso adulto para usuário específico"""
    
    # Caminho do banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'memoria', 'user_profiles.db')
    
    if not os.path.exists(db_path):
        print(f"ERRO: Banco de dados nao encontrado: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar se usuário existe
            cursor.execute("SELECT user_id, user_name, has_mature_access FROM profiles WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                print(f"ERRO: Usuario {user_id} nao encontrado no banco de dados")
                return False
            
            print(f"Usuario encontrado: {user[1]} (ID: {user[0]})")
            print(f"Status atual: has_mature_access = {user[2]}")
            
            # Atualizar para ativar modo adulto
            cursor.execute("""
                UPDATE profiles 
                SET has_mature_access = 1,
                    user_age = '18+',
                    adult_intensity_level = COALESCE(adult_intensity_level, 1),
                    adult_interaction_style = COALESCE(adult_interaction_style, 'romantic')
                WHERE user_id = ?
            """, (user_id,))
            
            if cursor.rowcount > 0:
                print("SUCESSO: Modo adulto ativado com sucesso!")
                
                # Verificar atualização
                cursor.execute("SELECT has_mature_access, user_age FROM profiles WHERE user_id = ?", (user_id,))
                updated = cursor.fetchone()
                print(f"Novo status: has_mature_access = {updated[0]}, user_age = {updated[1]}")
                
                return True
            else:
                print("ERRO: Falha ao atualizar o banco de dados")
                return False
                
    except Exception as e:
        print(f"ERRO: Erro ao acessar banco de dados: {e}")
        return False

def main():
    """Função principal"""
    print("CORREÇÃO DE ACESSO ADULTO - ERON.IA")
    print("=" * 50)
    
    # ID do usuário baseado nos logs que vi
    user_id = "7405892492"  # Romario
    
    print(f"Corrigindo acesso adulto para usuario: {user_id}")
    print()
    
    if fix_adult_access(user_id):
        print()
        print("CORREÇÃO CONCLUÍDA!")
        print()
        print("O usuario agora tem acesso aos comandos adultos:")
        print("   - /devassa_config")
        print("   - /devassa_off") 
        print("   - /adult_status")
        print("   - Todos os comandos de configuração adulta")
        print()
        print("Reinicie o bot para aplicar as mudancas!")
    else:
        print()
        print("CORREÇÃO FALHOU!")
        print("   Verifique os logs acima para mais detalhes.")

if __name__ == "__main__":
    main()