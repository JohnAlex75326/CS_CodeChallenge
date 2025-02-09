#Implement an LFU (Least Frequently Used) cache. It should be able to be initialized with a cache size n, and contain the following methods:
#set(key, value): sets key to value. If there are already n items in the cache and we are adding a new item, then it should also remove the least frequently used item. If there is a tie, then the least recently used key should be removed.
#get(key): gets the value at key. If no such key exists, return null.
#Each operation should run in O(1) time.


from collections import defaultdict, OrderedDict

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.freq = 1

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data = {}  # Stores key -> Node
        self.freq_map = defaultdict(OrderedDict)  # Stores freq -> OrderedDict of nodes
        self.min_freq = 0
    
    def _update_freq(self, node: Node):
        """Helper function to update the frequency of a node."""
        del self.freq_map[node.freq][node.key]
        if not self.freq_map[node.freq]:
            del self.freq_map[node.freq]
            if node.freq == self.min_freq:
                self.min_freq += 1
        
        node.freq += 1
        self.freq_map[node.freq][node.key] = node
    
    def get(self, key: int) -> int:
        if key not in self.data:
            return None
        node = self.data[key]
        self._update_freq(node)
        return node.value
    
    def set(self, key: int, value: int):
        if self.capacity == 0:
            return
        
        if key in self.data:
            node = self.data[key]
            node.value = value
            self._update_freq(node)
        else:
            if len(self.data) >= self.capacity:
                # Evict least frequently used node
                lfu_key, lfu_node = self.freq_map[self.min_freq].popitem(last=False)
                del self.data[lfu_key]
                if not self.freq_map[self.min_freq]:
                    del self.freq_map[self.min_freq]
            
            new_node = Node(key, value)
            self.data[key] = new_node
            self.freq_map[1][key] = new_node
            self.min_freq = 1

# Testing LFUCache
lfu = LFUCache(2)
lfu.set(1, 1)
lfu.set(2, 2)
print(lfu.get(1))  # Output: 1
lfu.set(3, 3)  # Evicts key 2
print(lfu.get(2))  # Output: None
print(lfu.get(3))  # Output: 3
lfu.set(4, 4)  # Evicts key 1
print(lfu.get(1))  # Output: None
print(lfu.get(3))  # Output: 3
print(lfu.get(4))  # Output: 4