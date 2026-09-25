"""Imprime a árvore sintática abstrata em um formato hierárquico legível."""

from ast_nodes import (
Number, Identifier, BinaryExpression, Assignment,
Block, If, For, While, FunctionDef, Call, Return,
)

def print_ast(node, indent=""):
    # O recuo representa a profundidade do nó dentro da árvore.
    if isinstance(node, Assignment):
        # A atribuição possui um destino e uma expressão de valor.
        print(indent + "Assignment")
        print(indent + "  target:")
        print_ast(node.target, indent + "    ")
        print(indent + "  value:")
        print_ast(node.value, indent + "    ")
    elif isinstance(node, If):
        # Mostra a condição e as duas ramificações possíveis.
        print(indent + "If")
        print(indent + "  condition:")
        print_ast(node.condition, indent + "    ")
        print(indent + "  then:")
        print_ast(node.then_branch, indent + "    ")
        if node.else_branch is not None:
            print(indent + "  else:")
            print_ast(node.else_branch, indent + "    ")
    elif isinstance(node, For):
        # Mostra as três cláusulas do laço e o corpo com as repetições.
        print(indent + "For")
        print(indent + "  init:")
        print_ast(node.init, indent + "    ")
        print(indent + "  condition:")
        print_ast(node.condition, indent + "    ")
        print(indent + "  update:")
        print_ast(node.update, indent + "    ")
        print(indent + "  body:")
        print_ast(node.body, indent + "    ")
    elif isinstance(node, While):
        # Mostra a condição verificada a cada repetição.
        print(indent + "While")
        print(indent + "  condition:")
        print_ast(node.condition, indent + "    ")
        print(indent + "  body:")
        print_ast(node.body, indent + "    ")
    elif isinstance(node, FunctionDef):
        # Mostra o nome, os parâmetros e o corpo da função.
        params = ", ".join(node.params)
        print(indent + f"FunctionDef({node.name}({params}))")
        print(indent + "  body:")
        print_ast(node.body, indent + "    ")
    elif isinstance(node, Call):
        # Mostra a função chamada e cada argumento.
        print(indent + f"Call({node.name})")
        for argumento in node.args:
            print_ast(argumento, indent + "  ")
    elif isinstance(node, Return):
        # Mostra o valor devolvido, quando existe.
        print(indent + "Return")
        if node.value is not None:
            print_ast(node.value, indent + "  ")
    elif isinstance(node, Block):
        # Um bloco lista todas as suas instruções sob o mesmo recuo.
        print(indent + "Block")
        for statement in node.statements:
            print_ast(statement, indent + "  ")
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
