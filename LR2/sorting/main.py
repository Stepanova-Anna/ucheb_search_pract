"""
Сравнение алгоритмов сортировки: QuickSort, MergeSort, TimSort
Измеряем: время выполнения для массивов разного размера и типа
"""

import time
import random
import sys
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

# Увеличиваем лимит рекурсии для больших массивов
sys.setrecursionlimit(10**6)

def quicksort(arr, low, high):
    """Быстрая сортировка (опорный элемент — медиана трёх)"""
    if low < high:

        mid = (low + high) // 2
        if arr[low] > arr[mid]:
            arr[low], arr[mid] = arr[mid], arr[low]
        if arr[low] > arr[high]:
            arr[low], arr[high] = arr[high], arr[low]
        if arr[mid] > arr[high]:
            arr[mid], arr[high] = arr[high], arr[mid]
        arr[mid], arr[high] = arr[high], arr[mid]

        pivot = arr[high]
        i = low - 1

        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        pi = i + 1

        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)


def quicksort_wrapper(arr):
    """Обёртка для QuickSort"""
    quicksort(arr, 0, len(arr) - 1)
    return arr


def mergesort(arr):
    """Сортировка слиянием"""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])

    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])

    return result


def timsort_wrapper(arr):
    return sorted(arr)


def generate_random_array(size):
    """Случайный массив"""
    return [random.randint(0, size * 10) for _ in range(size)]


def generate_sorted_array(size):
    """Отсортированный массив (возрастание)"""
    return list(range(size))


def generate_reversed_array(size):
    """Обратно отсортированный массив (убывание)"""
    return list(range(size - 1, -1, -1))


def generate_nearly_sorted_array(size, swaps=0.02):
    """Почти отсортированный массив (с небольшими перестановками)"""
    arr = list(range(size))
    num_swaps = int(size * swaps)
    for _ in range(num_swaps):
        i, j = random.randint(0, size - 1), random.randint(0, size - 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def measure_time(sort_func, arr):
    """Измерение времени выполнения сортировки"""
    arr_copy = arr.copy()
    start = time.perf_counter()
    sort_func(arr_copy)
    elapsed = time.perf_counter() - start
    return elapsed


def run_experiment():
    """Запуск полного эксперимента"""

    sizes = [1000, 5000, 10000, 50000, 100000]

    # Типы данных
    data_types = {
        'Случайные': generate_random_array,
        'Отсортированные': generate_sorted_array,
        'Обратные': generate_reversed_array,
        'Почти отсортированные': lambda s: generate_nearly_sorted_array(s, 0.02)
    }

    # Алгоритмы
    algorithms = {
        'QuickSort': quicksort_wrapper,
        'MergeSort': mergesort,
        'TimSort': timsort_wrapper
    }


    results = {algo: {dtype: [] for dtype in data_types} for algo in algorithms}

    print("ЭКСПЕРИМЕНТ: Сравнение алгоритмов сортировки")

    for size in sizes:
        print(f"\n Тестирование размера: {size:,} элементов")

        for dtype_name, gen_func in data_types.items():
            print(f"  • {dtype_name}...", end=" ", flush=True)

            # Генерация данных
            data = gen_func(size)

            for algo_name, algo_func in algorithms.items():

                times = []
                for _ in range(3):
                    elapsed = measure_time(algo_func, data)
                    times.append(elapsed)
                best_time = min(times)
                results[algo_name][dtype_name].append(best_time)

            print("✓")

    return results, sizes, data_types, algorithms


def visualize_results(results, sizes, data_types, algorithms):
    """Построение графиков и таблиц"""

    print("ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ (размер массива: 100,000 элементов)")

    target_size_idx = 4
    table_data = []
    for algo_name in algorithms:
        row = [algo_name]
        for dtype_name in data_types:
            time_ms = results[algo_name][dtype_name][target_size_idx] * 1000
            row.append(f"{time_ms:.1f} мс")
        table_data.append(row)

    print(tabulate(table_data,
                   headers=["Алгоритм"] + list(data_types.keys()),
                   tablefmt="grid"))


    print("УСКОРЕНИЕ TimSort ОТНОСИТЕЛЬНО ДРУГИХ АЛГОРИТМОВ (размер 100,000)")

    speedup_data = []
    for dtype_name in data_types:
        timsort_time = results['TimSort'][dtype_name][target_size_idx]
        quicksort_time = results['QuickSort'][dtype_name][target_size_idx]
        mergesort_time = results['MergeSort'][dtype_name][target_size_idx]

        speedup_data.append([
            dtype_name,
            f"{quicksort_time / timsort_time:.1f}x",
            f"{mergesort_time / timsort_time:.1f}x"
        ])

    print(tabulate(speedup_data,
                   headers=["Тип данных", "QuickSort быстрее?", "MergeSort быстрее?"],
                   tablefmt="grid"))

    # Построение графиков
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    colors = {'QuickSort': '#1f77b4', 'MergeSort': '#ff7f0e', 'TimSort': '#2ca02c'}

    # График 1: Случайные данные
    ax1 = axes[0, 0]
    for algo_name in algorithms:
        times = [t * 1000 for t in results[algo_name]['Случайные']]
        ax1.plot(sizes, times, 'o-', label=algo_name, color=colors[algo_name], linewidth=2, markersize=8)
    ax1.set_xlabel('Размер массива (элементов)')
    ax1.set_ylabel('Время (мс)')
    ax1.set_title('Сравнение на случайных данных')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')

    # График 2: Отсортированные данные
    ax2 = axes[0, 1]
    for algo_name in algorithms:
        times = [t * 1000 for t in results[algo_name]['Отсортированные']]
        ax2.plot(sizes, times, 'o-', label=algo_name, color=colors[algo_name], linewidth=2, markersize=8)
    ax2.set_xlabel('Размер массива (элементов)')
    ax2.set_ylabel('Время (мс)')
    ax2.set_title('Сравнение на отсортированных данных')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    ax2.set_yscale('log')

    # График 3: Обратные данные
    ax3 = axes[1, 0]
    for algo_name in algorithms:
        times = [t * 1000 for t in results[algo_name]['Обратные']]
        ax3.plot(sizes, times, 'o-', label=algo_name, color=colors[algo_name], linewidth=2, markersize=8)
    ax3.set_xlabel('Размер массива (элементов)')
    ax3.set_ylabel('Время (мс)')
    ax3.set_title('Сравнение на обратно отсортированных данных')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    ax3.set_yscale('log')

    # График 4: Почти отсортированные данные
    ax4 = axes[1, 1]
    for algo_name in algorithms:
        times = [t * 1000 for t in results[algo_name]['Почти отсортированные']]
        ax4.plot(sizes, times, 'o-', label=algo_name, color=colors[algo_name], linewidth=2, markersize=8)
    ax4.set_xlabel('Размер массива (элементов)')
    ax4.set_ylabel('Время (мс)')
    ax4.set_title('Сравнение на почти отсортированных данных')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xscale('log')
    ax4.set_yscale('log')

    plt.tight_layout()
    plt.savefig('sorting_comparison.png', dpi=150)
    plt.show()

    print("\n Графики сохранены в 'sorting_comparison.png'")


def print_analysis(results, sizes):
    """Вывод аналитических выводов"""

    print("АНАЛИЗ РЕЗУЛЬТАТОВ")

    # Сравнение при максимальном размере
    max_size_idx = -1
    max_size = sizes[max_size_idx]

    print(f"\n Результаты при размере массива {max_size:,} элементов (случайные данные):")

    time_comparison = []
    for algo_name in results:
        time_sec = results[algo_name]['Случайные'][max_size_idx]
        time_ms = time_sec * 1000
        time_comparison.append((algo_name, time_ms))
        print(f"  • {algo_name}: {time_ms:.1f} мс")


    fastest = min(time_comparison, key=lambda x: x[1])
    slowest = max(time_comparison, key=lambda x: x[1])

    print(f"\n Самый быстрый алгоритм на случайных данных: {fastest[0]} ({fastest[1]:.1f} мс)")
    print(f" Самый медленный: {slowest[0]} ({slowest[1]:.1f} мс)")
    print(f" TimSort быстрее QuickSort в {time_comparison[0][1] / time_comparison[2][1]:.1f} раза")
    print(f" TimSort быстрее MergeSort в {time_comparison[1][1] / time_comparison[2][1]:.1f} раза")


def main():

    print("СРАВНЕНИЕ АЛГОРИТМОВ СОРТИРОВКИ ДЛЯ БОЛЬШИХ МАССИВОВ ДАННЫХ")

    results, sizes, data_types, algorithms = run_experiment()

    visualize_results(results, sizes, data_types, algorithms)

    print_analysis(results, sizes)

    print("ЭКСПЕРИМЕНТ ЗАВЕРШЁН")

if __name__ == "__main__":
    main()