import pickle
import re

class Node(object):
    def __init__(self, char: str):
        self.char = char
        self.is_end = False
        self.counter = 0
        self.children = {}
        self.status_ids = set()

class Trie(object):
    
    def __init__(self):
        self.root: Node = Node("")
        self.char_hash: dict = {}
            
    def __filter_chars(self, status: str, to_lower: bool = True) -> str:
        char_filter: str = ""
        if to_lower:
            status = status.lower()
        for char in status:
            if (97 <= ord(char) <= 122) or (not to_lower and (65 <= ord(char) <= 90)) or char == ' ':
                char_filter += char
            else:
                char_filter += " "
        return char_filter.strip()
        
    def insert(self, status: str, id: str):
        status: str = self.__filter_chars(status)
        words = status.split(" ")    
        
        for word in words:
            node = self.root
            for char in word:
                if char in node.children:
                    node = node.children[char]
                else:
                    new_node: Node = Node(char)
                    node.children[char] = new_node
                    node = new_node
                    if char not in self.char_hash:
                        self.char_hash.update({char : [node]})
                    else:
                        self.char_hash[char].append(node)
                    
            node.status_ids.add(id)
            node.counter += 1
            node.is_end = True
        
    
    def autocomplete(self, prefix: str) -> dict:
        prefix = self.__filter_chars(prefix)
        node: Node = self.root
    
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        words: list = self.__get_words_from_prefix(node, prefix)
        words.sort(key = lambda w: w[1], reverse=True)
        return words
        
    def __get_words_from_prefix(self, node: Node, prefix: str) -> list:
        words = []
        
        if node.is_end:
            words.append((prefix, node.counter))
        
        for char, child in node.children.items():
            words.extend(self.__get_words_from_prefix(child, prefix + char))
        
        return words
    
    def search_words_union(self, term: str) -> dict:
        term = self.__filter_chars(term)
        words: list = re.findall(r'\b\w+\b', term)
        status_ids: dict = {}
        for word in words:
            word_ids: list = list(self.__quary(word))
            for status_id in word_ids:
                if status_id in status_ids:
                    status_ids[status_id] = status_ids[status_id] + 1
                else:
                    status_ids.update({status_id : 1})
            
        return status_ids
    
    def __search(self, word: str, counter: int, node: Node):
        if len(word) == counter:
            return node.status_ids
            
        ids = set()
        char = word[counter]
        if char in node.children:
            status_ids = self.__search(word, counter + 1, node.children[char])
            if status_ids:
                ids.update(status_ids)
        
        return ids

    def has_phrase(self, status: str, phrase: str) -> bool:
        status = self.__filter_chars(status)
        phrase_len: int = len(phrase)
        status_len: int = len(status)
        
        bad_char = {}
        for i in range(phrase_len):
            bad_char[phrase[i]] = i 
        
        i: int = phrase_len - 1       
        k: int = phrase_len - 1
        while i < status_len:
            if status[i] == phrase[k]:
                if k == 0:
                    return True, i
                else:
                    i -= 1
                    k -= 1
            else:
                j = bad_char.get(status[i], -1)
                i += phrase_len - min(k, j + 1)
                k = phrase_len - 1
        return False, None
        
    def search_phrases(self, phrase: str, statuses: dict):
        phrase = self.__filter_chars(phrase)

        status_ids: list = []
        for status in statuses:
            message = statuses[status]['status_message']
            message = self.__filter_chars(message)
            has_phrase, _ = self.has_phrase(message, " " + phrase + " ")
            if has_phrase:
                status_ids.append(status)
                

        return status_ids
 
    def __quary(self, term: str) -> set:
        chars = "".join(self.__filter_chars(term).split(" "))        
        if len(chars) == 0:
            return set()
        
        ids = set()
        if chars[0] not in self.char_hash:
            return ids
        
        nodes: list[Node] = self.char_hash[chars[0]]
        for node in nodes:
            node_id = self.__search(chars, 1, node)
            if node_id:
                ids.update(node_id)

        return ids

if __name__ == "__main__":
    # trie: Trie = Trie.load("trie.obj")

    trie: Trie = Trie()
    status_dict: dict = {
        1 : {"status_message" : "this is not is not doing great "},
        2 : {"status_message" : "is not doing great things"},
        3 : {"status_message" : "is totally not doing great"},
    }
    for status in status_dict:
        trie.insert(status_dict[status]['status_message'], status)
    
    print(trie.search_phrases("is not doing great", status_dict))