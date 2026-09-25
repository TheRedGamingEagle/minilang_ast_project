"""Define a estrutura de dados usada para representar tokens da linguagem."""

from dataclasses import dataclass

# Um token é a menor unidade reconhecida pelo analisador léxico.
@dataclass
class Token:
    # Tipo sintático do token, como NUMERO ou SOMA.
    tipo: str
    # Texto original que foi encontrado no código-fonte.
    valor: str
