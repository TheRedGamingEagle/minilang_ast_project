"""Executa a AST da MiniLang e mantém os valores das variáveis em memória."""

from ast_nodes import (
    Number, Identifier, BinaryExpression, Assignment,
    Block, If, For,
)

# Interpretador que avalia cada tipo de nó recursivamente.
class Interpreter:
    def __init__(self):
        # O dicionário funciona como a memória de variáveis do programa.
        self.memory = {}
        # Rastreia o número de vezes que um corpo de laço já rodou.
        self.max_loop_iterations = 10000

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
            return self.apply_operator(node.operator, left, right)
        if isinstance(node, Assignment):
            # O valor é calculado antes de ser salvo no nome de destino.
            value = self.evaluate(node.value)
            self.memory[node.target.name] = value
            return value
        if isinstance(node, If):
            # A condição decide qual das duas ramificações será executada.
            if self.evaluate(node.condition):
                return self.evaluate(node.then_branch)
            if node.else_branch is not None:
                # Sem else, um if falso simplesmente não faz nada.
                return self.evaluate(node.else_branch)
            return None
        if isinstance(node, Block):
            # Todas as instruções do bloco rodam em ordem.
            result = None
            for statement in node.statements:
                result = self.evaluate(statement)
            return result
        if isinstance(node, For):
            init, condition, update = node.init, node.condition, node.update
            # A inicialização roda uma única vez, antes do laço.
            self.evaluate(init)
            iterations = 0
            while self.evaluate(condition):
                # Guarda contra laços infinitos acidentais neste projeto didático.
                iterations += 1
                if iterations > self.max_loop_iterations:
                    raise RecursionError(
                        f"Laço excedeu {self.max_loop_iterations} iterações."
                    )
                self.evaluate(node.body)
                self.evaluate(update)
            return None
        # Qualquer classe nova de nó precisa ser tratada explicitamente.
        raise ValueError(f"Nó desconhecido: {type(node).__name__}")

    def apply_operator(self, operator, left, right):
        # Aplica a operação registrada no nó da AST.
        if operator == "+": return left + right
        if operator == "-": return left - right
        if operator == "*": return left * right
        if operator == "/":
            # Evita que a divisão por zero chegue ao operador do Python.
            if right == 0: raise ZeroDivisionError("Divisão por zero.")
            return left / right
        # Operadores de comparação sempre devolvem um booleano.
        if operator == "==": return left == right
        if operator == "!=": return left != right
        if operator == "<": return left < right
        if operator == ">": return left > right
        if operator == "<=": return left <= right
        if operator == ">=": return left >= right
        raise ValueError(f"Operador desconhecido: {operator}")
