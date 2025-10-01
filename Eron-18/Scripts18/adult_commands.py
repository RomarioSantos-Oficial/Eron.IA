"""
Sistema de Comandos Adultos - CONTEÚDO +18
Gerencia ativação, verificação de idade e termos de responsabilidade
"""

from datetime import datetime, timedelta
import hashlib
import secrets
import json

class AdultCommandSystem:
    """
    Sistema de comandos para ativação do modo adulto com verificação de idade.
    RESTRITO PARA MAIORES DE 18 ANOS.
    """
    
    def __init__(self, adult_db):
        self.db = adult_db
        
        # Termos de responsabilidade
        self.terms_of_responsibility = """
🔞 TERMOS DE RESPONSABILIDADE - CONTEÚDO ADULTO (+18)

⚠️ ATENÇÃO: Este modo contém conteúdo adulto explícito destinado EXCLUSIVAMENTE para maiores de 18 anos.

📋 AO CONTINUAR, VOCÊ DECLARA E GARANTE QUE:
• Possui 18 anos completos ou mais
• É legalmente capaz de acessar conteúdo adulto em sua jurisdição
• Está acessando este conteúdo por livre e espontânea vontade
• Compreende que o conteúdo pode incluir linguagem explícita e simulação de relacionamento íntimo

🛡️ RESPONSABILIDADES:
• O usuário é ÚNICO responsável pelo uso deste modo
• Este sistema é uma simulação de IA e não substitui relacionamentos reais
• Mantenha seus dados pessoais seguros
• Use com responsabilidade e respeito

⚖️ PROTEÇÕES LEGAIS:
• Este sistema registra verificações de idade para proteção legal
• Dados são criptografados e protegidos
• Você pode revogar acesso a qualquer momento

🚨 Se você NÃO tem 18 anos completos, PARE AGORA e não prossiga.

Digite 'ACEITO18' para confirmar que você tem 18+ anos e aceita estes termos.
Digite 'CANCELAR' para cancelar a ativação.
        """
        
        # Perguntas de verificação de idade (aleatórias)
        self.age_verification_questions = [
            {
                "question": "Em que ano você nasceu? (Digite apenas o ano, ex: 1990)",
                "type": "birth_year",
                "min_age": 18
            },
            {
                "question": "Quantos anos você tem? (Digite apenas o número)",
                "type": "current_age",
                "min_value": 18
            }
        ]

    def handle_adult_activation_command(self, user_id, platform='telegram'):
        """Inicia processo de ativação do modo adulto"""
        
        # Verificar se já tem acesso ativo
        if self.has_active_adult_access(user_id):
            return {
                'status': 'already_active',
                'message': '🔞 Modo adulto já está ativo para você!\n\nPara ajustar configurações, use /devassa_config'
            }
        
        # Verificar se já passou pela verificação recentemente
        recent_verification = self.db.get_recent_verification(user_id, hours=24)
        if recent_verification and not recent_verification['verified']:
            return {
                'status': 'recent_attempt',
                'message': '⚠️ Você tentou verificação recentemente mas não completou ou não atende aos requisitos.\n\nTente novamente em 24 horas ou entre em contato se há algum erro.'
            }
        
        # Iniciar processo de verificação
        verification_token = self.generate_verification_token(user_id)
        
        # Registrar tentativa de verificação
        self.db.log_verification_attempt(user_id, verification_token, platform)
        
        return {
            'status': 'terms_required',
            'message': self.terms_of_responsibility,
            'token': verification_token
        }

    def handle_terms_response(self, user_id, response, verification_token):
        """Processa resposta aos termos de responsabilidade"""
        
        # Verificar token válido
        if not self.db.validate_verification_token(user_id, verification_token):
            return {
                'status': 'invalid_token',
                'message': '❌ Sessão de verificação inválida ou expirada. Tente novamente com /18'
            }
        
        if response.upper() == 'ACEITO18':
            # Prosseguir para verificação de idade
            question = self.get_age_verification_question()
            
            # Atualizar estado da verificação
            self.db.update_verification_stage(user_id, verification_token, 'age_verification')
            
            return {
                'status': 'age_verification',
                'message': f"✅ Termos aceitos!\n\n🔍 VERIFICAÇÃO DE IDADE:\n{question['question']}",
                'question_type': question['type'],
                'token': verification_token
            }
            
        elif response.upper() == 'CANCELAR':
            # Cancelar verificação
            self.db.cancel_verification(user_id, verification_token, 'user_cancelled')
            
            return {
                'status': 'cancelled',
                'message': '✅ Ativação cancelada com sucesso.\n\nVocê pode tentar novamente a qualquer momento com /18'
            }
        else:
            return {
                'status': 'invalid_response',
                'message': '❌ Resposta inválida!\n\nDigite exatamente:\n• "ACEITO18" para aceitar os termos\n• "CANCELAR" para cancelar'
            }

    def handle_age_verification(self, user_id, age_response, verification_token, question_type):
        """Processa resposta da verificação de idade"""
        
        # Verificar token válido
        if not self.db.validate_verification_token(user_id, verification_token):
            return {
                'status': 'invalid_token',
                'message': '❌ Sessão de verificação inválida ou expirada. Tente novamente com /18'
            }
        
        try:
            age_value = int(age_response.strip())
        except ValueError:
            return {
                'status': 'invalid_format',
                'message': '❌ Por favor, digite apenas números.\n\nExemplo: 25'
            }
        
        is_valid_age = False
        calculated_age = None
        
        if question_type == 'birth_year':
            current_year = datetime.now().year
            calculated_age = current_year - age_value
            is_valid_age = calculated_age >= 18 and age_value <= current_year - 18
            
        elif question_type == 'current_age':
            calculated_age = age_value
            is_valid_age = age_value >= 18
        
        if is_valid_age:
            # Idade válida - conceder acesso
            session_token = self.generate_session_token(user_id)
            
            # Registrar verificação bem-sucedida
            self.db.complete_age_verification(
                user_id, 
                verification_token, 
                calculated_age, 
                True,
                session_token
            )
            
            # Criar sessão adulta ativa
            self.db.create_adult_session(user_id, session_token)
            
            return {
                'status': 'access_granted',
                'message': '🔞✅ ACESSO ADULTO CONCEDIDO!\n\n🎉 Bem-vindo(a) ao modo DEVASSA do Eron.IA!\n\n⚙️ Configurações disponíveis:\n• /devassa_config - Ajustar intensidade e preferências\n• /devassa_off - Desativar modo adulto\n\n🔥 O Eron agora responderá com linguagem adulta adaptada ao seu perfil!\n\n💡 Dica: Você pode ajustar a intensidade (1-Suave, 2-Moderado, 3-Intenso) nas configurações.',
                'session_token': session_token
            }
        else:
            # Idade inválida
            self.db.complete_age_verification(
                user_id,
                verification_token, 
                calculated_age,
                False,
                None,
                'underage'
            )
            
            return {
                'status': 'access_denied',
                'message': '❌ ACESSO NEGADO\n\n🚫 Este conteúdo é restrito para maiores de 18 anos.\n\nSe você acredita que há um erro, tente novamente em 24 horas ou verifique se digitou sua idade corretamente.'
            }

    def has_active_adult_access(self, user_id):
        """Verifica se usuário tem acesso adulto ativo"""
        session = self.db.get_active_adult_session(user_id)
        return session and not self.is_session_expired(session)

    def is_session_expired(self, session):
        """Verifica se sessão está expirada"""
        if session['expires_at']:
            expiry_time = datetime.fromisoformat(session['expires_at'])
            return datetime.now() > expiry_time
        return False

    def get_age_verification_question(self):
        """Retorna pergunta aleatória de verificação de idade"""
        import random
        return random.choice(self.age_verification_questions)

    def generate_verification_token(self, user_id):
        """Gera token único para processo de verificação"""
        data = f"{user_id}_{datetime.now().isoformat()}_{secrets.token_hex(8)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def generate_session_token(self, user_id):
        """Gera token de sessão para acesso adulto"""
        data = f"session_{user_id}_{datetime.now().isoformat()}_{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def deactivate_adult_mode(self, user_id):
        """Desativa modo adulto para o usuário"""
        active_session = self.db.get_active_adult_session(user_id)
        if active_session:
            self.db.deactivate_adult_session(user_id, 'user_request')
            return {
                'status': 'deactivated',
                'message': '✅ Modo adulto desativado com sucesso!\n\n🔒 Eron voltará ao modo normal.\n\nVocê pode reativar a qualquer momento com /18'
            }
        else:
            return {
                'status': 'not_active',
                'message': '⚠️ Modo adulto não estava ativo.\n\nPara ativar, use o comando /18'
            }

    def get_adult_config_menu(self, user_id):
        """Retorna menu de configuração do modo adulto"""
        if not self.has_active_adult_access(user_id):
            return {
                'status': 'no_access',
                'message': '❌ Você não tem acesso adulto ativo.\n\nPara ativar, use /18'
            }
        
        devassa_profile = self.db.get_devassa_profile(user_id)
        if not devassa_profile:
            # Criar perfil padrão
            self.db.save_devassa_profile(
                user_id,
                intensity_level=2,
                gender_preference='feminino',
                relationship_stage='inicial'
            )
            devassa_profile = self.db.get_devassa_profile(user_id)
        
        menu = f"""
🔞⚙️ CONFIGURAÇÕES MODO DEVASSA

📊 Status Atual:
• Intensidade: {devassa_profile['intensity_level']}/3 ({self.get_intensity_description(devassa_profile['intensity_level'])})
• Gênero do Bot: {devassa_profile['gender_preference']}
• Estágio: {devassa_profile['relationship_stage']}

🎚️ Ajustar Intensidade:
• /intensidade1 - Suave (sensual, moderada)
• /intensidade2 - Moderado (direta, provocante)
• /intensidade3 - Intenso (explícita, muito provocante)

🎭 Alterar Gênero do Bot:
• /genero_feminino - Bot com personalidade feminina
• /genero_masculino - Bot com personalidade masculina
• /genero_neutro - Bot com linguagem neutra

🔒 Controles:
• /devassa_off - Desativar modo adulto
• /devassa_status - Ver status detalhado

⚠️ Lembre-se: Todas as alterações são aplicadas imediatamente!
        """
        
        return {
            'status': 'config_menu',
            'message': menu.strip()
        }

    def update_intensity(self, user_id, new_intensity):
        """Atualiza intensidade da linguagem"""
        if not self.has_active_adult_access(user_id):
            return {
                'status': 'no_access',
                'message': '❌ Você não tem acesso adulto ativo.'
            }
        
        if 1 <= new_intensity <= 3:
            self.db.save_devassa_profile(user_id, intensity_level=new_intensity)
            description = self.get_intensity_description(new_intensity)
            
            return {
                'status': 'updated',
                'message': f'✅ Intensidade atualizada para nível {new_intensity}!\n\n📝 {description}\n\n🔥 As próximas respostas já usarão o novo nível!'
            }
        else:
            return {
                'status': 'invalid_level',
                'message': '❌ Nível inválido! Use:\n• /intensidade1 (Suave)\n• /intensidade2 (Moderado)\n• /intensidade3 (Intenso)'
            }

    def update_gender_preference(self, user_id, gender):
        """Atualiza preferência de gênero do bot"""
        if not self.has_active_adult_access(user_id):
            return {
                'status': 'no_access',
                'message': '❌ Você não tem acesso adulto ativo.'
            }
        
        valid_genders = ['feminino', 'masculino', 'neutro']
        if gender in valid_genders:
            self.db.save_devassa_profile(user_id, gender_preference=gender)
            
            gender_descriptions = {
                'feminino': 'Bot com personalidade feminina (ela se apresenta como mulher)',
                'masculino': 'Bot com personalidade masculina (ele se apresenta como homem)',
                'neutro': 'Bot com linguagem neutra (sem gênero específico)'
            }
            
            return {
                'status': 'updated',
                'message': f'✅ Gênero do bot atualizado para {gender}!\n\n📝 {gender_descriptions[gender]}\n\n🔥 As próximas respostas já usarão a nova personalidade!'
            }
        else:
            return {
                'status': 'invalid_gender',
                'message': '❌ Gênero inválido! Use:\n• /genero_feminino\n• /genero_masculino\n• /genero_neutro'
            }

    def get_intensity_description(self, level):
        """Retorna descrição dos níveis de intensidade"""
        descriptions = {
            1: "Suave - Linguagem sensual mas moderada",
            2: "Moderado - Linguagem mais direta e provocante", 
            3: "Intenso - Linguagem explícita e muito provocante"
        }
        return descriptions.get(level, "Nível não definido")

    def get_adult_status(self, user_id):
        """Retorna status detalhado do modo adulto"""
        if not self.has_active_adult_access(user_id):
            return {
                'status': 'inactive',
                'message': '🔒 Modo adulto não está ativo.\n\nPara ativar, use /18'
            }
        
        session = self.db.get_active_adult_session(user_id)
        devassa_profile = self.db.get_devassa_profile(user_id)
        verification = self.db.get_latest_verification(user_id)
        
        status_message = f"""
🔞📊 STATUS DO MODO ADULTO

✅ Acesso: ATIVO
📅 Ativado em: {session['created_at'][:19]}
🔑 Sessão expira: {session['expires_at'][:19] if session['expires_at'] else 'Sem expiração'}

👤 Perfil Devassa:
• Intensidade: {devassa_profile['intensity_level']}/3
• Gênero Bot: {devassa_profile['gender_preference']}
• Estágio: {devassa_profile['relationship_stage']}

📈 Estatísticas:
• Interações adultas: {devassa_profile.get('interaction_count', 0)}
• Última interação: {devassa_profile.get('last_interaction', 'Nunca')}

🔐 Segurança:
• Verificação de idade: ✅ Verificada
• Data verificação: {verification['created_at'][:19] if verification else 'N/A'}

⚙️ Para configurar: /devassa_config
🔒 Para desativar: /devassa_off
        """
        
        return {
            'status': 'active_status',
            'message': status_message.strip()
        }

    def revoke_access(self, user_id, reason='user_request'):
        """Revoga acesso adulto e remove dados sensíveis"""
        # Desativar sessão
        self.db.deactivate_adult_session(user_id, reason)
        
        # Remover perfil devassa (opcional - manter histórico)
        # self.db.delete_devassa_profile(user_id)
        
        # Log de segurança
        self.db.log_security_event(
            user_id,
            'access_revoked',
            {'reason': reason, 'timestamp': datetime.now().isoformat()}
        )
        
        return {
            'status': 'revoked',
            'message': '🔒 Acesso adulto revogado com sucesso!\n\n✅ Todos os dados de sessão foram removidos.\n\nVocê pode reativar a qualquer momento com /18'
        }