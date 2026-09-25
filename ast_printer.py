"""Imprime a árvore sintática abstrata em um formato hierárquico legível."""

from ast_nodes import Number, Identifier, BinaryExpression, Assignment

def print_ast(node, indent=""):
    # O recuo representa a profundidade do nó dentro da árvore.
    if isinstance(node, Assignment):
        # A atribuição possui um destino e uma expressão de valor.
        print(indent + "Assignment")
        print(indent + "  target:")
        print_ast(node.target, indent + "    ")
        print(indent + "  value:")
        print_ast(node.value, indent + "    ")
    elif isinstance(node, BinaryExpression):
        # Mostra o operador e depois imprime os operandos recursivamente.
        print(indent + f"BinaryExpression({node.operator})")
        print_ast(node.left, indent + "  ")
        print_ast(node.right, indent + "  ")
    elif isinstance(node, Number):
        # Folha da árvore que contém um valor numérico.
        print(indent + f"Number({node.value})")
    elif isinstance(node, Identifier):
        # Folha da árvore que contém o nome de uma variável.
        print(indent + f'Identifier("{node.name}")')
