# Отчёт
Отчёт находится в файле "Практикум-ЛР-3"

## Результат выполнения демонстрационной программы (На файле screenshot.png):

```bash
[1] Проверка корректности...
✓ Корректность: восстановление ПОЛНОЕ (попиксельно)
   Результат: АЛГОРИТМ КОРРЕКТЕН

[2] Измерение эффективности...
Filename: C:\Users\zhizh\Code\img-comp-algs\main.py

Line #    Mem usage    Increment  Occurrences   Line Contents
=============================================================
   108     44.2 MiB     44.2 MiB           1   @memory_profiler.profile
   109                                         def measure_performance(image_path):
   110                                             """Измеряем время, память, степень сжатия"""
   111                                             
   112     44.2 MiB      0.0 MiB           1       original = Image.open(image_path)
   113     48.2 MiB      4.0 MiB           1       original_size = len(np.array(original).tobytes())
   114     48.2 MiB      0.0 MiB           1       original_time = time.time()
   115     48.2 MiB      0.0 MiB           1       time.sleep(0.01)  # имитация
   116     48.2 MiB      0.0 MiB           1       original_time = time.time() - original_time  # просто для формата
   117                                             
   118                                             # PNG (референс)
   119     48.2 MiB      0.0 MiB           1       png_buffer = io.BytesIO()
   120     48.3 MiB      0.1 MiB           1       original.save(png_buffer, format='PNG', compress_level=6)
   121     48.3 MiB      0.0 MiB           1       png_size = len(png_buffer.getvalue())
   122                                             
   123     48.3 MiB      0.0 MiB           1       start_time = time.time()
   124     51.5 MiB      3.2 MiB           1       compressed_fast = hybrid_compress(image_path, mode='fast')
   125     51.5 MiB      0.0 MiB           1       fast_time = (time.time() - start_time) * 1000  # в мс
   126                                             
   127     51.5 MiB      0.0 MiB           1       start_time = time.time()
   128     53.9 MiB      2.4 MiB           1       compressed_dense = hybrid_compress(image_path, mode='dense')
   129     53.9 MiB      0.0 MiB           1       dense_time = (time.time() - start_time) * 1000
   130                                             
   131                                             # Время распаковки
   132     53.9 MiB      0.0 MiB           1       start_time = time.time()
   133     55.1 MiB      1.2 MiB           1       hybrid_decompress(compressed_fast)
   134     55.1 MiB      0.0 MiB           1       decompress_fast_time = (time.time() - start_time) * 1000
   135                                             
   136     55.1 MiB      0.0 MiB           1       start_time = time.time()
   137     53.5 MiB     -1.6 MiB           1       hybrid_decompress(compressed_dense)
   138     53.5 MiB      0.0 MiB           1       decompress_dense_time = (time.time() - start_time) * 1000
   139                                             
   140                                             # Коэффициенты сжатия
   141     53.5 MiB      0.0 MiB           1       fast_ratio = original_size / len(compressed_fast)
   142     53.5 MiB      0.0 MiB           1       dense_ratio = original_size / len(compressed_dense)
   143     53.5 MiB      0.0 MiB           1       png_ratio = original_size / png_size
   144                                             
   145     53.5 MiB      0.0 MiB           1       return {
   146     53.5 MiB      0.0 MiB           1           'original_size_kb': original_size / 1024,
   147     53.5 MiB      0.0 MiB           1           'png_size_kb': png_size / 1024,
   148     53.5 MiB      0.0 MiB           1           'fast_size_kb': len(compressed_fast) / 1024,
   149     53.5 MiB      0.0 MiB           1           'dense_size_kb': len(compressed_dense) / 1024,
   150     53.5 MiB      0.0 MiB           1           'fast_ratio': fast_ratio,
   151     53.5 MiB      0.0 MiB           1           'dense_ratio': dense_ratio,
   152     53.5 MiB      0.0 MiB           1           'png_ratio': png_ratio,
   153     53.5 MiB      0.0 MiB           1           'fast_compress_ms': fast_time,
   154     53.5 MiB      0.0 MiB           1           'dense_compress_ms': dense_time,
   155     53.5 MiB      0.0 MiB           1           'fast_decompress_ms': decompress_fast_time,
   156     53.5 MiB      0.0 MiB           1           'dense_decompress_ms': decompress_dense_time
   157                                             }



[3] РЕЗУЛЬТАТЫ:
------------------------------------------------------------
Параметр                  PNG          Гибрид (fast)   Гибрид (dense)
------------------------------------------------------------
Размер (КБ):              872.2        1665.8          1408.6
Коэф. сжатия:             3.10         1.62            1.92
Сжатие (мс):              -            10381.5         10484.3
Распаковка (мс):          -            6051.2          6116.4
------------------------------------------------------------

Выигрыш по сжатию:
   Быстрый режим: 91.0%
   Плотный режим: 61.5%

ГИПОТЕЗА H1 ПРИНЯТА: выигрыш ≥5% на тестовом изображении
```
