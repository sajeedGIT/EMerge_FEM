def calculate_squares(n):
    result = 0

    for i in range(n):
        result += i * i

    return result


answer = calculate_squares(100)

print(answer)