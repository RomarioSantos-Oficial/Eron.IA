import sys
import os
from src.knowledge_base import KnowledgeBase
from src.memory import EronMemory
from src.check import check_age

# Acessa os bancos de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORIA_DIR = os.path.join(BASE_DIR, 'memoria')

if __name__ == "__main__":
    print("Bem-vindo ao Eron - Seu assistente de apoio emocional!")
    if not check_age():
        print("Acesso negado. Apenas para maiores de 18 anos.")
        sys.exit()
    
    knowledge_base = KnowledgeBase(memoria_dir=MEMORIA_DIR)
    eron_memory = EronMemory(db_path=os.path.join(MEMORIA_DIR, 'eron_memory.db'))
    
    print("\nVocê pode começar a conversar. Digite 'sair' para encerrar.")
    while True:
        user_input = input("Você: ")
        if user_input.lower() == 'sair':
            print("Até logo!")
            break
        
        # Lógica principal: busca a resposta na base de conhecimento
        resposta = knowledge_base.search_answer(user_input)
        
        # Se a resposta não for encontrada, você pode usar o LLM aqui
        if not resposta:
            # Exemplo de integração com LLM local
            # from your_llm_module import get_llm_response
            # resposta = get_llm_response(user_input)
            # knowledge_base.save_qa(user_input, resposta, tema="llm_gerado")
            resposta = "Desculpe, ainda estou aprendendo. Pode me ensinar?"
            
        print(f"Eron: {resposta}")
        eron_memory.save_message(user_input, resposta)