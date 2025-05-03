import os
import ast


def count_code_metrics(filepath):
    """Анализирует файл и возвращает метрики кода"""
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            content = f.read()
        except UnicodeDecodeError:
            return None

    lines = content.split('\n')
    total_lines = len(lines)
    total_chars = sum(len(line) for line in lines)

    classes = set()
    functions = set()

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.add(node.name)
    except SyntaxError:
        pass

    return {
        'path': filepath,
        'lines': total_lines,
        'chars': total_chars,
        'classes': len(classes),
        'functions': len(functions)
    }


def scan_directory(directory):
    """Рекурсивно сканирует директорию для .py файлов"""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                metrics = count_code_metrics(full_path)
                if metrics:
                    results.append(metrics)
    return results


def print_statistics(results):
    """Выводит сводную статистику"""
    total_files = len(results)
    total_lines = sum(f['lines'] for f in results)
    total_chars = sum(f['chars'] for f in results)
    total_classes = sum(f['classes'] for f in results)
    total_functions = sum(f['functions'] for f in results)

    print(f"\n{' Статистика анализа ':━^50}")
    print(f"▪ Всего файлов: {total_files}")
    print(f"▪ Всего строк: {total_lines}")
    print(f"▪ Всего символов: {total_chars}")
    print(f"▪ Всего классов: {total_classes}")
    print(f"▪ Всего функций: {total_functions}")
    print("━" * 50)


if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"Сканирую Python-файлы в: {current_dir}")

    analysis_results = scan_directory(current_dir)

    if analysis_results:
        print_statistics(analysis_results)
    else:
        print("Не найдено ни одного .py файла")
