def solution(n: int) -> int:
    if n < 2:
        return 1
    else:
        ans = 1
        for i in range(1, n+1):
            ans *= i
        
        return ans

if __name__ == '__main__':
    n = 5
    print(f'Factorial of {5} is {solution(n)}.')
