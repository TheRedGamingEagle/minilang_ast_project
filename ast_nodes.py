"""Declara os nós que podem formar a árvore sintática abstrata (AST)."""

from dataclasses import dataclass
from typing import Optional

# Classe-base comum para todos os elementos da AST.
class ASTNode:
    pass

# Representa um número inteiro escrito no programa.
@dataclass
class Number(ASTNode):
    value: int

# Representa o uso de uma variável pelo seu nome.
@dataclass
class Identifier(ASTNode):
    name: str

# Representa uma operação entre duas expressões, como 2 + 3.
# Operações de comparação (==, !=, <, >, <=, >=) usam o mesmo nó.
@dataclass
class BinaryExpression(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode

# Representa a atribuição do resultado de uma expressão a uma variável.
@dataclass
class Assignment(ASTNode):
    target: Identifier
    value: ASTNode

# Agrupa uma sequência de instruções entre chaves { }.
@dataclass
class Block(ASTNode):
    statements: list[ASTNode]

# Representa uma escolha: if (condição) { bloco } else { bloco }.
# else_branch é None quando não há else; pode ser um Block ou outro If (else if).
@dataclass
class If(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode] = None

# Representa um laço: for (init; condição; atualização) { bloco }.
# init e update são Assignment; condition é expressão de comparação.
@dataclass
class For(ASTNode):
    init: Assignment
    condition: ASTNode
    update: Assignment
    body: Block

# Representa um laço: while (condição) { bloco }.
@dataclass
class While(ASTNode):
    condition: ASTNode
    body: Block

# Representa uma declaração: function nome(a, b) { ... }.
@dataclass
class FunctionDef(ASTNode):
    name: str
    params: list[str]
    body: Block

# Representa uma chamada: nome(expr, expr).
@dataclass
class Call(ASTNode):
    name: str
    args: list[ASTNode]

# Representa: return [expressão] ;
@dataclass
class Return(ASTNode):
    value: Optional[ASTNode] = None
