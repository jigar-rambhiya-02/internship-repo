def solution(arr: list) -> int:

    a = 0
    b = 0
    dif = 0
    area = dif * min(a, b)
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if min(arr[i], arr[j]) * (j - i) > area:
                a, b = arr[i], arr[j]
                dif = j - i
                area = dif * min(a, b)
    
    return f'ans: {dif * min(a, b)}, a = {a}, b = {b})'

    #


if __name__ == '__main__':   # fixed guard
    test = [2, 1, 8, 6, 4, 6, 5, 5]
    print(solution(test))