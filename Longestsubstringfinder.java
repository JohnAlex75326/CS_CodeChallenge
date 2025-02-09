import java.util.HashMap;

class LongestSubstringFinder {
    public int findLongestSubstring(String s, int k) {
        if (s == null || k == 0) return 0;
        
        HashMap<Character, Integer> charCount = new HashMap<>();
        int left = 0, right = 0, maxLength = 0;
        
        while (right < s.length()) {
            char rightChar = s.charAt(right);
            charCount.put(rightChar, charCount.getOrDefault(rightChar, 0) + 1);
            right++;
            
            while (charCount.size() > k) {
                char leftChar = s.charAt(left);
                charCount.put(leftChar, charCount.get(leftChar) - 1);
                if (charCount.get(leftChar) == 0) {
                    charCount.remove(leftChar);
                }
                left++;
            }
            
            maxLength = Math.max(maxLength, right - left);
        }
        
        return maxLength;
    }

    public static void main(String[] args) {
        LongestSubstringFinder finder = new LongestSubstringFinder();
        System.out.println(finder.findLongestSubstring("abcba", 2)); // Output: 3
    }
}