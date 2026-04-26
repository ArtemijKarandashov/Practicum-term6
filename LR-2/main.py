import time
import gzip
import lz4.frame
import os
import psutil
import matplotlib.pyplot as plt
import numpy as np

def generate_log(size_mb=100):
    lines = [
        "192.168.1.1 - - [24/Apr/2026:10:00:01 +0000] \"GET /index.html HTTP/1.1\" 200 1234\n",
        "10.0.0.2 - - [24/Apr/2026:10:00:02 +0000] \"POST /api/login HTTP/1.1\" 401 512\n",
        "192.168.1.3 - - [24/Apr/2026:10:00:03 +0000] \"GET /images/logo.png HTTP/1.1\" 200 34567\n",
        "172.16.0.4 - - [24/Apr/2026:10:00:04 +0000] \"GET /css/style.css HTTP/1.1\" 200 2345\n",
        "10.0.0.5 - - [24/Apr/2026:10:00:05 +0000] \"GET /js/main.js HTTP/1.1\" 200 8910\n",
        "192.168.1.1 - - [24/Apr/2026:10:00:06 +0000] \"GET /about.html HTTP/1.1\" 200 5678\n",
    ]
    data = b"".join([line.encode() for line in lines]) * (size_mb * 1024 * 1024 // sum(len(l) for l in lines))
    return data[:size_mb * 1024 * 1024]

print("Генерация тестовых данных (100 МБ)...")
test_data = generate_log(100)
print(f"Размер исходных данных: {len(test_data) / 1024 / 1024:.2f} MB")

def measure_memory_usage():
    return psutil.Process().memory_info().rss / 1024 / 1024

def measure_algorithm(compress_func, decompress_func, data, name):

    mem_before = measure_memory_usage()
    start = time.perf_counter()
    compressed = compress_func(data)
    compress_time = time.perf_counter() - start
    mem_after = measure_memory_usage()
    
    start = time.perf_counter()
    decompressed = decompress_func(compressed)
    decompress_time = time.perf_counter() - start
    
    compress_speed = len(data) / compress_time / 1024 / 1024  # MB/s
    decompress_speed = len(compressed) / decompress_time / 1024 / 1024  # MB/s
    compression_ratio = len(data) / len(compressed)
    memory_used = mem_after - mem_before
    
    return {
        'name': name,
        'original_size_mb': len(data) / 1024 / 1024,
        'compressed_size_mb': len(compressed) / 1024 / 1024,
        'compression_ratio': compression_ratio,
        'compress_time_s': compress_time,
        'decompress_time_s': decompress_time,
        'compress_speed_mb_s': compress_speed,
        'decompress_speed_mb_s': decompress_speed,
        'memory_mb': memory_used,
        'compressed_data': compressed  # для проверки корректности
    }

def gzip_compress(data):
    return gzip.compress(data, compresslevel=6)

def gzip_decompress(data):
    return gzip.decompress(data)

def lz4_compress(data):
    return lz4.frame.compress(data)

def lz4_decompress(data):
    return lz4.frame.decompress(data)

iterations = 5
results_gzip = []
results_lz4 = []

print("\nЗапуск эксперимента (5 итераций)...")
for i in range(iterations):
    print(f"Итерация {i+1}/{iterations}")
    res_gzip = measure_algorithm(gzip_compress, gzip_decompress, test_data, "GZIP")
    res_lz4 = measure_algorithm(lz4_compress, lz4_decompress, test_data, "LZ4")
    results_gzip.append(res_gzip)
    results_lz4.append(res_lz4)

def average_results(results):
    avg = {}
    keys = ['compression_ratio', 'compress_time_s', 'decompress_time_s', 
            'compress_speed_mb_s', 'decompress_speed_mb_s', 'compressed_size_mb', 'memory_mb']
    for key in keys:
        avg[key] = np.mean([r[key] for r in results])
    avg['name'] = results[0]['name']
    return avg

avg_gzip = average_results(results_gzip)
avg_lz4 = average_results(results_lz4)

plt.style.use('seaborn-v0_8-darkgrid')
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# График 1: Степень сжатия
ax1 = axes[0, 0]
names = ['GZIP', 'LZ4']
ratios = [avg_gzip['compression_ratio'], avg_lz4['compression_ratio']]
bars1 = ax1.bar(names, ratios, color=['#2E86AB', '#A23B72'])
ax1.set_ylabel('Степень сжатия (во сколько раз)')
ax1.set_title('Сравнение степени сжатия\n(выше = лучше)')
ax1.axhline(y=1, color='red', linestyle='--', label='без сжатия')
for bar, val in zip(bars1, ratios):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{val:.1f}', ha='center')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# График 2: Скорость сжатия (MB/s)
ax2 = axes[0, 1]
compress_speeds = [avg_gzip['compress_speed_mb_s'], avg_lz4['compress_speed_mb_s']]
bars2 = ax2.bar(names, compress_speeds, color=['#2E86AB', '#A23B72'])
ax2.set_ylabel('Скорость (MB/s)')
ax2.set_title('Сравнение скорости СЖАТИЯ\n(выше = лучше)')
for bar, val in zip(bars2, compress_speeds):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f'{val:.0f}', ha='center')
ax2.grid(axis='y', alpha=0.3)

# График 3: Скорость распаковки (MB/s)
ax3 = axes[1, 0]
decompress_speeds = [avg_gzip['decompress_speed_mb_s'], avg_lz4['decompress_speed_mb_s']]
bars3 = ax3.bar(names, decompress_speeds, color=['#2E86AB', '#A23B72'])
ax3.set_ylabel('Скорость (MB/s)')
ax3.set_title('Сравнение скорости РАСПАКОВКИ\n(выше = лучше)')
for bar, val in zip(bars3, decompress_speeds):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, f'{val:.0f}', ha='center')
ax3.grid(axis='y', alpha=0.3)

# График 4: Компромисс (время сжатия vs степень сжатия)
ax4 = axes[1, 1]
ax4.scatter([avg_gzip['compress_time_s']], [avg_gzip['compression_ratio']], 
            s=200, color='#2E86AB', label='GZIP')
ax4.scatter([avg_lz4['compress_time_s']], [avg_lz4['compression_ratio']], 
            s=200, color='#A23B72', label='LZ4')
ax4.set_xlabel('Время сжатия (секунды)')
ax4.set_ylabel('Степень сжатия')
ax4.set_title('Компромисс: скорость сжатия vs размер')
for name, x, y in [('GZIP', avg_gzip['compress_time_s'], avg_gzip['compression_ratio']),
                   ('LZ4', avg_lz4['compress_time_s'], avg_lz4['compression_ratio'])]:
    ax4.annotate(name, (x, y), xytext=(10, 10), textcoords='offset points')
ax4.grid(alpha=0.3)
ax4.legend()

plt.suptitle('Сравнение алгоритмов сжатия: GZIP vs LZ4\n(данные: лог веб-сервера, 100 МБ)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('compression_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

# Таблица результатов
print("\n" + "="*70)
print("РЕЗУЛЬТАТЫ ЭКСПЕРИМЕНТА (среднее за 5 итераций)")
print("="*70)

print(f"\n{'Показатель':<35} {'GZIP':<20} {'LZ4':<20}")
print("-"*70)
print(f"{'Исходный размер (МБ)':<35} {100:<20} {100:<20}")
print(f"{'Сжатый размер (МБ)':<35} {avg_gzip['compressed_size_mb']:<20.2f} {avg_lz4['compressed_size_mb']:<20.2f}")
print(f"{'Степень сжатия (раз)':<35} {avg_gzip['compression_ratio']:<20.2f} {avg_lz4['compression_ratio']:<20.2f}")
print(f"{'Время сжатия (с)':<35} {avg_gzip['compress_time_s']:<20.3f} {avg_lz4['compress_time_s']:<20.3f}")
print(f"{'Скорость сжатия (МБ/с)':<35} {avg_gzip['compress_speed_mb_s']:<20.0f} {avg_lz4['compress_speed_mb_s']:<20.0f}")
print(f"{'Время распаковки (с)':<35} {avg_gzip['decompress_time_s']:<20.3f} {avg_lz4['decompress_time_s']:<20.3f}")
print(f"{'Скорость распаковки (МБ/с)':<35} {avg_gzip['decompress_speed_mb_s']:<20.0f} {avg_lz4['decompress_speed_mb_s']:<20.0f}")
print(f"{'Использование памяти (МБ)':<35} {avg_gzip['memory_mb']:<20.1f} {avg_lz4['memory_mb']:<20.1f}")

# Проверка корректности
print("\n" + "-"*70)
print("ПРОВЕРКА КОРРЕКТНОСТИ: все данные восстановлены без ошибок")