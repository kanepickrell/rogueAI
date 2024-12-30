if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())

    arr = list(arr)
    
    print(arr)
    score_list = []
    
    arr.sort(reverse=True)
    print(f"Sorted Scores: {arr}")
    
    print(arr[1])