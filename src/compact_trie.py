from node import *
from typing import List, Tuple, Union, Dict

class CompactTrie:
    def __init__(self, max_code):
        self.root = Node()
        self.next_code = 0
        self.max_code = max_code

    def search(self, word: bytes):
        """Retorna o código do nó correspondente a palavra ou prefixo."""
        current_node = self.root
        i = 0
        while i < len(word):
            key = word[i:i+1]
            if key not in current_node.children:
                return None
            current_node = current_node.children[key]
            i += 1
        return current_node.code if current_node.isEndOfWord else None

    def cpl(self, prefix1, prefix2):
        """Calcula o tamanho do prefixo comum entre dois blocos de bytes."""
        min_len = min(len(prefix1), len(prefix2))
        for i in range(min_len):
            if prefix1[i] != prefix2[i]:
                return i
        return min_len

    def insert(self, word: bytes, code: int = None):
        """
        Insere uma sequência de bytes (word) na trie compacta.
        Se o limite de códigos for atingido, apenas retorne os códigos existentes.
        """
        if self.next_code >= self.max_code:
            return self.search(word)

        current_node = self.root
        i = 0

        while i < len(word):
            key = word[i:i+1]

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
    
    def remove(self, word: bytes):
        """Remove uma sequência de símbolos da trie."""
        def _remove(node, word, index):
            if index == len(word):
                if node.isEndOfWord:
                    node.isEndOfWord = False
                    return len(node.children) == 0
                return False

            key = word[index:index + 1]
            if key in node.children:
                child_node = node.children[key]
                should_remove = _remove(child_node, word, index + 1)

                if should_remove:
                    del node.children[key]
                    return len(node.children) == 0 and not node.isEndOfWord
            return False

        _remove(self.root, word, 0)
            
    def print_trie(self, node=None, level=0):
        if node is None:
            node = self.root

        indent = "  " * level
        for label, child in node.children.items():
            print(f"{indent}Content: {child.content}, Code: {child.code}, Is Full Word: {child.isEndOfWord}")
            self.print_trie(child, level + 1)
            
class CompactTrie2(object):
    def __init__(self):
        # Mapeamento normal (onde chave é string e valor é int)
        self.Map: Dict[str, CompactTrie2] = {}
        self.Value: Union[None, int, str] = None

    # Métodos para inserção no mapeamento
    def __setitem__(self, item: str, value: Union[int, str]) -> None:
        if len(item) == 0:
            raise KeyError("CompactTrie2 _setitem_ - Invalid item of len 0")

        current_node = self
        while item:
            # Tenta encontrar um prefixo correspondente
            found_match = False
            for prefix in list(current_node.Map.keys()):
                if item.startswith(prefix):
                    found_match = True
                    # Reduz a string de acordo com o prefixo encontrado
                    item = item[len(prefix):]
                    current_node = current_node.Map[prefix]
                    break

            if not found_match:
                # Se não encontrar prefixo, cria um novo nó para o resto da string
                current_node.Map[item] = CompactTrie2()
                current_node = current_node.Map[item]
                item = ""  # Item completamente consumido

        # Agora a chave foi inserida
        current_node.Value = value

    def __getitem__(self, item: str) -> Union[None, int, str]:
        if len(item) == 0:
            raise KeyError("CompactTrie2 _getitem_ - Invalid item of len 0")

        current_node = self
        while item:
            found_match = False
            for prefix in list(current_node.Map.keys()):
                if item.startswith(prefix):
                    found_match = True
                    item = item[len(prefix):]
                    current_node = current_node.Map[prefix]
                    break

            if not found_match:
                return None

        return current_node.Value

    # Método para excluir chave no mapeamento normal
    def delete(self, item: str) -> bool:
        if len(item) == 0:
            raise KeyError("CompactTrie2 delete - Invalid item of len 0")

        current_node = self
        path = []  # Para rastrear os nós que estamos percorrendo

        while item:
            found_match = False
            for prefix in list(current_node.Map.keys()):
                if item.startswith(prefix):
                    found_match = True
                    item = item[len(prefix):]
                    current_node = current_node.Map[prefix]
                    path.append((current_node, prefix))
                    break

            if not found_match:
                return False

        # Agora estamos no nó onde a chave termina
        if current_node.Value is not None:
            current_node.Value = None
            # Limpa o caminho se os nós não forem necessários
            for node, prefix in reversed(path):
                if node.Value is None and not node.Map:
                    del node.Map[prefix]  # Remove o nó se ele não tiver valor ou filhos
            return True
        return False

    # Função auxiliar para garantir que um nó exista
    def __ensure_not_none(self, key: str):
        if key not in self.Map:
            self.Map[key] = CompactTrie2()