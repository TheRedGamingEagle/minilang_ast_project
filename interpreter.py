"""Executa a AST da MiniLang e mantém os valores das variáveis em memória."""

from ast_nodes import Number, Identifier, BinaryExpression, Assignment

# Interpretador que avalia cada tipo de nó recursivamente.
class Interpreter:
    def __init__(self):
        # O dicionário funciona como a memória de variáveis do programa.
        self.memory = {}

    def evaluate(self, node):
        if isinstance(node, Number):
            # Números já chegam convertidos pelo parser.
            return node.value
        if isinstance(node, Identifier):
            # Uma variável precisa ter sido atribuída antes de ser usada.
            if node.name not in self.memory:
                raise NameError(f"Variável '{node.name}' não definida.")
            return self.memory[node.name]
        if isinstance(node, BinaryExpression):
            # Primeiro avalia os dois lados; isso também resolve variáveis aninhadas.
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            # Aplica a operação registrada no nó da AST.
            if node.operator == "+": return left + right
            if node.operator == "-": return left - right
            if node.operator == "*": return left * right
            if node.operator == "/":
                # Evita que a divisão por zero chegue ao operador do Python.
                if right == 0: raise ZeroDivisionError("Divisão por zero.")
                return left / right
        if isinstance(node, Assignment):
            # O valor é calculado antes de ser salvo no nome de destino.
            value = self.evaluate(node.value)
            self.memory[node.target.name] = value
            return value
        # Qualquer classe nova de nó precisa ser tratada explicitamente.
        raise ValueError(f"Nó desconhecido: {type(node).__name__}")
