def check_age():
    try:
        idade = int(input("Por favor, informe sua idade: "))
        return idade >= 18
    except ValueError:
        print("Idade inválida.")
        return False