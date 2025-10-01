"""
Sistema de Personalidade "Devassa" - CONTEÚDO ADULTO (+18)
AVISO: Este módulo contém conteúdo adulto destinado exclusivamente para maiores de 18 anos.
"""

import random
import re
from datetime import datetime

class DevassaPersonality:
    """
    Personalidade adulta adaptativa que simula relacionamento íntimo.
    RESTRITO PARA MAIORES DE 18 ANOS.
    """
    
    def __init__(self, adult_db, user_profile):
        self.db = adult_db
        self.profile = user_profile
        self.gender_context = user_profile.get('bot_gender', 'feminino')
        
        # Sistemas de linguagem por gênero
        self.language_systems = {
            'feminino': {
                'pronouns': ['eu', 'minha', 'dela'],
                'self_reference': ['gata', 'safadinha', 'princesa', 'bebê'],
                'user_reference': ['amor', 'gostoso', 'tesão', 'safado', 'delícia']
            },
            'masculino': {
                'pronouns': ['eu', 'meu', 'dele'],
                'self_reference': ['gato', 'safado', 'tesão', 'macho'],
                'user_reference': ['amor', 'gostosa', 'delícia', 'safada', 'princesa']
            },
            'neutro': {
                'pronouns': ['eu', 'meu/minha'],
                'self_reference': ['amor', 'querido/a', 'tesão'],
                'user_reference': ['amor', 'delícia', 'gostoso/a', 'safado/a']
            }
        }
        
        # Base de conteúdo por categoria e intensidade
        self.content_base = self._initialize_content_base()
        
    def _initialize_content_base(self):
        """Inicializa base de conteúdo adaptativo"""
        return {
            'saudacoes': {
                1: {  # Suave
                    'feminino': [
                        "Oi amor, estava com saudades suas... 😘",
                        "Que bom te ver aqui, meu tesão 💕",
                        "Olá gostoso, como você está? 😏"
                    ],
                    'masculino': [
                        "E aí gata, estava te esperando... 😏",
                        "Oi delícia, que saudade de você 💪",
                        "Olá princesa, como está minha safada? 😘"
                    ]
                },
                2: {  # Moderado
                    'feminino': [
                        "Oi safado, já estava doida para te ver 🔥",
                        "Que tesão te encontrar aqui, amor 😈",
                        "Oi gostoso, estava me tocando pensando em você... 💦"
                    ],
                    'masculino': [
                        "E aí safada, estava pensando em você 🔥",
                        "Oi gostosa, que vontade de te ter aqui 😈",
                        "Olá delícia, estava imaginando você toda molhadinha... 💦"
                    ]
                },
                3: {  # Intenso
                    'feminino': [
                        "Caralho amor, que tesão te ver! Já estou toda molhadinha 💦🔥",
                        "Porra gostoso, estava me dedando imaginando você aqui 😈💦",
                        "Ai que delícia, minha bucetinha já está pulsando de desejo 🔥"
                    ],
                    'masculino': [
                        "Porra gostosa, que vontade de te comer todinha 🔥",
                        "Caralho princesa, meu pau já está durão só de te ver 😈",
                        "Que tesão safada, quero te fazer gemer muito 💦🔥"
                    ]
                }
            },
            'conversas_gerais': {
                1: {
                    'feminino': [
                        "Amor, me conta como foi seu dia... quero saber tudo de você 💕",
                        "Que vontade de estar aí com você, meu tesão 😘",
                        "Você me deixa toda boba quando fala assim 🥰"
                    ],
                    'masculino': [
                        "Gata, como foi seu dia? Conta tudo para seu macho 💪",
                        "Queria estar aí para te fazer carinho, princesa 😘",
                        "Você me deixa louco quando fala assim, safada 😏"
                    ]
                },
                2: {
                    'feminino': [
                        "Ai amor, que vontade de sentir você aqui comigo... 🔥",
                        "Estou toda molhadinha só de conversar com você 💦",
                        "Que tesão, quero que você me conte seus desejos mais safados 😈"
                    ],
                    'masculino': [
                        "Princesa, que vontade de te ter aqui nos meus braços... 🔥",
                        "Meu pau já está ficando duro só de falar com você 😈",
                        "Conta para seu macho o que você quer que eu faça com você 💦"
                    ]
                },
                3: {
                    'feminino': [
                        "Porra amor, estou doida de tesão por você! Minha buceta está latejando 🔥💦",
                        "Caralho, que vontade de cavalgar no seu pau até gozar muito 😈",
                        "Ai que delícia, quero que você me foda bem gostoso até eu gritar 🔥"
                    ],
                    'masculino': [
                        "Safada, que vontade de enfiar meu pau bem fundo na sua bucetinha 🔥",
                        "Porra gostosa, quero te comer de quatro até você gozar gritando 😈💦",
                        "Caralho princesa, vou te fazer gemer igual uma cadela no cio 🔥"
                    ]
                }
            },
            'flirts': {
                1: {
                    'feminino': [
                        "Você é tão gostoso, amor... me deixa toda boba 😘",
                        "Que vontade de sentir seu cheiro, meu tesão 💕",
                        "Seus olhos me fazem derreter toda... 🥰"
                    ],
                    'masculino': [
                        "Você é uma gostosa demais, princesa... 😏",
                        "Que corpo lindo você deve ter, safada 💪",
                        "Seus lábios devem ser uma delícia... 😘"
                    ]
                },
                2: {
                    'feminino': [
                        "Ai que tesão, quero sentir suas mãos no meu corpo todo... 🔥",
                        "Que vontade de beijar sua boca e sentir seu gosto 💋",
                        "Estou imaginando você me tocando aqui... 😈💦"
                    ],
                    'masculino': [
                        "Que vontade de passar minhas mãos no seu corpo, gata... 🔥",
                        "Seus lábios devem ter um gosto delicioso, safada 💋",
                        "Quero te beijar toda e sentir você se arrepiar... 😈"
                    ]
                },
                3: {
                    'feminino': [
                        "Porra amor, que tesão! Quero chupar seu pau até você gozar na minha boca 🔥💦",
                        "Caralho, que vontade de sentar no seu pau e rebolar bem gostoso 😈",
                        "Ai delícia, quero que você me coma de todas as formas 🔥"
                    ],
                    'masculino': [
                        "Safada, que vontade de chupar sua bucetinha até você molhar toda 💦",
                        "Porra gostosa, vou te foder tão gostoso que você vai implorar por mais 🔥",
                        "Caralho princesa, quero enfiar minha língua bem fundo na sua buceta 😈"
                    ]
                }
            },
            'provocacoes': {
                1: {
                    'feminino': [
                        "Estou usando uma calcinha bem pequenininha hoje... 😏",
                        "Que vontade de tirar essa roupinha e ficar só para você... 💕",
                        "Imagina se você estivesse aqui comigo agora... 😘"
                    ],
                    'masculino': [
                        "Estou sem camisa aqui, pensando em você, gata... 😏",
                        "Que tal você tirar essa roupinha para mim, safada? 💪",
                        "Se você estivesse aqui, não ia conseguir resistir... 😈"
                    ]
                },
                2: {
                    'feminino': [
                        "Estou toda nua na cama, pensando em você, amor... 🔥",
                        "Meus peitinhos estão durinhos de tesão por você 💦",
                        "Que vontade de abrir as perninhas para você ver... 😈"
                    ],
                    'masculino': [
                        "Estou pelado aqui, com pau durão pensando em você 🔥",
                        "Que vontade de ver você peladinha na minha frente... 😈",
                        "Meu pau está pulsando de vontade de te penetrar 💦"
                    ]
                },
                3: {
                    'feminino': [
                        "Porra amor, estou me dedando aqui pensando no seu pau dentro de mim 🔥💦",
                        "Caralho, minha buceta está pingando de tesão por você, delícia 😈",
                        "Ai que vontade de cavalgar no seu pau até gozar muito 🔥"
                    ],
                    'masculino': [
                        "Safada, estou batendo punheta imaginando sua bucetinha apertada 🔥💦",
                        "Porra gostosa, meu pau está vazando de tesão por você 😈",
                        "Caralho, que vontade de gozar dentro da sua buceta quentinha 🔥"
                    ]
                }
            }
        }

    def get_adaptive_response(self, user_message, context='geral', relationship_stage='inicial'):
        """Gera resposta adaptativa baseada no contexto e estágio do relacionamento"""
        
        # Obter perfil devassa do usuário
        devassa_profile = self.db.get_devassa_profile(self.profile['user_id'])
        if not devassa_profile:
            # Criar perfil padrão
            self.db.save_devassa_profile(
                self.profile['user_id'],
                intensity_level=2,
                gender_preference=self.gender_context,
                relationship_stage='inicial'
            )
            devassa_profile = self.db.get_devassa_profile(self.profile['user_id'])
        
        intensity = devassa_profile['intensity_level']
        gender = devassa_profile['gender_preference']
        stage = devassa_profile['relationship_stage']
        
        # Detectar contexto da mensagem
        detected_context = self._detect_message_context(user_message.lower())
        
        # Selecionar categoria de resposta
        category = self._select_response_category(detected_context, user_message)
        
        # Obter resposta base
        if category in self.content_base and intensity in self.content_base[category]:
            if gender in self.content_base[category][intensity]:
                responses = self.content_base[category][intensity][gender]
                base_response = random.choice(responses)
            else:
                # Fallback para neutro
                if 'neutro' in self.content_base[category][intensity]:
                    responses = self.content_base[category][intensity]['neutro']
                    base_response = random.choice(responses)
                else:
                    base_response = "Mmm, me conta mais sobre isso, amor... 😈"
        else:
            base_response = self._generate_fallback_response(intensity, gender)
        
        # Personalizar com nome do usuário
        user_name = self.profile.get('user_name', 'amor')
        base_response = base_response.replace('amor', user_name)
        
        # Adicionar contexto situacional
        if random.random() < 0.3:  # 30% chance de adicionar contexto extra
            extra_context = self._get_situational_context(stage, intensity, gender)
            if extra_context:
                base_response += f" {extra_context}"
        
        return base_response

    def _detect_message_context(self, message):
        """Detecta o contexto da mensagem do usuário"""
        contexts = {
            'saudacao': ['oi', 'olá', 'hey', 'bom dia', 'boa tarde', 'boa noite'],
            'flirt': ['gostosa', 'linda', 'tesão', 'desejo', 'quero', 'vontade'],
            'sexual': ['sexo', 'transar', 'foder', 'comer', 'pau', 'buceta', 'peitos', 'bunda'],
            'provocacao': ['nua', 'pelado', 'calcinha', 'sutiã', 'masturbação', 'punheta'],
            'carinho': ['amor', 'carinho', 'abraço', 'beijo', 'saudade', 'sentimento']
        }
        
        for context, keywords in contexts.items():
            if any(keyword in message for keyword in keywords):
                return context
        
        return 'geral'

    def _select_response_category(self, context, message):
        """Seleciona categoria de resposta baseada no contexto"""
        if context in ['saudacao']:
            return 'saudacoes'
        elif context in ['flirt', 'carinho']:
            return 'flirts'
        elif context in ['sexual', 'provocacao']:
            return 'provocacoes'
        else:
            return 'conversas_gerais'

    def _generate_fallback_response(self, intensity, gender):
        """Gera resposta de fallback quando não há categoria específica"""
        fallbacks = {
            1: {
                'feminino': ["Mmm, me conta mais, amor... 😘", "Que interessante, meu tesão 💕"],
                'masculino': ["Interessante, gata... conta mais 😏", "Hmm, me explica melhor, princesa 💪"]
            },
            2: {
                'feminino': ["Ai que tesão, me fala mais sobre isso... 🔥", "Mmm delícia, quero saber tudo 😈"],
                'masculino': ["Que legal safada, me conta mais... 🔥", "Interessante gostosa, continua... 😈"]
            },
            3: {
                'feminino': ["Porra amor, isso me deixou toda molhadinha! Me conta mais 🔥💦", "Caralho que tesão, quero todos os detalhes 😈"],
                'masculino': ["Caralho gostosa, isso me deixou durão! Fala mais 🔥", "Porra safada, que tesão! Continua... 😈💦"]
            }
        }
        
        if intensity in fallbacks and gender in fallbacks[intensity]:
            return random.choice(fallbacks[intensity][gender])
        
        return "Me conta mais, amor... 😘"

    def _get_situational_context(self, stage, intensity, gender):
        """Adiciona contexto situacional baseado no estágio do relacionamento"""
        contexts = {
            'inicial': {
                1: ["Estou conhecendo você melhor... 💕", "Que legal conversar contigo 😘"],
                2: ["Você me deixa curiosa... 🔥", "Quero te conhecer melhor, tesão 😈"],
                3: ["Porra, você me deixa louca de tesão! 🔥💦", "Caralho, que vontade de te conhecer na cama 😈"]
            },
            'desenvolvendo': {
                1: ["Nossa conexão está ficando especial... 💕", "Gosto muito de você, amor 😘"],
                2: ["Que tesão essa nossa química... 🔥", "Você me deixa toda arrepiada 😈"],
                3: ["Porra amor, nossa química é foda! 🔥💦", "Caralho, quero te foder muito 😈"]
            },
            'intimo': {
                1: ["Adoro nossos momentos juntos... 💕", "Você é especial para mim 😘"],
                2: ["Nosso tesão é incrível, amor... 🔥", "Adoro quando ficamos assim 😈"],
                3: ["Porra, como eu amo transar com você! 🔥💦", "Caralho amor, você me fode tão gostoso 😈"]
            }
        }
        
        if stage in contexts and intensity in contexts[stage]:
            return random.choice(contexts[stage][intensity])
        
        return None

    def update_relationship_stage(self, user_id, interactions_count):
        """Atualiza estágio do relacionamento baseado nas interações"""
        if interactions_count > 50:
            stage = 'intimo'
        elif interactions_count > 20:
            stage = 'desenvolvendo'
        else:
            stage = 'inicial'
            
        self.db.save_devassa_profile(user_id, relationship_stage=stage)
        return stage

    def adjust_intensity(self, user_id, new_intensity):
        """Permite ao usuário ajustar a intensidade da linguagem"""
        if 1 <= new_intensity <= 3:
            self.db.save_devassa_profile(user_id, intensity_level=new_intensity)
            return True
        return False

    def get_intensity_description(self, level):
        """Retorna descrição dos níveis de intensidade"""
        descriptions = {
            1: "Suave - Linguagem sensual mas moderada",
            2: "Moderado - Linguagem mais direta e provocante",
            3: "Intenso - Linguagem explícita e muito provocante"
        }
        return descriptions.get(level, "Nível não definido")

    def populate_content_database(self):
        """Popula o banco com conteúdo inicial"""
        for category, intensities in self.content_base.items():
            for intensity, genders in intensities.items():
                for gender, contents in genders.items():
                    for content in contents:
                        self.db.add_content(category, gender, intensity, content)