"""
Sistema de verificação e controle de funcionalidades adultas
"""
import sqlite3
import os
from datetime import datetime

class AdultAccessSystem:
    """Sistema para gerenciar acesso a conteúdo adulto"""
    
    def __init__(self):
        # Usar o mesmo banco de perfis
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'memoria', 'user_profiles.db')
        self.db_path = db_path
    
    def get_connection(self):
        """Obter conexão com o banco"""
        return sqlite3.connect(self.db_path)
    
    def check_age(self, user_id):
        """Verificar status de idade e modo adulto de um usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_age, has_mature_access, adult_intensity_level,
                       adult_interaction_style, created_at
                FROM profiles 
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                user_age, has_mature_access, adult_intensity, adult_style, created_at = row
                
                # Verificar se é maior de idade
                is_adult = False
                if user_age:
                    try:
                        is_adult = int(user_age) >= 18
                    except (ValueError, TypeError):
                        is_adult = False
                
                return {
                    'user_age': user_age,
                    'is_adult': is_adult,
                    'adult_mode_active': bool(has_mature_access),
                    'adult_intensity_level': adult_intensity or 1,
                    'interaction_style': adult_style or 'romantic',
                    'activation_date': created_at,
                    'gender': 'não especificado'  # Pode ser expandido depois
                }
            
            return {
                'user_age': None,
                'is_adult': False,
                'adult_mode_active': False,
                'adult_intensity_level': 1,
                'interaction_style': 'romantic',
                'activation_date': None,
                'gender': 'não especificado'
            }
    
    def activate_adult_mode(self, user_id):
        """Ativar modo adulto para um usuário"""
        user_data = self.check_age(user_id)
        
        # Só ativar se for maior de idade
        if not user_data['is_adult']:
            return False
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE profiles 
                SET has_mature_access = 1,
                    adult_intensity_level = COALESCE(adult_intensity_level, 1),
                    adult_interaction_style = COALESCE(adult_interaction_style, 'romantic')
                WHERE user_id = ?
            """, (user_id,))
            
            return cursor.rowcount > 0
    
    def deactivate_adult_mode(self, user_id):
        """Desativar modo adulto para um usuário"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE profiles 
                SET has_mature_access = 0
                WHERE user_id = ?
            """, (user_id,))
            
            return cursor.rowcount > 0
    
    def set_adult_preferences(self, user_id, intensity=None, style=None, preferences=None, boundaries=None):
        """Configurar preferências adultas de um usuário"""
        user_data = self.check_age(user_id)
        if not user_data['adult_mode_active']:
            return False
        
        update_fields = []
        values = []
        
        if intensity is not None:
            update_fields.append("adult_intensity_level = ?")
            values.append(intensity)
        
        if style is not None:
            update_fields.append("adult_interaction_style = ?")
            values.append(style)
        
        if preferences is not None:
            update_fields.append("adult_content_preferences = ?")
            values.append(','.join(preferences) if isinstance(preferences, list) else preferences)
        
        if boundaries is not None:
            update_fields.append("adult_boundaries = ?")
            values.append(','.join(boundaries) if isinstance(boundaries, list) else boundaries)
        
        if not update_fields:
            return False
        
        values.append(user_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE profiles SET {', '.join(update_fields)} WHERE user_id = ?"
            cursor.execute(query, values)
            return cursor.rowcount > 0
    
    def set_adult_gender(self, user_id, gender):
        """Definir gênero para modo adulto (pode ser expandido)"""
        return self.set_adult_preferences(user_id)  # Por enquanto não faz nada específico
    
    def get_adult_preferences(self, user_id):
        """Obter preferências adultas detalhadas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT adult_intensity_level, adult_interaction_style,
                       adult_content_preferences, adult_boundaries
                FROM profiles 
                WHERE user_id = ? AND has_mature_access = 1
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                intensity, style, preferences, boundaries = row
                return {
                    'intensity_level': intensity or 1,
                    'interaction_style': style or 'romantic',
                    'content_preferences': preferences.split(',') if preferences else [],
                    'boundaries': boundaries.split(',') if boundaries else []
                }
            
            return None

# Instância global do sistema
_adult_system = AdultAccessSystem()

# Funções de conveniência para compatibilidade
def check_age(user_id=None):
    """Verificar idade e status adulto (compatibilidade)"""
    if user_id:
        return _adult_system.check_age(user_id)
    else:
        # Para compatibilidade com código antigo
        try:
            idade = int(input("Por favor, informe sua idade: "))
            return idade >= 18
        except ValueError:
            print("Idade inválida.")
            return False

def activate_adult_mode(user_id):
    """Ativar modo adulto"""
    return _adult_system.activate_adult_mode(user_id)

def deactivate_adult_mode(user_id):
    """Desativar modo adulto"""
    return _adult_system.deactivate_adult_mode(user_id)

def set_adult_gender(user_id, gender):
    """Definir gênero adulto"""
    return _adult_system.set_adult_gender(user_id, gender)

def get_adult_preferences(user_id):
    """Obter preferências adultas"""
    return _adult_system.get_adult_preferences(user_id)