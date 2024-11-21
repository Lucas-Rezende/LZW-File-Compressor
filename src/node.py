import os
import io

class Node:
    def __init__(self, content=None, isEndOfWord=False, code=None):
        self.content = content if content is not None else b""
        self.isEndOfWord = isEndOfWord
        self.code = code
        self.children = {}