"""Ponto de entrada que demonstra todas as etapas do interpretador."""

from pathlib import Path

from lexer import tokenize
from parser import Parser
from interpreter import Interpreter
from ast_printer import print_ast

def executar(codigo, interpreter):
    # Exibe o código fonte que será processado nesta rodada.
    print("\nCÓDIGO:", codigo)
    # Etapa 1: transforma o texto em tokens.
    tokens = tokenize(codigo)

    # Mostra o resultado da análise léxica para fins didáticos.
    print("\nTOKENS:")
    for token in tokens:
        print(f"{token.tipo:<22} {token.valor}")

    # Etapa 2: transforma os tokens em uma árvore sintática.
    parser = Parser(tokens)
    ast = parser.parse()

    # Exibe a estrutura criada pelo parser (uma instrução por linha do arquivo).
    for statement in ast:
        print("\nAST:")
        print_ast(statement)

        # Etapa 3: avalia a AST e atualiza a memória do interpretador.
        resultado = interpreter.evaluate(statement)
        print("\nRESULTADO:", resultado)
        print("MEMÓRIA:", interpreter.memory)

def main():
    # Um único interpretador permite que as atribuições sejam reutilizadas.
    interpreter = Interpreter()
    # O arquivo .mini contém o código-fonte do exemplo completo do programa.
    arquivo_exemplo = Path(__file__).with_name("calcula_bonus.mini")
    codigo = arquivo_exemplo.read_text(encoding="utf-8")

    # O programa inteiro percorre o pipeline completo da MiniLang.
    executar(codigo, interpreter)

# Executa a demonstração somente quando este arquivo é chamado diretamente.
if __name__ == "__main__":
    main()
