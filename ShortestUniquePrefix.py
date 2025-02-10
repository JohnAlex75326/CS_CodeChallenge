"""
Given a list of words, return the shortest unique prefix of each word. For example, given the list:

dog
cat
apple
apricot
fish
Return the list:

d
c
app
apr
f

"""

class TrieNode:
    def __init__(self):
        self.children = {}
        self.count = 0

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
    
    def find_unique_prefix(self, word: str) -> str:
        node = self.root
        prefix = ""
        for char in word:
            prefix += char
            node = node.children[char]
            if node.count == 1:
                return prefix
        return prefix  # This case occurs if the word itself is unique

class ShortestUniquePrefixFinder:
    def __init__(self, words):
        self.trie = Trie()
        self.words = words
        for word in words:
            self.trie.insert(word)
    
    def get_unique_prefixes(self):
        return [self.trie.find_unique_prefix(word) for word in self.words]

# Example Usage
words = ["dog", "cat", "apple", "apricot", "fish"]
finder = ShortestUniquePrefixFinder(words)
print(finder.get_unique_prefixes())  # Output: ['d', 'c', 'app', 'apr', 'f']