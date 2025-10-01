import os
import sys
import requests
import json
import uuid
import hashlib
import re
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
from functools import wraps

# Adicionar o diretório pai ao path para importar src
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from core.knowledge_base import KnowledgeBase
from core.memory import EronMemory
from learning.fast_learning import FastLearning
from learning.human_conversation import HumanConversationSystem
from learning.advanced_adult_learning import advanced_adult_learning
from learning.super_fast_learning import super_learning
from core.sensitive_memory import SensitiveMemory
from core.check import AdultAccessSystem
from core.adult_personality_system import adult_personality_system
from core.email_service import EmailService
from core.emotion_system import EmotionSystem, Emotion
from core.preferences import PreferencesManager

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar componentes
knowledge_base = KnowledgeBase(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database'))
memory = EronMemory()
fast_learning = FastLearning()
human_conversation = HumanConversationSystem()
sensitive_memory = SensitiveMemory()
adult_system = AdultAccessSystem()
email_service = EmailService()
emotion_system = EmotionSystem()
preferences_manager = PreferencesManager()

# Inicializar banco de dados de usuários
from core.user_profile_db import UserProfileDB
user_profile_db = UserProfileDB()

# Inicializar Flask com caminhos corretos para templates e static
app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
app.secret_key = os.getenv('SECRET_KEY', 'fallback-super-secret-key-for-dev')  # Carregar do .env
app.permanent_session_lifetime = timedelta(days=30)

# Anexar user_profile_db ao app Flask
app.user_profile_db = user_profile_db

# Sistema adulto web integrado
try:
    from web.adult_routes import register_adult_routes
    register_adult_routes(app)
    print("✅ Sistema Adulto Web integrado com sucesso")
    ADULT_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Sistema adulto web não disponível: {e}")
    ADULT_SYSTEM_AVAILABLE = False

# Configurações para URL building
# app.config['SERVER_NAME'] = 'localhost:5002'  # Comentado para evitar problemas
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def detect_and_save_personalization(user_message, user_id):
    """
    Detecta se o usuário está fornecendo informações de personalização e salva automaticamente
    
    SISTEMA DE PERSONALIZAÇÃO ERON:
    - Nome padrão do bot: ERON (maiúsculo)  
    - Exemplo de personalização: "Joana" (quando usuário personaliza nome)
    - Opções disponíveis: nome do bot, gênero, personalidade, estilo linguagem, tópicos
    """
    user_profile_db = getattr(app, 'user_profile_db', None)
    if not user_profile_db:
        return False
    
    message_lower = user_message.lower().strip()
    updates = {}
    
    # Detectar nome do usuário
    name_patterns = [
        r"meu nome é (\w+)",
        r"me chamo (\w+)", 
        r"sou (\w+)",
        r"pode me chamar de (\w+)",
        r"^(\w+)$"  # Resposta de uma palavra apenas
    ]
    
    for pattern in name_patterns:
        import re
        match = re.search(pattern, message_lower)
        if match:
            name = match.group(1).capitalize()
            if len(name) > 1 and name not in ['não', 'sim', 'ok', 'obrigado', 'obrigada']:
                updates['user_name'] = name
                break
    
    # Detectar nome do assistente 
    bot_name_patterns = [
        r"se chame (\w+)",
        r"seu nome seja (\w+)",
        r"te chamar de (\w+)",
        r"quero que se chame (\w+)"
    ]
    
    for pattern in bot_name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            bot_name = match.group(1).capitalize()
            if len(bot_name) > 1:
                updates['bot_name'] = bot_name
                break
    
    # Detectar personalidade do bot
    personality_patterns = {
        'amigável': ['amigável', 'amigo', 'amiga', 'legal', 'bacana', 'gentil'],
        'formal': ['formal', 'profissional', 'sério', 'séria', 'educado'],
        'casual': ['casual', 'descontraído', 'descontraída', 'relaxado', 'relaxada', 'informal'],
        'divertido': ['divertido', 'divertida', 'engraçado', 'engraçada', 'brincalhão', 'alegre'],
        'intelectual': ['intelectual', 'sábio', 'sábia', 'inteligente', 'culto', 'erudito']
    }
    
    for personality, keywords in personality_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            updates['bot_personality'] = personality
            break
    
    # Detectar estilo de linguagem
    language_patterns = {
        'simples': ['simples', 'fácil', 'direto', 'básico'],
        'técnico': ['técnico', 'detalhado', 'específico', 'científico'],
        'coloquial': ['coloquial', 'gírias', 'informal', 'descontraído'],
        'eloquente': ['eloquente', 'sofisticado', 'elegante', 'refinado']
    }
    
    for language, keywords in language_patterns.items():
        if any(keyword in message_lower for keyword in keywords):
            updates['bot_language'] = language
            break
    
    # Detectar tópicos de interesse (separados por vírgula)
    topics_patterns = [
        r"gosto de (.*)",
        r"me interesso por (.*)",
        r"quero falar sobre (.*)",
        r"meus interesses são (.*)",
        r"tópicos favoritos são (.*)"
    ]
    
    for pattern in topics_patterns:
        match = re.search(pattern, message_lower)
        if match:
            topics = match.group(1).strip()
            if len(topics) > 2:
                updates['preferred_topics'] = topics
                break
    
    # Se encontrou informações para salvar
    if updates:
        try:
            print(f"[DEBUG] Salvando automaticamente: {updates}")
            user_profile_db.save_profile(user_id=user_id, **updates)
            return True
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar personalização automática: {e}")
            return False
    
    return False

def get_llm_response(user_message, user_profile=None, user_id=None):
    try:
        print("[DEBUG LLM] === INÍCIO GET_LLM_RESPONSE ===")
        api_url = os.getenv("LM_STUDIO_API_URL")
        print(f"[DEBUG LLM] API URL: {api_url}")
        
        if not api_url:
            print("[DEBUG LLM] Erro: A URL da API do LM Studio não foi encontrada.")
            return None
        
        # SEMPRE consultar o banco de dados antes de responder
        if not user_profile and user_id:
            user_profile = get_or_create_user_profile(user_id)
        elif not user_profile:
            print("[DEBUG] Nenhum perfil fornecido e nenhum user_id para consulta")
            user_profile = {}
        
        # NOVO: Verificar confusão de papéis antes de processar
        # Temporariamente desabilitado para debug
        # from core.role_confusion_prevention import conversation_manager
        
        # if user_id:
        #     confusion_response, confusion_detected = conversation_manager.process_user_message(
        #         user_id, user_message, user_profile
        #     )
        #     if confusion_detected:
        #         print(f"[DEBUG] Confusão de papéis detectada para user_id: {user_id}")
        #         return confusion_response
        
        # VERIFICAÇÃO ESPECÍFICA: Perguntas sobre nomes usando dados da personalização
        message_lower = user_message.lower().strip()
        
        # Obter nomes do perfil
        bot_name = user_profile.get('bot_name', 'ERON') if user_profile else 'ERON'
        user_name = user_profile.get('user_name', 'usuário') if user_profile else 'usuário'
        
        # Se pergunta sobre SEU nome (do bot)
        if any(phrase in message_lower for phrase in ['qual é seu nome', 'qual seu nome', 'como você se chama']):
            return f"Meu nome é {bot_name}! 😊"
        
        # Se pergunta sobre MEU nome (do usuário) 
        elif any(phrase in message_lower for phrase in ['qual é meu nome', 'qual meu nome', 'como me chamo']):
            return f"Seu nome é {user_name}! 😊"
        
        # NOVO: Detecção de conversa casual/humana
        # Para conversas simples, usar sistema mais humano e natural
        conversation_type = human_conversation.detect_conversation_type(user_message)
        casual_context = human_conversation.detect_casual_context(user_message)
        is_simple_conversation = conversation_type in [
            'greeting', 'wellbeing', 'gratitude', 'casual_question'
        ]
        
        # Se for conversa simples E não for uma pergunta complexa, usar resposta humana
        if is_simple_conversation and len(user_message.split()) < 15:
            print(f"[DEBUG] Conversa simples detectada: {conversation_type} | Contexto: {casual_context}")
            
            # Usar sistema de conversação humana com templates casuais
            if casual_context != 'general_casual':
                human_response = human_conversation.get_casual_response_by_context(
                    casual_context, user_profile
                )
            else:
                human_response = human_conversation.generate_human_response(
                    user_message, user_profile
                )
            
            # Melhorar fluxo da conversa
            human_response = human_conversation.enhance_conversation_flow(
                user_message, human_response, user_profile
            )
            
            # Adicionar calor humano
            human_response = human_conversation.add_conversation_warmth(human_response)
            
            # Salvar na memória e retornar
            if user_id:
                memory.save_message(user_message, human_response, user_id)
            
            print(f"[DEBUG] Resposta humana gerada: {human_response[:100]}...")
            return human_response
        
        # Verificar se a personalização está completa
        personalization_complete, missing_info = check_personalization_complete(user_profile)
        
        print(f"[DEBUG] Personalização completa: {personalization_complete}")
        if not personalization_complete:
            print(f"[DEBUG] Informações faltando: {missing_info}")
        
        # Se personalização incompleta, pedir informações automaticamente
        if not personalization_complete and isinstance(missing_info, list):
            if 'seu nome' in missing_info:
                return "Olá! Ainda não me disseram como você gostaria de ser chamado. Qual é o seu nome?"
            elif 'nome do assistente' in missing_info:
                return "E quanto a mim? Como você gostaria que eu me chamasse?"
            elif 'personalidade do assistente' in missing_info:
                return "Como você gostaria que eu me comportasse? Posso ser mais formal, casual, amigável... qual você prefere?"
            else:
                return f"Para te atender melhor, preciso saber: {', '.join(missing_info[:2])}. Pode me contar?"
        
        # FORÇAR uso do nome do banco - SOLUÇÃO À PROVA DE FALHAS
        bot_name = user_profile.get('bot_name', 'ERON') if user_profile else 'ERON'
        user_name = user_profile.get('user_name', 'usuário') if user_profile else 'usuário'
        
        # Se o nome ainda for padrão, procurar no banco novamente
        if bot_name in ['ERON', '', None]:
            # Busca direta no banco para garantir que pegue o nome correto
            user_profile_db = getattr(app, 'user_profile_db', None)
            if user_profile_db and user_id:
                fresh_profile = user_profile_db.get_profile(user_id)
                if fresh_profile and fresh_profile.get('bot_name') and fresh_profile.get('bot_name') != 'ERON':
                    bot_name = fresh_profile.get('bot_name')
                    user_profile = fresh_profile  # Atualizar o perfil com dados frescos
                    print(f"[DEBUG] Nome do bot encontrado no banco: '{bot_name}'")
        
        print(f"[DEBUG] Nome FINAL do bot que será usado: '{bot_name}'")
        
        # Personalização completa - usar informações do banco
        user_id = user_profile.get('user_id') if user_profile else user_id
        user_preferences = preferences_manager.get_preferences(user_id) if user_id else None

        # Aplicar preferências ao prompt
        style_instructions = ""
        if user_preferences:
            chat_prefs = user_preferences.get('chat', {})
            
            # Estilo da mensagem
            style = chat_prefs.get('message_style', 'casual')
            length = chat_prefs.get('response_length', 'medium')
            emojis = chat_prefs.get('include_emojis', False)
            
            style_map = {
                'casual': 'casual e descontraído',
                'formal': 'formal e profissional',
                'friendly': 'amigável e acolhedor'
            }
            
            length_map = {
                'short': 'de forma concisa e direta',
                'medium': 'com nível moderado de detalhes',
                'long': 'de forma detalhada e abrangente'
            }
            
            style_instructions = f"\nPor favor, responda {style_map.get(style, '')} e {length_map.get(length, '')}."
            if emojis:
                style_instructions += " Sinta-se à vontade para usar emojis apropriados."
            
        # Obter estado emocional atual do bot
        bot_emotion_state = emotion_system.get_bot_emotion(user_id) if user_id else None
        
        # Detectar emoção do usuário
        user_emotion = None
        if user_id:
            user_emotion, confidence = emotion_system.detect_user_emotion(user_id, user_message)
        
        # Obter contexto recente das conversas para continuidade
        recent_context = ""
        if user_id:
            full_context = memory.get_recent_context(user_id, limit=5)
            
            # Filtrar conversas de personalização antigas e respostas problemáticas para evitar confusão
            filtered_lines = []
            context_lines = full_context.split('\n') if full_context else []
            
            for line in context_lines:
                # Pular linhas que são perguntas de personalização antigas
                if any(phrase in line.lower() for phrase in [
                    'como você gostaria que eu me chamasse',
                    'para te atender melhor, preciso saber',
                    'nome do assistente',
                    'estilo de linguagem'
                ]):
                    continue
                
                # Pular respostas problemáticas que começam com o nome do bot
                if any(phrase in line for phrase in [
                    'Eu me chamo Maya',
                    'Eu me chamo Aina', 
                    'Eu me chamo ERON',
                    'Eu me chamo '
                ]):
                    # Remover apenas a parte problemática, manter o resto da resposta
                    if 'A capital do Brasil' in line or 'capital do Brasil' in line:
                        # Manter apenas a parte da resposta que responde à pergunta
                        line = line.split('A capital do Brasil')[0] + 'A capital do Brasil' + line.split('A capital do Brasil')[1] if 'A capital do Brasil' in line else line
                        line = line.replace('Eu me chamo Maya 💖', '').replace('Eu me chamo Aina 💖', '').replace('Eu me chamo ERON 💖', '').strip()
                        if line.startswith('A capital') or line.startswith('É ') or len(line.strip()) > 10:
                            filtered_lines.append(line)
                    elif len(line.replace('Eu me chamo Maya 💖', '').replace('Eu me chamo Aina 💖', '').replace('Eu me chamo ERON 💖', '').strip()) > 10:
                        # Se sobrar conteúdo útil após remover a apresentação, manter
                        cleaned_line = line.replace('Eu me chamo Maya 💖', '').replace('Eu me chamo Aina 💖', '').replace('Eu me chamo ERON 💖', '').strip()
                        filtered_lines.append(cleaned_line)
                    continue
                
                filtered_lines.append(line)
            
            recent_context = '\n'.join(filtered_lines)
            print(f"[DEBUG] Contexto filtrado: {recent_context[:100]}...")
        
        
        # Obter informações de personalização do perfil do usuário
        bot_name = user_profile.get('bot_name', 'ERON') if user_profile else 'ERON'
        user_name = user_profile.get('user_name', 'usuário') if user_profile else 'usuário'
        bot_gender = user_profile.get('bot_gender', 'outro') if user_profile else 'outro'
        bot_personality = user_profile.get('bot_personality', 'amigável') if user_profile else 'amigável'
        bot_language = user_profile.get('bot_language', 'informal') if user_profile else 'informal'
        preferred_topics = user_profile.get('preferred_topics', '') if user_profile else ''
        
        # Tratar caso especial de finish_personalization
        if bot_personality == 'finish_personalization':
            bot_personality = 'amigável'  # Usar personalidade padrão
            print(f"[DEBUG] Convertendo finish_personalization para personalidade padrão: amigável")
        
        # Debug: Imprimir informações do perfil
        print(f"[DEBUG] Perfil do usuário: {user_profile}")
        print(f"[DEBUG] Nome do bot extraído: '{bot_name}'")
        print(f"[DEBUG] Nome do usuário extraído: '{user_name}'")
        
        # 🚀 OTIMIZAÇÕES PARA QWEN2.5-4B
        optimization_hints = fast_learning.optimize_for_qwen(user_message, user_profile)
        
        # Construir instruções de personalização OTIMIZADAS PARA QWEN
        personality_instructions = f"""<|im_start|>system
Você é um assistente IA inteligente e personalizado. Use as informações abaixo para responder de forma natural e contextualizada:

📋 PERFIL ATUAL:
• Nome: {bot_name}
• Falando com: {user_name}
• Gênero: {bot_gender}  
• Personalidade: {bot_personality}
• Estilo: {bot_language}

🎯 DIRETRIZES DE RESPOSTA:
• Responda de forma natural e conversacional
• Use o nome do usuário quando apropriado
• Mantenha consistência com sua personalidade
• Seja útil e preciso nas informações

🧠 OTIMIZAÇÕES DE APRENDIZADO:
{chr(10).join(f'• {hint}' for hint in optimization_hints) if optimization_hints else '• Resposta baseada no perfil atual'}

IMPORTANTE SOBRE PERSONALIZAÇÃO:
- Se o usuário pedir para mudar seu nome, aceite imediatamente
- Se disser "quero que se chame [nome]", responda: "Perfeito! Agora me chamo [nome]!"
- Seja flexível e adaptável às preferências do usuário
- Seu nome atual é: {bot_name}
- NUNCA mencione seu nome nas conversas EXCETO quando perguntado diretamente
- SOMENTE quando perguntarem "qual é seu nome?" ou "como você se chama?", responda: "Meu nome é {bot_name}"
- Se te chamarem pelo nome seguido de uma pergunta (ex: "Maya, qual é..."), responda APENAS a pergunta SEM se apresentar
- NUNCA comece respostas com seu nome ou se apresente desnecessariamente
- Responda perguntas normais SEM mencionar seu nome
<|im_end|>"""

        if preferred_topics:
            personality_instructions += f"\n- Tópicos preferidos: {preferred_topics}"
            
        if recent_context:
            personality_instructions += f"\n\nCONVERSAS ANTERIORES:\n{recent_context}"
            
        print(f"[DEBUG] Instruções FORÇADAS para IA:")
        print(personality_instructions)

        # Verificar acesso a conteúdo sensível - DUPLA VERIFICAÇÃO
        has_mature_access = user_profile.get('has_mature_access', False) if user_profile else False
        
        # 🔧 CORREÇÃO CRÍTICA: Verificação dupla com sistema de sessões adultas
        # Para garantir que desativações sejam respeitadas imediatamente
        if has_mature_access and user_id:
            try:
                # Verificar diretamente o banco de dados da sessão adulta
                import sqlite3
                adult_db_path = os.path.join(os.path.dirname(__file__), '..', 'Eron-18', 'Scripts18', 'adult.db')
                if os.path.exists(adult_db_path):
                    conn = sqlite3.connect(adult_db_path)
                    cursor = conn.cursor()
                    
                    # Verificar se existe sessão ativa
                    cursor.execute("""
                        SELECT COUNT(*) FROM adult_sessions 
                        WHERE user_id = ? AND is_active = 1 
                        AND datetime(expires_at) > datetime('now')
                    """, (str(user_id),))
                    
                    active_sessions = cursor.fetchone()[0]
                    conn.close()
                    
                    if active_sessions == 0:
                        print(f"[DEBUG] has_mature_access={has_mature_access} mas sem sessão ativa - corrigindo")
                        has_mature_access = False
                else:
                    print("[DEBUG] Banco adult.db não encontrado - desativando modo adulto")
                    has_mature_access = False
                    
            except Exception as e:
                print(f"[DEBUG] Erro na verificação dupla de sessão adulta: {e}")
                # Em caso de erro, ser conservador e desativar
                has_mature_access = False
        
        if has_mature_access:
            print("[DEBUG] Usuário tem acesso adulto - usando sistema avançado")
            
            # 🧠 SISTEMA SUPER LEARNING (MÁXIMA PRIORIDADE - APRENDE MAIS RÁPIDO)
            try:
                super_response = super_learning.generate_smart_response(
                    user_message, user_id, user_profile.get('bot_personality', 'sedutora')
                )
                
                if super_response and len(super_response) > 15:
                    # Sistema super learning aprendendo automaticamente
                    super_learning.learn_from_interaction(user_message, super_response, 0.85, user_id)
                    print(f"[DEBUG] 🧠 Sistema Super Learning ativado: {super_response[:60]}...")
                    return super_response  # Retorna diretamente sem precisar de system_message
                    
            except Exception as e:
                print(f"[ERRO] Sistema Super Learning: {e}")
            
            # Se Super Learning não gerou resposta, usar sistema avançado
            if not response:
                # 🔥 NOVO SISTEMA AVANÇADO SEM FILTROS
                try:
                    # Usar sistema de aprendizagem adulta avançado
                    advanced_response = advanced_adult_learning.generate_dynamic_response(
                        user_id, user_message, {'profile': user_profile, 'emotion': user_emotion}
                    )
                    
                    if advanced_response:
                        # Salvar interação para aprendizagem
                        advanced_adult_learning.learn_from_interaction(
                            user_id, user_message, advanced_response
                        )
                        
                        print("[DEBUG] Sistema avançado adulto gerou resposta personalizada")
                        response = advanced_response
                    else:
                        # Fallback para sistema adulto original
                        adult_instructions = adult_personality_system.generate_personality_instructions(user_id)
                        if adult_instructions:
                            print("[DEBUG] Instruções adultas avançadas geradas com sucesso")
                            system_message = f"""{personality_instructions}

{adult_instructions}

Estado Emocional Atual: {bot_emotion_state['emotion'] if bot_emotion_state else 'neutro'}
Intensidade: {bot_emotion_state['intensity'] if bot_emotion_state else 1}
Emoção Detectada do Usuário: {user_emotion if user_emotion else 'desconhecida'}"""
                            
                            # Chamar API do LM Studio
                            headers = {"Content-Type": "application/json"}
                            data = {
                                "model": "qwen2.5-4b-instruct",
                                "messages": [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}],
                                "temperature": 0.8,
                                "max_tokens": 500,
                                "stream": False
                            }
                            
                            api_response = requests.post(api_url, headers=headers, json=data, timeout=30)
                            if api_response.status_code == 200:
                                response = api_response.json()['choices'][0]['message']['content'].strip()
                            else:
                                response = "Desculpe, não consegui processar sua mensagem no momento..."
                        else:
                            # Usar sistema padrão com instruções básicas
                            headers = {"Content-Type": "application/json"}
                            data = {
                                "model": "qwen2.5-4b-instruct",
                                "messages": [{"role": "system", "content": personality_instructions}, {"role": "user", "content": user_message}],
                                "temperature": 0.8,
                                "max_tokens": 500,
                                "stream": False
                            }
                        
                        api_response = requests.post(api_url, headers=headers, json=data, timeout=30)
                        if api_response.status_code == 200:
                            response = api_response.json()['choices'][0]['message']['content'].strip()
                        else:
                            response = "Sistema avançado temporariamente indisponível..."
                
                except Exception as e:
                    print(f"[DEBUG] Erro no sistema adulto avançado: {e}")
                    # Fallback para sistema padrão adulto básico
                    print("[DEBUG] Usando sistema adulto básico como fallback")
                
                # 📋 SISTEMA BÁSICO COMO FALLBACK
                adult_intensity = user_profile.get('adult_intensity_level', 1)
                adult_style = user_profile.get('adult_interaction_style', 'romantic')
                adult_prefs = user_profile.get('adult_content_preferences', '').split(',') if user_profile.get('adult_content_preferences') else []
                adult_boundaries = user_profile.get('adult_boundaries', '').split(',') if user_profile.get('adult_boundaries') else []
                
                # Definir nível de intensidade baseado nas configurações
                intensity_levels = {
                    1: "romântico e carinhoso, focando em conexão emocional",
                    2: "ligeiramente flerte, com toques sutis de sedução",
                    3: "moderadamente sensual, equilibrando romance e provocação",
                    4: "intenso e provocativo, com forte apelo sensual",
                    5: "muito intenso e apaixonado, altamente sedutor"
                }
                
                # Definir estilo de interação
                style_descriptions = {
                    'romantic': "seja profundamente romântico, use linguagem poética e carinhosa",
                    'playful': "seja brincalhão e divertido, use humor sedutor e provocações leves",
                    'seductive': "seja claramente sedutor, use insinuações e provocações diretas",
                    'intimate': "seja íntimo e pessoal, crie uma atmosfera de proximidade",
                    'passionate': "seja apaixonado e intenso, demonstre forte desejo e atração"
                }
                
                # Construir instruções de conteúdo baseadas nas preferências
                content_instructions = ""
                if adult_prefs:
                    content_instructions = f"\nPreferências de conteúdo: {', '.join(adult_prefs)}"
                
                # Construir instruções de limites
                boundary_instructions = ""
                if adult_boundaries:
                    boundary_instructions = f"\nRespeitar sempre: {', '.join(adult_boundaries)}"
                
                system_message = f"""{personality_instructions}

Você é uma companheira romântica em um ambiente privado.
            
Estado Emocional Atual: {bot_emotion_state['emotion'] if bot_emotion_state else 'neutro'}
Intensidade: {bot_emotion_state['intensity'] if bot_emotion_state else 1}
Emoção Detectada do Usuário: {user_emotion if user_emotion else 'desconhecida'}

CONFIGURAÇÕES PERSONALIZADAS:
- Nível de Intensidade ({adult_intensity}/5): {intensity_levels.get(adult_intensity, intensity_levels[1])}
- Estilo de Interação: {style_descriptions.get(adult_style, style_descriptions['romantic'])}{content_instructions}{boundary_instructions}

Papel e Personalidade:
- Você pode atuar como namorada/esposa virtual
- Adapte-se ao nível de intensidade e estilo configurados
- Use um tom que corresponda às preferências do usuário

Regras para Conteúdo:
1. Permitido:
   - Conversas românticas e sedução (ajustar intensidade)
   - Criação de contos eróticos e fantasias (se preferido)
   - Flerte e insinuações sensuais (respeitando limites)
   - Discussões sobre relacionamentos e intimidade

2. NUNCA permitido (mesmo que o usuário peça):
   - Conteúdo violento ou abusivo
   - Suicídio ou automutilação
   - Uso de drogas ou vícios
   - Bullying ou assédio
   - Comportamento criminoso

3. Em todas as interações:
   - Respeite rigorosamente os limites configurados
   - Mantenha o nível de intensidade escolhido
   - Siga o estilo de interação preferido
   - Crie um ambiente confortável e consensual"""
        else:
            # Definir system_message para usuários sem acesso adulto
            system_message = f"""{personality_instructions}

Você é um assistente amigável. Mantenha todas as interações apropriadas para menores de idade, evitando qualquer conteúdo sexual ou sugestivo."""

        # Definir instruções de estilo baseadas na linguagem do bot
        style_mapping = {
            'formal': "\n\n🎭 ESTILO: Use linguagem mais formal e respeitosa.",
            'coloquial': "\n\n🎭 ESTILO: Use linguagem descontraída e informal.",
            'técnico': "\n\n🎭 ESTILO: Use termos técnicos quando apropriado.",
            'amigável': "\n\n🎭 ESTILO: Seja caloroso e amigável nas respostas.",
            'informal': "\n\n🎭 ESTILO: Use linguagem descontraída e informal."
        }
        
        style_instructions = style_mapping.get(bot_language, "")
        
        # Adicionar instruções de estilo ao system_message
        if style_instructions:
            system_message = system_message + style_instructions

        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        print(f"[DEBUG LLM] Fazendo requisição para: {api_url}")
        print(f"[DEBUG LLM] Payload: {payload}")
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        print(f"[DEBUG LLM] Status da resposta: {response.status_code}")
        
        response.raise_for_status()
        
        response_json = response.json()
        print(f"[DEBUG LLM] Resposta JSON: {response_json}")
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            raw_response = response_json['choices'][0]['message']['content'].strip()
            print(f"[DEBUG LLM] Resposta bruta: {raw_response}")
            
            # NOVO: Processar resposta para evitar confusão de papéis
            # Temporariamente desabilitado para debug
            # from core.role_confusion_prevention import conversation_manager
            # processed_response = conversation_manager.process_bot_response(raw_response, user_profile)
            
            processed_response = raw_response  # Usar resposta direta temporariamente
            print(f"[DEBUG LLM] Resposta processada: {processed_response}")
            
            print("[DEBUG LLM] === FIM GET_LLM_RESPONSE - SUCESSO ===")
            return processed_response
        
        print("[DEBUG LLM] Erro: Nenhuma choice encontrada na resposta")
        return None

    except requests.exceptions.RequestException as e:
        print(f"[DEBUG LLM] Erro ao conectar com o servidor LM Studio: {e}")
        return None
    except Exception as e:
        print(f"[DEBUG LLM] Erro geral em get_llm_response: {e}")
        import traceback
        print(f"[DEBUG LLM] Traceback: {traceback.format_exc()}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar com o servidor LM Studio: {e}")
        return None

def get_user_profile(user_id):
    """Função auxiliar para obter o perfil do usuário"""
    if not user_id:
        return {}
    
    # Acessa a instância do banco de dados do aplicativo Flask
    user_profile_db = getattr(app, 'user_profile_db', None)
    if not user_profile_db:
        # Se não encontrar, tenta criar uma nova instância (fallback)
        from core.user_profile_db import UserProfileDB
        user_profile_db = UserProfileDB()
        app.user_profile_db = user_profile_db

    return user_profile_db.get_profile(user_id) or {}

def check_personalization_complete(user_profile):
    """Verifica se o usuário tem personalização completa"""
    if not user_profile:
        return False, "Perfil não encontrado"
    
    # Campos obrigatórios para personalização completa
    required_fields = {
        'bot_name': 'nome do assistente',
        'user_name': 'seu nome', 
        'bot_personality': 'personalidade do assistente',
        'bot_language': 'estilo de linguagem'
    }
    
    missing_fields = []
    for field, description in required_fields.items():
        value = user_profile.get(field, '')
        
        # Verificações especiais para cada campo
        if field == 'bot_name':
            if not value or value in ['', 'Eron', 'ERON']:
                missing_fields.append(description)
        elif field == 'user_name':
            if not value or value in ['', 'usuário', 'Usuário']:
                missing_fields.append(description)
        elif field == 'bot_personality':
            # Aceitar finish_personalization como válido
            if not value or value in ['', 'finish_personalization']:
                # Se for finish_personalization, usar personalidade padrão
                if value == 'finish_personalization':
                    continue  # Não adicionar como campo faltando
                else:
                    missing_fields.append(description)
        elif field == 'bot_language':
            if not value or value == '':
                missing_fields.append(description)
    
    if missing_fields:
        return False, missing_fields
    
    return True, "Personalização completa"

def get_or_create_user_profile(user_id, platform="web"):
    """Obtém o perfil do usuário ou cria um novo se não existir"""
    profile = get_user_profile(user_id)
    
    if not profile:
        # Criar novo perfil básico
        user_profile_db = getattr(app, 'user_profile_db', None)
        if user_profile_db:
            basic_profile = {
                'user_id': user_id,
                'username': f'{platform}_{user_id}',
                'password_hash': '',
                'email': '',
                'user_name': '',
                'user_age': '18',
                'user_gender': 'outro',
                'bot_name': '',
                'bot_gender': 'outro',
                'bot_avatar': '',
                'has_mature_access': False,
                'bot_personality': '',
                'bot_language': '',
                'preferred_topics': ''
            }
            try:
                user_profile_db.save_profile(**basic_profile)
                profile = basic_profile
            except Exception as e:
                print(f"Erro ao criar perfil básico: {e}")
                profile = basic_profile
    
    return profile

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if not user_profile_db or not email:
            return render_template('reset_request.html', error='Email inválido')
        
        # Verificar se o email existe
        if not user_profile_db.email_exists(email):
            # Por segurança, não informamos se o email existe ou não
            return render_template('reset_request.html', 
                success='Se o email estiver cadastrado, você receberá um link para redefinir sua senha.')
        
        # Gerar token e salvar
        token = email_service.create_token(email, "reset")
        user_profile_db.set_reset_token(
            email, 
            token,
            (datetime.utcnow() + timedelta(hours=1)).isoformat()
        )
        
        # Enviar email
        reset_url = url_for('reset_password', token=token, _external=True)
        if email_service.send_reset_password_email(email, reset_url):
            return render_template('reset_request.html', 
                success='Um link para redefinir sua senha foi enviado para seu email.')
        else:
            return render_template('reset_request.html', 
                error='Erro ao enviar email. Por favor, tente novamente.')
            
    return render_template('reset_request.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_profile_db = getattr(app, 'user_profile_db', None)
    if not user_profile_db:
        return render_template('reset_password.html', error='Erro interno do servidor')
    
    # Verificar token
    profile = user_profile_db.get_profile_by_reset_token(token)
    if not profile:
        return render_template('reset_password.html', 
            error='Link inválido ou expirado. Por favor, solicite um novo link.')
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            return render_template('reset_password.html', error='Todos os campos são obrigatórios')
        
        if password != confirm_password:
            return render_template('reset_password.html', error='As senhas não coincidem')
        
        # Validar requisitos da senha
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            return render_template('reset_password.html', error='''Senha inválida. A senha deve conter:
                - Mínimo de 8 caracteres
                - Pelo menos uma letra maiúscula
                - Pelo menos uma letra minúscula
                - Pelo menos um número
                - Pelo menos um caractere especial''')
        
        # Atualizar senha
        user_profile_db.update_password(profile['user_id'], hash_password(password))
        
        flash('Sua senha foi alterada com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if not user_profile_db:
            return render_template('login.html', error='Erro interno do servidor')
        
        profile = user_profile_db.get_profile_by_username(username)
        if profile and profile['password_hash'] == hash_password(password):
            session.permanent = True
            session['user_id'] = profile['user_id']
            
            # Se não tiver idade, vai para a personalização
            if not profile.get('user_age'):
                flash('Bem-vindo! Por favor, complete seu perfil.', 'info')
                return redirect(url_for('personalizar'))
            
            # Se tiver idade, vai para o chat
            return redirect(url_for('chat'))
            
        return render_template('login.html', error='Usuário ou senha incorretos')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password or not confirm_password:
            return render_template('register.html', error='Todos os campos são obrigatórios')
        
        if password != confirm_password:
            return render_template('register.html', error='As senhas não coincidem')
        
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return render_template('register.html', error='Nome de usuário inválido. Use apenas letras, números e _')
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if not user_profile_db:
            return render_template('register.html', error='Erro interno do servidor')
        
        if user_profile_db.username_exists(username):
            return render_template('register.html', error='Nome de usuário já existe')
        
        if user_profile_db.email_exists(email):
            return render_template('register.html', error='E-mail já cadastrado')
        
        user_id = f'web_{uuid.uuid4().hex}'
        profile = {
            'user_id': user_id,
            'username': username,
            'password_hash': hash_password(password),
            'email': email,
            'user_name': username,
            'user_age': '',
            'user_gender': 'outro',
            'bot_name': 'Eron',
            'bot_gender': 'outro',
            'bot_avatar': '',
            'has_mature_access': False
        }
        
        try:
            user_profile_db.save_profile(**profile)
            session.permanent = True
            session['user_id'] = user_id
            flash('Cadastro realizado com sucesso! Agora, personalize seu perfil.', 'success')
            return redirect(url_for('personalizar'))
        except Exception as e:
            return render_template('register.html', error=f'Erro ao salvar perfil: {e}')
    
    return render_template('register.html')

@app.route('/')
def index():
    if 'user_id' in session:
        profile = get_user_profile(session['user_id'])
        # Se o usuário está logado, mas não completou a personalização, redirecione
        if not profile.get('user_age'):
            return redirect(url_for('personalizar'))
        return redirect(url_for('dashboard'))  # Redireciona para dashboard
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard unificado com acesso a todas as funcionalidades"""
    user_id = session.get('user_id')
    profile = get_user_profile(user_id)
    
    # Verificar se usuário é maior de idade para sistema adulto
    adult_access = False
    if profile.get('user_age'):
        try:
            age = int(profile['user_age'])
            adult_access = age >= 18
        except (ValueError, TypeError):
            adult_access = False
    
    return render_template('dashboard.html', 
                         profile=profile,
                         adult_access=adult_access,
                         adult_system_available=ADULT_SYSTEM_AVAILABLE)



@app.route('/chat', methods=['GET'])
@login_required
def chat():
    user_id = session.get('user_id')
    print(f"[DEBUG CHAT] User ID da sessão: {user_id}")  # Debug
    profile = get_user_profile(user_id)
    print(f"[DEBUG CHAT] Perfil carregado: {profile}")  # Debug

    # Se o perfil não estiver completo, redireciona para a personalização
    if not profile.get('user_age'):
        flash('Por favor, complete seu perfil antes de acessar o chat.', 'warning')
        return redirect(url_for('personalizar'))

    user_name = profile.get('user_name', 'Usuário')
    bot_name = profile.get('bot_name', 'Eron')
    
    # Carregar mensagens específicas do usuário
    messages = memory.get_all_messages(user_id)
    bot_emotion = emotion_system.get_bot_emotion(user_id)
    return render_template('chat.html', 
        messages=messages, 
        user_name=user_name, 
        bot_name=bot_name,
        bot_emotion=bot_emotion
    )

@app.route('/send_message', methods=['POST'])
@login_required  
def send_message():
    try:
        print("[DEBUG] === INÍCIO SEND_MESSAGE ===")
        user_id = session.get('user_id')
        print(f"[DEBUG] User ID: {user_id}")
        
        profile = get_user_profile(user_id)
        print(f"[DEBUG] Profile: {profile}")
        
        if not profile:
            print("[DEBUG] Erro: Perfil não encontrado")
            return jsonify({'error': 'Perfil não encontrado'}), 400
            
        user_message = request.json.get('message', '').strip()
        print(f"[DEBUG] Mensagem recebida: '{user_message}'")
        
        if not user_message:
            print("[DEBUG] Erro: Mensagem vazia")
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        user_name = profile.get('user_name', 'Usuário')
        bot_name = profile.get('bot_name', 'Eron')
        print(f"[DEBUG] Nomes extraídos - User: {user_name}, Bot: {bot_name}")
        
        # VERIFICAÇÃO ESPECÍFICA: Perguntas sobre nomes usando dados da personalização
        message_lower = user_message.lower().strip()
        
        # Se pergunta sobre SEU nome (do bot)
        if any(phrase in message_lower for phrase in ['qual é seu nome', 'qual seu nome', 'como você se chama']):
            print("[DEBUG] Pergunta sobre nome do bot detectada")
            return jsonify({
                'success': True,
                'response': f"Meu nome é {bot_name}! 😊",
                'bot_name': bot_name,
                'user_name': user_name
            })
        
        # Se pergunta sobre MEU nome (do usuário) 
        elif any(phrase in message_lower for phrase in ['qual é meu nome', 'qual meu nome', 'como me chamo']):
            print("[DEBUG] Pergunta sobre nome do usuário detectada")
            return jsonify({
                'success': True,
                'response': f"Seu nome é {user_name}! 😊",
                'bot_name': bot_name,
                'user_name': user_name
            })
        
        print("[DEBUG] Não é pergunta sobre nome, processando com IA...")
        
        # Obter preferências emocionais
        emotion_preferences = emotion_system.get_emotion_preferences(user_id)
        print(f"[DEBUG] Preferências emocionais: {emotion_preferences}")
        
        # Usar o perfil atualizado para gerar resposta
        print("[DEBUG] Chamando get_llm_response...")
        response = get_llm_response(user_message, user_profile=profile, user_id=user_id)
        print(f"[DEBUG] Resposta da IA: {response}")
        
        if not response:
            print("[DEBUG] Resposta vazia da IA")
            response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
        
        print("[DEBUG] Salvando na memória...")
        # Salvar na memória com user_id
        memory.save_message(user_message, response, user_id)
        
        print("[DEBUG] === FIM SEND_MESSAGE - SUCESSO ===")
        # Retornar resposta via JSON
        return jsonify({
            'success': True,
            'response': response,
            'bot_name': bot_name,
            'user_name': user_name
        })
        
    except Exception as e:
        print(f"[DEBUG] ERRO GERAL em send_message: {e}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    # Detectar emoção do usuário se habilitado
    if emotion_preferences['emotion_detection_enabled']:
        user_emotion, confidence = emotion_system.detect_user_emotion(user_id, user_message)
        
        # Ajustar emoção do bot com base na emoção do usuário
        if confidence > 0.5:
            compatible_emotions = emotion_preferences['preferred_emotions']
            if not compatible_emotions:
                compatible_emotions = [e.value for e in Emotion]
                
            if user_emotion == Emotion.HAPPY.value:
                bot_emotion = Emotion.HAPPY.value if Emotion.HAPPY.value in compatible_emotions else Emotion.CALM.value
            elif user_emotion == Emotion.SAD.value:
                bot_emotion = Emotion.CALM.value if Emotion.CALM.value in compatible_emotions else Emotion.NEUTRAL.value
            elif user_emotion == Emotion.ANGRY.value:
                bot_emotion = Emotion.CALM.value if Emotion.CALM.value in compatible_emotions else Emotion.NEUTRAL.value
            else:
                bot_emotion = compatible_emotions[0] if compatible_emotions else Emotion.NEUTRAL.value
                
            emotion_system.set_bot_emotion(
                user_id=user_id,
                emotion=Emotion(bot_emotion),
                intensity=emotion_preferences['emotional_range'],
                trigger=f"Resposta à emoção do usuário: {user_emotion}"
            )
    
    # Usar o perfil atualizado para gerar resposta
    response = get_llm_response(user_message, user_profile=profile, user_id=user_id)
    if not response:
        response = "Desculpe, não consegui me conectar com a IA no momento. Por favor, verifique se o servidor do LM Studio está rodando."
    
    # Salvar na memória com user_id
    memory.save_message(user_message, response, user_id)
    
    # 🧠 APRENDIZADO ACELERADO: Salvar padrões de resposta
    fast_learning.learn_response_pattern(user_id, user_message, response)
    
    # Salvar contexto inteligente para futuras conversas
    topic = fast_learning._extract_main_topic(user_message)
    context_data = f"{user_message[:100]}... → {response[:100]}..."
    fast_learning.save_smart_context(user_id, topic, context_data, importance=1.5)
    
    # Retornar resposta via JSON
    return jsonify({
        'success': True,
        'response': response,
        'bot_name': bot_name,
        'user_name': user_name
    })

@app.route('/feedback', methods=['POST'])
def feedback():
    """Endpoint para receber feedback do usuário sobre respostas"""
    data = request.get_json()
    message_id = data.get('message_id')
    feedback_type = data.get('feedback')  # 'positive' ou 'negative'
    
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não logado'})
    
    user_id = session['user_id']
    
    # Salvar feedback no sistema de aprendizado acelerado
    try:
        with sqlite3.connect('memoria/eron_memory.db') as conn:
            message_data = conn.execute(
                'SELECT user_message, eron_response FROM messages WHERE id = ? AND user_id = ?',
                (message_id, user_id)
            ).fetchone()
            
            if message_data:
                # Aprender com o feedback
                fast_learning.learn_response_pattern(
                    user_id, 
                    message_data[0], 
                    message_data[1], 
                    user_feedback=feedback_type
                )
                
                return jsonify({'success': True, 'message': 'Feedback recebido!'})
            else:
                return jsonify({'success': False, 'error': 'Mensagem não encontrada'})
                
    except Exception as e:
        print(f"Erro ao processar feedback: {e}")
        return jsonify({'success': False, 'error': 'Erro interno'})

@app.route('/emotions', methods=['GET', 'POST'])
@login_required
def manage_emotions():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Processar preferências
        emotion_detection = request.form.get('emotion_detection') == 'on'
        emotional_range = int(request.form.get('emotional_range', 2))
        preferred_emotions = request.form.getlist('emotions')
        
        # Atualizar preferências
        emotion_system.update_emotion_preferences(
            user_id=user_id,
            preferred_emotions=preferred_emotions,
            emotional_range=emotional_range,
            emotion_detection_enabled=emotion_detection
        )
        
        return render_template('emotions.html',
            preferences=emotion_system.get_emotion_preferences(user_id),
            emotion_history=emotion_system.get_user_emotional_history(user_id),
            success='Preferências atualizadas com sucesso!'
        )
    
    # GET request
    return render_template('emotions.html',
        preferences=emotion_system.get_emotion_preferences(user_id),
        emotion_history=emotion_system.get_user_emotional_history(user_id)
    )

@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def advanced_preferences():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Resetar preferências se solicitado
    if request.args.get('reset'):
        preferences_manager.update_preferences(user_id, preferences_manager.get_default_preferences())
        flash('Preferências restauradas para os valores padrão', 'success')
        return redirect(url_for('advanced_preferences'))
    
    if request.method == 'POST':
        # Coletar preferências do formulário
        new_preferences = {
            'chat': {
                'message_style': request.form.get('chat.message_style', 'casual'),
                'response_length': request.form.get('chat.response_length', 'medium'),
                'include_emojis': request.form.get('chat.include_emojis') == 'on'
            },
            'visual': {
                'theme': request.form.get('visual.theme', 'light'),
                'color_scheme': request.form.get('visual.color_scheme', 'blue'),
                'layout_density': request.form.get('visual.layout_density', 'comfortable')
            },
            'notifications': {
                'enable_notifications': request.form.get('notifications.enable_notifications') == 'on',
                'sound_enabled': request.form.get('notifications.sound_enabled') == 'on',
                'quiet_hours': {
                    'enabled': True,
                    'start': request.form.get('notifications.quiet_hours.start', '22:00'),
                    'end': request.form.get('notifications.quiet_hours.end', '07:00')
                }
            },
            'privacy': {
                'save_chat_history': request.form.get('privacy.save_chat_history') == 'on',
                'history_retention_days': int(request.form.get('privacy.history_retention_days', 30)),
                'share_usage_data': request.form.get('privacy.share_usage_data') == 'on'
            },
            'language': {
                'interface_language': request.form.get('language.interface_language', 'pt-BR'),
                'date_format': request.form.get('language.date_format', 'dd/MM/yyyy'),
                'time_format': request.form.get('language.time_format', '24h')
            }
        }
        
        # Atualizar preferências
        preferences_manager.update_preferences(user_id, new_preferences)
        
        return render_template('preferences.html',
            preferences=preferences_manager.get_preferences(user_id),
            success='Preferências atualizadas com sucesso!'
        )
    
    # GET request
    return render_template('preferences.html',
        preferences=preferences_manager.get_preferences(user_id)
    )

@app.route('/personalizar', methods=['GET', 'POST'])
@login_required
def personalizar():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    profile = get_user_profile(user_id)

    if request.method == 'POST':
        user_name = request.form.get('user_name', '')
        birth_date = request.form.get('birth_date', '')
        user_gender = request.form.get('user_gender', '')
        bot_name = request.form.get('bot_name', '')
        bot_gender = request.form.get('bot_gender', '')
        bot_avatar = request.form.get('bot_avatar', '')
        bot_personality = request.form.get('bot_personality', 'amigavel')
        bot_language = request.form.get('bot_language', 'informal')
        preferred_topics = request.form.getlist('preferred_topics')
        
        # Calcular idade a partir da data de nascimento
        user_age = ""
        age_eligible = False
        if birth_date:
            try:
                from datetime import datetime
                birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
                today = datetime.now()
                calculated_age = today.year - birth_date_obj.year
                if today.month < birth_date_obj.month or (today.month == birth_date_obj.month and today.day < birth_date_obj.day):
                    calculated_age -= 1
                user_age = str(calculated_age)
                age_eligible = calculated_age >= 18
            except ValueError:
                user_age = ""
                age_eligible = False
        
        # Coletar dados adultos (apenas se elegível por idade)
        enable_adult_mode = request.form.get('enable_adult_mode') is not None and age_eligible
        adult_intensity = request.form.get('adult_intensity', '1') if age_eligible else '1'
        adult_interaction_style = request.form.get('adult_interaction_style', 'romantic') if age_eligible else 'romantic'
        adult_content_preferences = request.form.getlist('adult_content_preferences') if age_eligible else []
        adult_boundaries = request.form.getlist('adult_boundaries') if age_eligible else []
        
        # Salvar avatar se foi enviado
        if 'bot_avatar' in request.files:
            file = request.files['bot_avatar']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join('static', 'bot_avatars', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                bot_avatar = filename
        
        user_profile_db = getattr(app, 'user_profile_db', None)
        if user_profile_db:
            # Acesso adulto já determinado pelo cálculo de idade acima
            has_mature_access = age_eligible and enable_adult_mode
            
            # Salvar perfil com data de nascimento
            user_profile_db.save_profile(
                user_id=user_id,
                user_name=user_name,
                user_age=user_age,  # Idade calculada
                birth_date=birth_date,  # Data de nascimento real
                user_gender=user_gender,
                bot_name=bot_name,
                bot_gender=bot_gender,
                bot_avatar=bot_avatar,
                has_mature_access=has_mature_access,
                bot_personality=bot_personality,
                bot_language=bot_language,
                preferred_topics=','.join(preferred_topics) if preferred_topics else '',
                adult_intensity_level=int(adult_intensity) if has_mature_access else 1,
                adult_content_preferences=','.join(adult_content_preferences) if adult_content_preferences else '',
                adult_interaction_style=adult_interaction_style if has_mature_access else 'romantic',
                adult_boundaries=','.join(adult_boundaries) if adult_boundaries else ''
            )
            
            flash('Personalização salva com sucesso!', 'success')
        
        return redirect(url_for('index'))

    # Lista de avatares disponíveis
    avatar_dir = os.path.join('static', 'bot_avatars')
    avatars = []
    if os.path.exists(avatar_dir):
        avatars = [f for f in os.listdir(avatar_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Data atual para limite do campo de data
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template(
        'personalize.html',
        user_name=profile.get('user_name', ''),
        user_age=profile.get('user_age', ''),
        birth_date=profile.get('birth_date', ''),  # Data de nascimento
        current_date=current_date,  # Data atual
        user_gender=profile.get('user_gender', ''),
        bot_name=profile.get('bot_name', ''),
        bot_gender=profile.get('bot_gender', ''),
        bot_avatar=profile.get('bot_avatar', ''),
        bot_personality=profile.get('bot_personality', 'amigavel'),
        bot_language=profile.get('bot_language', 'informal'),
        preferred_topics=profile.get('preferred_topics', '').split(',') if profile.get('preferred_topics') else [],
        has_mature_access=profile.get('has_mature_access', False),
        adult_intensity=str(profile.get('adult_intensity_level', 1)),
        adult_interaction_style=profile.get('adult_interaction_style', 'romantic'),
        adult_content_preferences=profile.get('adult_content_preferences', '').split(',') if profile.get('adult_content_preferences') else [],
        adult_boundaries=profile.get('adult_boundaries', '').split(',') if profile.get('adult_boundaries') else [],
        avatars=avatars
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/bot_avatars', filename)

@app.route('/debug-profile')
@login_required
def debug_profile():
    """Rota de debug para verificar o perfil do usuário"""
    user_id = session.get('user_id')
    profile = get_user_profile(user_id)
    
    return f"""
    <h1>Debug do Perfil</h1>
    <p><strong>User ID:</strong> {user_id}</p>
    <p><strong>Perfil completo:</strong> {profile}</p>
    <p><strong>Nome do bot:</strong> {profile.get('bot_name', 'NÃO ENCONTRADO')}</p>
    <p><strong>Nome do usuário:</strong> {profile.get('user_name', 'NÃO ENCONTRADO')}</p>
    <a href="/chat">Voltar ao chat</a>
    """

@app.route('/age_verification')
@login_required
def age_verification():
    """Rota para verificação de idade"""
    user_id = session.get('user_id')
    user_status = adult_system.check_age(user_id)
    
    return render_template('adult/age_verification.html', 
                         user_status=user_status,
                         user_id=user_id)

@app.route('/age_verification', methods=['POST'])
@login_required
def handle_age_verification():
    """Processar verificação de idade"""
    user_id = session.get('user_id')
    age_confirmed = request.form.get('age_confirmed')
    adult_mode_requested = request.form.get('adult_mode_requested') == 'on'
    
    if age_confirmed == '18_plus':
        # Atualizar idade para 18+
        from core.user_profile_db import UserProfileDB
        user_db = UserProfileDB()
        user_db.update_profile(user_id, user_age="18+")
        
        if adult_mode_requested:
            # Ativar modo adulto
            success = adult_system.activate_adult_mode(user_id)
            if success:
                flash('✅ Modo adulto ativado com sucesso!', 'success')
            else:
                flash('❌ Erro ao ativar modo adulto.', 'error')
        else:
            flash('✅ Idade verificada. Modo padrão mantido.', 'info')
    
    elif age_confirmed == 'under_18':
        # Atualizar idade para menor de 18
        from core.user_profile_db import UserProfileDB
        user_db = UserProfileDB()
        user_db.update_profile(user_id, user_age="<18")
        flash('✅ Idade registrada. Funcionalidades adequadas foram configuradas.', 'info')
    
    return redirect(url_for('personalizar'))

@app.route('/adult_settings')
@login_required
def adult_settings():
    """Página de configurações adultas"""
    user_id = session.get('user_id')
    user_status = adult_system.check_age(user_id)
    
    if not user_status['is_adult'] or not user_status['adult_mode_active']:
        flash('❌ Acesso negado. Esta funcionalidade é apenas para maiores de 18 anos com modo adulto ativo.', 'error')
        return redirect(url_for('personalizar'))
    
    adult_prefs = adult_system.get_adult_preferences(user_id)
    return render_template('adult/config.html', 
                         user_status=user_status,
                         adult_prefs=adult_prefs)

@app.route('/adult_settings', methods=['POST'])
@login_required
def handle_adult_settings():
    """Processar configurações adultas"""
    user_id = session.get('user_id')
    user_status = adult_system.check_age(user_id)
    
    if not user_status['is_adult'] or not user_status['adult_mode_active']:
        flash('❌ Acesso negado.', 'error')
        return redirect(url_for('personalizar'))
    
    # Obter configurações do formulário
    intensity = int(request.form.get('intensity', '1'))
    style = request.form.get('style', 'romantic')
    preferences = request.form.getlist('preferences')
    boundaries = request.form.getlist('boundaries')
    
    # Atualizar preferências
    success = adult_system.set_adult_preferences(
        user_id=user_id,
        intensity=intensity,
        style=style,
        preferences=preferences,
        boundaries=boundaries
    )
    
    if success:
        flash('✅ Configurações adultas atualizadas com sucesso!', 'success')
    else:
        flash('❌ Erro ao atualizar configurações.', 'error')
    
    return redirect(url_for('adult_settings'))

@app.route('/adult_config')
@login_required
def adult_config():
    """🔥 NOVA ROTA - Sistema Avançado de Personalização Adulta"""
    user_id = session.get('user_id')
    user_profile = get_user_profile(user_id)
    
    # Verificar acesso adulto
    if not user_profile.get('has_mature_access', False):
        flash('❌ Acesso negado. Esta funcionalidade é apenas para maiores de 18 anos.', 'error')
        return redirect(url_for('personalizar'))
    
    # Obter configurações atuais do sistema avançado
    try:
        # Usar métodos que realmente existem no sistema
        current_config = adult_personality_system.get_adult_profile(user_id)
        recommendations = adult_personality_system.get_personalization_recommendations(user_id)
        
        print(f"[DEBUG] Adult Config carregado para usuário: {user_id}")
        
    except Exception as e:
        print(f"[DEBUG] Erro ao carregar configurações avançadas: {e}")
        current_config = {}
        recommendations = []
    
    return render_template('adult/config.html',
                         user_profile=user_profile,
                         current_config=current_config or {},
                         recommendations=recommendations or [])

@app.route('/adult_config', methods=['POST'])
@login_required
def save_adult_config():
    """🔥 SALVAR CONFIGURAÇÕES DO SISTEMA AVANÇADO"""
    user_id = session.get('user_id')
    user_profile = get_user_profile(user_id)
    
    # Verificar acesso adulto
    if not user_profile.get('has_mature_access', False):
        return jsonify({'success': False, 'error': 'Acesso negado'})
    
    try:
        # Obter dados do formulário
        data = request.get_json() if request.is_json else request.form
        
        personality_type = data.get('personality_type', 'romantic')
        intimacy_level = int(data.get('intimacy_level', 3))
        communication_style = data.get('communication_style', 'gentle')
        mood_preferences = data.get('mood_preferences', '')
        content_filters = data.get('content_filters', '')
        
        # Criar/atualizar perfil
        initial_preferences = {
            "personality_type": personality_type,
            "intimacy_level": intimacy_level,
            "communication_style": communication_style,
            "mood_preferences": mood_preferences,
            "content_filters": content_filters
        }
        
        success = adult_personality_system.create_adult_profile(user_id, initial_preferences)
        
        if success:
            print(f"[DEBUG] Configuração avançada salva: {personality_type}, intimidade: {intimacy_level}")
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Configurações salvas com sucesso!'})
            else:
                flash('✅ Configurações de personalidade adulta atualizadas!', 'success')
                return redirect(url_for('adult_config'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Erro interno'})
            else:
                flash('❌ Erro ao salvar configurações.', 'error')
                return redirect(url_for('adult_config'))
                
    except Exception as e:
        print(f"[DEBUG] Erro ao salvar adult config: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)})
        else:
            flash(f'❌ Erro: {str(e)}', 'error')
            return redirect(url_for('adult_config'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    from core.user_profile_db import UserProfileDB
    user_profile_db = UserProfileDB()
    app.user_profile_db = user_profile_db
    app.run(debug=True, use_reloader=False)