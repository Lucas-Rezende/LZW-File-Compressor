from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Node:
    """
    Representa um nó em uma estrutura de árvore, como uma árvore de prefixos ou trie.

    Attributes:
        content (str): Conteúdo armazenado no nó.
        children (Dict[str, Node]): Filhos de um nó.
        isEndOfWord (bool): Indica se o nó marca o fim de uma palavra completa.
        code (Optional[int]): Código associado a sequência (2^bits códigos).
    """
    content: str
    children: Dict[str, 'Node'] = field(default_factory=dict)
    isEndOfWord: bool = False
    code: Optional[int] = None

    @classmethod
    def create_root(cls):
        """
        Método de construção da raíz. A raíz é criada sem conteúdo e sem filhos, a priori.
        """
        return cls(content="", isEndOfWord=False)
    
class CompactTrie:
    """
    Implementação da trie compacta. Estão disponíveis os métodos essenciais, como inserção, busca e remoção.
    Ademais, há também um método para imprimir hierarquicamente a trie compacta e um método de comparação de prefixos.
    """
    def __init__(self):
        self.root = Node.create_root()
        self.next_code = 0

    def search(self, word: str) -> Optional[tuple[Node, Node]]:
        """
        Busca palavra na Compact Trie.
        Args:
            word: Padrão a ser buscada na trie.
        Returns:
            Optional[tuple[Node, Node]]: Retorna o último nó que forma a palavra e seu pai na trie. Caso a palavra não exista, retorna None.
        """
        current_node = self.root
        parent_node = None
        i = 0

        while i < len(word):
            key = word[i]

            if key not in current_node.children:
                return None

            aux_node = current_node.children[key]

            prefixSize = self.cpl(word[i:], aux_node.content)
            if prefixSize != len(aux_node.content):
                return None

            i += prefixSize
            parent_node = current_node
            current_node = aux_node

        if current_node.isEndOfWord:
            return current_node, parent_node
        return None

    def insert(self, word: str, code: int = None):
        """
        Insere a palavra na Compact Trie e atribui um código (automaticamente ou manualmente).
        Args:
            word: Padrão a ser inserido na trie.
            code: Código que será atribuído ao nó. Se não fornecido, será atribuído automaticamente.
        """
        current_node = self.root
        i = 0

        while i < len(word):
            key = word[i]

            if key not in current_node.children:
                new_node = Node(word[i:], isEndOfWord=True)
                if code is not None:
                    new_node.code = code
                else:
                    new_node.code = self.next_code
                    self.next_code += 1
                current_node.children[key] = new_node
                return new_node.code

            aux_node = current_node.children[key]

            prefixSize = self.cpl(word[i:], aux_node.content)

            if prefixSize == len(aux_node.content):
                i += prefixSize
                current_node = aux_node

            else:
                new_node = Node(aux_node.content[prefixSize:], isEndOfWord=aux_node.isEndOfWord, code=aux_node.code)
                new_node.children = aux_node.children

                aux_node.content = aux_node.content[:prefixSize]
                aux_node.isEndOfWord = False
                aux_node.code = None
                aux_node.children = {new_node.content[0]: new_node}

                if prefixSize < len(word[i:]):
                    remaining_node = Node(word[i + prefixSize:], isEndOfWord=True)
                    if code is not None:
                        remaining_node.code = code
                    else:
                        remaining_node.code = self.next_code
                        self.next_code += 1
                    aux_node.children[remaining_node.content[0]] = remaining_node
                    return remaining_node.code
                else:
                    aux_node.isEndOfWord = True
                    if code is not None:
                        aux_node.code = code
                    else:
                        aux_node.code = self.next_code
                        self.next_code += 1
                    return aux_node.code

        if current_node.isEndOfWord and current_node.code is None:
            if code is not None:
                current_node.code = code
            else:
                current_node.code = self.next_code
                self.next_code += 1

        return current_node.code


    def remove(self, word: str) -> bool:
        """
        Remove a palavra da Compact Trie.
        Idea: To delete a string x from a tree, we first locate the leaf representing x. Then, assuming x exists, we remove the corresponding leaf node.
        If the parent of our leaf node has only one other child, then that child's incoming label is appended to the parent's incoming label and the child is removed.
        Args:
            word: Padrão a ser inserido na trie.
        """
        result = self.search(word)

        if result is None:
            return False

        current_node, parent_node = result

        if len(current_node.children) > 0:
            current_node.isEndOfWord = False
            return True

        key_to_remove = current_node.content[0]
        del parent_node.children[key_to_remove]

        if len(parent_node.children) == 1 and not parent_node.isEndOfWord:
            only_child_key = next(iter(parent_node.children))
            only_child = parent_node.children[only_child_key]
            parent_node.content += only_child.content
            parent_node.isEndOfWord = only_child.isEndOfWord
            parent_node.children = only_child.children

        return True

    def cpl(self, a: str, b: str) -> int:
        """
        Verifica o tamanho do maior prefixo em comum entre duas strings.
        Args:
            a: Primeira string.
            b: Segunda string
        """
        length = 0
        index = 0
        while length < len(a) and length < len(b) and a[index] == b[index]:
            length += 1
            index += 1
        return length

    def print_trie(self, node=None, prefix=''):
        """
        Imprime hierarquicamente os elementos da trie.
        """
        if node is None:
            node = self.root

        for key, child in node.children.items():
            end_marker = ' (End of word)' if child.isEndOfWord else ''
            print(f"{prefix}{child.content}{end_marker}")
            self.print_trie(child, prefix + '  ')

def lzw_encoder(textoNormal):
    """
        Codificar um arquivo usando o algoritmo LZW.
    """
    dicionario = CompactTrie()

    for i in range(0,256):
        dicionario.insert(chr(i))

    ret = []
    buffer = ''
    for i in range(0, len(textoNormal)):
        c = textoNormal[i]
        if len(buffer) == 0 or dicionario.search(buffer + c):
            buffer = buffer + c
        else:
            code = dicionario.search(buffer)[0].code
            dicionario.insert(buffer + c)
            buffer = c
            ret = ret + [code]
    if buffer:
        ret = ret + [dicionario.search(buffer)[0].code]
    return ret

def lzw_decoder(symbols):
    """ Classe usada para decodificar um arquivo codificado com LZW.
        Segue as mesmas restrições de lzw_encoder

        Decodifica o arquivo. Emite sequêncialmente as cadeias correspondentes
        aos códigos lidos. Caso a concatenação dos códigos lidos não corresponda
        a uma cadeia existente, acrescenta no dicionário como uma nova cadeia. """
    dicionario = CompactTrie()

    for i in range(0,256):
        dicionario.insert(str(i), chr(i))

    codigosUsados = 256
    last_symbol = symbols[0]
    ret = dicionario.search(str(last_symbol))[0].code
    for symbol in symbols[1:]:
        if dicionario.search(str(symbol)) != None:
            current = dicionario.search(str(symbol))[0].code
            previous = dicionario.search(str(last_symbol))[0].code
            to_add = current[0]
            dicionario.insert(str(codigosUsados), previous + to_add)
            codigosUsados = codigosUsados + 1
            ret = ret + current
        else:
            previous = dicionario.search(str(last_symbol))[0].code
            to_add = previous[0]
            dicionario.insert(str(codigosUsados), previous + to_add)
            codigosUsados = codigosUsados + 1
            ret = ret + previous + to_add
        last_symbol = symbol
    return ret

if __name__ == "__main__":
    string = ''
    string = 'TESTETESTETESTETESTETESTE'
    print(" ".join(str(ord(char)) for char in string))
    encoded = lzw_encoder(string)
    print ('encoded:', encoded)

    decoded = lzw_decoder(encoded)
    print ('decoded:', decoded)