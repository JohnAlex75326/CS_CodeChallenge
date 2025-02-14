class ListNode:
    def __init__(self, value=0, next=None):
        self.value = value
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, value):
        if not self.head:
            self.head = ListNode(value)
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = ListNode(value)
    
    def rotate_right(self, k):
        if not self.head or k == 0:
            return
        
        # Compute the length of the list
        length = 1
        tail = self.head
        while tail.next:
            tail = tail.next
            length += 1
        
        # Connect the tail to the head to form a cycle
        tail.next = self.head
        
        # Find the new tail: (length - k % length - 1)th node
        k = k % length
        new_tail = self.head
        for _ in range(length - k - 1):
            new_tail = new_tail.next
        
        # Set the new head and break the cycle
        self.head = new_tail.next
        new_tail.next = None
    
    def to_list(self):
        result = []
        curr = self.head
        while curr:
            result.append(curr.value)
            curr = curr.next
        return result

# Example usage:
ll = LinkedList()
for val in [1, 2, 3, 4, 5]:
    ll.append(val)

ll.rotate_right(3)
print(ll.to_list())  # Expected Output: [3, 4, 5, 1, 2]
#
