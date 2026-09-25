"""Executa a AST da MiniLang e mantém os valores das variáveis em memória."""

from ast_nodes import (
    Number, Identifier, BinaryExpression, Assignment,
    Block, If, For, While, FunctionDef, Call, Return,
)

# Exceção interna usada para encerrar a execução de uma função via return.
class RetornoSinal(Exception):
    def __init__(self, valor=None):
        super().__init__("Instrução 'return' fora de uma função.")
        self.valor = valor

# Interpretador que avalia cada tipo de nó recursivamente.
class Interpreter:
    def __init__(self):
        # O dicionário funciona como a memória de variáveis globais do programa.
        self.memory = {}
        # Pilha de escopos locais, criados ao entrar em uma função.
        self.locais: list = []
        # Tabela de funções declaradas pelo programa.
        self.functions = {}
        # Guardas de proteção contra laços e recursões sem fim.
        self.max_loop_iterations = 10000

    def evaluate(self, node):
        if isinstance(node, Number):
            # Números já chegam convertidos pelo parser.
            return node.value
        if isinstance(node, Identifier):
            # Procura do escopo mais interno para o global.
            for frame in reversed(self.locais):
                if node.name in frame:
                    return frame[node.name]
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
            self.guardar(node.target.name, value)
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
                    raise RuntimeError(
                        f"Laço excedeu {self.max_loop_iterations} iterações."
                    )
                self.evaluate(node.body)
                self.evaluate(update)
            return None
        if isinstance(node, While):
            # Enquanto a condição continuar verdadeira, o corpo é repetido.
            iterations = 0
            while self.evaluate(node.condition):
                iterations += 1
                if iterations > self.max_loop_iterations:
                    raise RuntimeError(
                        f"Laço excedeu {self.max_loop_iterations} iterações."
                    )
                self.evaluate(node.body)
            return None
        if isinstance(node, FunctionDef):
            # A declaração apenas registra a função para uso futuro.
            self.functions[node.name] = node
            return None
        if isinstance(node, Call):
            try:
                return self.chamar(node)
            except RecursionError:
                raise RecursionError(
                    f"Recursão profunda demais ao chamar '{node.name}'."
                )
        if isinstance(node, Return):
            # Encerra a função imediatamente, carregando o valor devolvido.
            valor = None if node.value is None else self.evaluate(node.value)
            raise RetornoSinal(valor)
        # Qualquer classe nova de nó precisa ser tratada explicitamente.
        raise ValueError(f"Nó desconhecido: {type(node).__name__}")

    def guardar(self, nome, valor):
        # Grava a variável no escopo mais interno que já a possui. Nomes
        # existentes são atualizados onde vivem (inclusive no global); um
        # nome novo passa a viver no escopo local (ou no global, fora de funções).
        for frame in reversed(self.locais):
            if nome in frame:
                frame[nome] = valor
                return
        if nome in self.memory:
            self.memory[nome] = valor
            return
        if self.locais:
            self.locais[-1][nome] = valor
        else:
            self.memory[nome] = valor

    def chamar(self, call):
        # Executa a função com uma memória local nova: os parâmetros entram
        # nela e o escopo global continua acessível somente para leitura.
        if call.name not in self.functions:
            raise NameError(f"Função '{call.name}' não definida.")
        defn = self.functions[call.name]
        if len(call.args) != len(defn.params):
            raise TypeError(
                f"Função '{call.name}' espera {len(defn.params)} parâmetro(s), "
                f"recebeu {len(call.args)} argumento(s)."
            )
        argumentos = [self.evaluate(arg) for arg in call.args]
        self.locais.append(
            {nome: valor for nome, valor in zip(defn.params, argumentos)}
        )
        try:
            self.evaluate(defn.body)
        except RetornoSinal as sinal:
            return sinal.valor
        finally:
            self.locais.pop()
        # Função sem return devolve None.
        return None

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
