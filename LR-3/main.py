"""
Пилотный эксперимент: сравнение гибридного сжатия без потерь с PNG
Автор: (Ваше имя)
Лабораторная работа №3
"""

import numpy as np
from PIL import Image
import time
import memory_profiler
import zlib
import struct


def rle_encode(data):
    """RLE сжатие для байтового массива"""
    encoded = []
    i = 0
    while i < len(data):
        run_length = 1
        while i + run_length < len(data) and data[i] == data[i + run_length] and run_length < 255:
            run_length += 1
        encoded.append((data[i], run_length))
        i += run_length
    return encoded


def hybrid_compress(image_path, mode='fast'):
    """
    Гибридное сжатие: RLE + LZ77 (через zlib)
    mode: 'fast' - уровень сжатия 1, 'dense' - уровень 9
    """
    # Загружаем изображение
    img = Image.open(image_path)
    original_bytes = np.array(img).tobytes()
    
    # Применяем RLE как предварительный этап
    rle_encoded = rle_encode(original_bytes)
    
    # Превращаем RLE в байтовый поток
    rle_bytes = bytearray()
    for value, count in rle_encoded:
        rle_bytes.extend([value, count])
    
    # LZ77 + энтропийное (через zlib)
    if mode == 'fast':
        compressed = zlib.compress(bytes(rle_bytes), level=1)
    else:  # dense
        compressed = zlib.compress(bytes(rle_bytes), level=9)
    
    # Сохраняем метаданные: исходный размер (для проверки)
    meta = struct.pack('I', len(original_bytes))
    
    return meta + compressed


def hybrid_decompress(compressed_data):
    """Полное восстановление изображения"""
    # Извлекаем метаданные
    original_size = struct.unpack('I', compressed_data[:4])[0]
    compressed_body = compressed_data[4:]
    
    # Распаковка LZ77
    rle_bytes = zlib.decompress(compressed_body)
    
    # Распаковка RLE
    decompressed = bytearray()
    for i in range(0, len(rle_bytes), 2):
        value = rle_bytes[i]
        count = rle_bytes[i + 1]
        decompressed.extend([value] * count)
    
    # Проверка размера
    if len(decompressed) != original_size:
        raise ValueError(f"Размер не совпадает: {len(decompressed)} vs {original_size}")
    
    return bytes(decompressed)


def image_from_bytes(data, original_shape):
    """Восстановить PIL Image из байтов"""
    arr = np.frombuffer(data, dtype=np.uint8).reshape(original_shape)
    return Image.fromarray(arr)


def test_correctness(original_image_path):
    """Попиксельная проверка восстановления"""
    # Оригинал
    original = Image.open(original_image_path)
    original_array = np.array(original)
    original_shape = original_array.shape
    
    # Сжатие и распаковка
    compressed = hybrid_compress(original_image_path, mode='fast')
    decompressed_bytes = hybrid_decompress(compressed)
    decompressed_array = np.frombuffer(decompressed_bytes, dtype=np.uint8).reshape(original_shape)
    
    # Сравнение
    if np.array_equal(original_array, decompressed_array):
        print("Корректность: восстановление ПОЛНОЕ (попиксельно)")
        return True
    else:
        diff = np.sum(original_array != decompressed_array)
        print(f"Ошибка: {diff} пикселей не совпадают")
        return False
    

@memory_profiler.profile
def measure_performance(image_path):
    """Измеряем время, память, степень сжатия"""
    
    original = Image.open(image_path)
    original_size = len(np.array(original).tobytes())
    original_time = time.time()
    time.sleep(0.01)  # имитация
    original_time = time.time() - original_time  # просто для формата
    
    # PNG (референс)
    png_buffer = io.BytesIO()
    original.save(png_buffer, format='PNG', compress_level=6)
    png_size = len(png_buffer.getvalue())
    
    start_time = time.time()
    compressed_fast = hybrid_compress(image_path, mode='fast')
    fast_time = (time.time() - start_time) * 1000  # в мс
    
    start_time = time.time()
    compressed_dense = hybrid_compress(image_path, mode='dense')
    dense_time = (time.time() - start_time) * 1000
    
    # Время распаковки
    start_time = time.time()
    hybrid_decompress(compressed_fast)
    decompress_fast_time = (time.time() - start_time) * 1000
    
    start_time = time.time()
    hybrid_decompress(compressed_dense)
    decompress_dense_time = (time.time() - start_time) * 1000
    
    # Коэффициенты сжатия
    fast_ratio = original_size / len(compressed_fast)
    dense_ratio = original_size / len(compressed_dense)
    png_ratio = original_size / png_size
    
    return {
        'original_size_kb': original_size / 1024,
        'png_size_kb': png_size / 1024,
        'fast_size_kb': len(compressed_fast) / 1024,
        'dense_size_kb': len(compressed_dense) / 1024,
        'fast_ratio': fast_ratio,
        'dense_ratio': dense_ratio,
        'png_ratio': png_ratio,
        'fast_compress_ms': fast_time,
        'dense_compress_ms': dense_time,
        'fast_decompress_ms': decompress_fast_time,
        'dense_decompress_ms': decompress_dense_time
    }

if __name__ == "__main__":
    import io  # для PNG буфера
    
    print("="*60)
    print("ПИЛОТНЫЙ ЭКСПЕРИМЕНТ: Гибридное сжатие без потерь")
    print("="*60)
    
    # Используйте свой тестовый файл
    test_image = "screenshot.png"
    
    try:
        # Шаг 1: Проверка корректности
        print("\n[1] Проверка корректности...")
        if test_correctness(test_image):
            print("   Результат: АЛГОРИТМ КОРРЕКТЕН")
        else:
            print("   Результат: ОШИБКА ВОССТАНОВЛЕНИЯ")
            exit(1)
        
        # Шаг 2: Замер производительности
        print("\n[2] Измерение эффективности...")
        perf = measure_performance(test_image)
        
        # Шаг 3: Вывод результатов
        print("\n[3] РЕЗУЛЬТАТЫ:")
        print("-"*60)
        print(f"{'Параметр':<25} {'PNG':<12} {'Гибрид (fast)':<15} {'Гибрид (dense)'}")
        print("-"*60)
        print(f"{'Размер (КБ):':<25} {perf['png_size_kb']:<12.1f} {perf['fast_size_kb']:<15.1f} {perf['dense_size_kb']:.1f}")
        print(f"{'Коэф. сжатия:':<25} {perf['png_ratio']:<12.2f} {perf['fast_ratio']:<15.2f} {perf['dense_ratio']:.2f}")
        print(f"{'Сжатие (мс):':<25} {'-':<12} {perf['fast_compress_ms']:<15.1f} {perf['dense_compress_ms']:.1f}")
        print(f"{'Распаковка (мс):':<25} {'-':<12} {perf['fast_decompress_ms']:<15.1f} {perf['dense_decompress_ms']:.1f}")
        print("-"*60)
        
        # Выигрыш
        gain_fast = (perf['png_ratio'] / perf['fast_ratio'] - 1) * 100
        gain_dense = (perf['png_ratio'] / perf['dense_ratio'] - 1) * 100
        
        print(f"\nВыигрыш по сжатию:")
        print(f"   Быстрый режим: {gain_fast:.1f}%")
        print(f"   Плотный режим: {gain_dense:.1f}%")
        
        # Проверка гипотезы
        if gain_dense >= 5:
            print("\nГИПОТЕЗА H1 ПРИНЯТА: выигрыш ≥5% на тестовом изображении")
        else:
            print("\nГИПОТЕЗА H1 ОТКЛОНЕНА: выигрыш менее 5%")
            
    except FileNotFoundError:
        print(f"Ошибка: Файл {test_image} не найден.")
        print("Создайте тестовое изображение или укажите правильный путь.")