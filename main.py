import sys
from eron.memory import EronMemory
from eron.check import check_age

def main():
    print("Bem-vindo ao Eron - Seu assistente de apoio emocional para adultos!")
    if not check_age():
        print("Acesso negado. Apenas para maiores de 18 anos.")
        sys.exit()
    memory = EronMemory()
    print("\nVocê pode começar a conversar. Digite 'sair' para encerrar.")
    while True:
        user_input = input("Você: ")
        if user_input.lower() == 'sair':
            print("Até logo!")
            break
        # Aqui você pode adicionar lógica de IA e integração com APIs
        resposta = f"(Eron) Eu ouvi: {user_input}"  # Resposta simples
        print(resposta)
        memory.save_message(user_input, resposta)

if __name__ == "__main__":
    main()
