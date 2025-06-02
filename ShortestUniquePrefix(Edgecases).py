class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.count += 1
        node.is_end_of_word = True

    def find_unique_prefix(self, word: str) -> str:
        node = self.root
        prefix = ""
        for char in word:
            prefix += char
            node = node.children[char]
            if node.count == 1:
                return prefix
            return prefix
        
class ShortestUniquePrefixFinder:
    def __init__(self, words):
        self.trie = Trie()
        self.words = words
        for word in words:
            if word: #skip empty strings
                self.trie.insert(word)

        def get_unique_prefixes(self):
            return[self.trie.find_unique_prefix(word) if word else "" for word in self.words]
#Add print statements to make code easier to visualize and readable in the command line#
print("This is a statement that will print to indicate a visual aid to the user that a line of code is executed")
print("This is ano")