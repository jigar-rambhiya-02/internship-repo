class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        if not 3 <= len(nums) <= 3000:
            return [[]]
        
        ans = []
        
        if sum(nums) == 0 and len(nums) == 3:
            ans.append(nums)
        
        # case to handle when there z in the list.
        # # include handling with the opposite numbers.

        # When there is no zero
        # # 
        

