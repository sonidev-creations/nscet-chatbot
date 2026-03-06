import math
import random


def generate_data(n):
    data = []
    for _ in range(n):
        row = [random.randint(0, 1000) for _ in range(50)]
        data.append(row)
    return data


def calculate_stats(data):
    stats = []
    for row in data:
        stats.append({
            "mean": sum(row)/len(row),
            "max": max(row),
            "min": min(row),
            "std_dev": math.sqrt(sum((x - sum(row)/len(row))**2 for x in row)/len(row))
        })
    return stats


def fibonacci(n):
    a, b = 0, 1
    seq = []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq

def factorials(n):
    return [math.factorial(i) for i in range(1, n+1)]

if __name__ == "__main__":
    data = generate_data(1000)
    stats = calculate_stats(data)
    fib = fibonacci(1000)
    facts = factorials(100)
    
    print("Data stats sample:", stats[:5])
    print("Fibonacci sample:", fib[:10])
    print("Factorials sample:", facts[:10])