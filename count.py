import os
import ast
import re
from collections import defaultdict


def parse_html_content(content):
    """Извлекает встроенные CSS и JS из HTML"""
    css_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)

    js_blocks = []
    for match in re.finditer(r'<script\b(?:\s+[^>]*)?>(.*?)</script>', content, re.DOTALL | re.IGNORECASE):
        script_tag, script_content = match.group(0), match.group(1)
        if re.search(r'type\s*=\s*["\'](?!text/javascript|application/javascript)', script_tag, re.IGNORECASE):
            continue
        if script_content.strip():
            js_blocks.append(script_content.strip())

    return {
        'css': [css.strip() for css in css_blocks if css.strip()],
        'js': js_blocks
    }


def count_metrics(content, lang):
    """Подсчитывает метрики для произвольного контента"""
    lines = content.split('\n')
    stats = {
        'lines': len(lines),
        'chars': sum(len(line) for line in lines)
    }

    if lang == 'python':
        classes = set()
        functions = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.add(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.add(node.name)
            stats.update({'classes': len(classes), 'functions': len(functions)})
        except (SyntaxError, TypeError):
            stats.update({'classes': 0, 'functions': 0})
    else:
        stats.update({'classes': 0, 'functions': 0})

    return stats


def analyze_file(filepath):
    """Анализирует файл и возвращает метрики"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, IOError, PermissionError):
        return None

    ext = os.path.splitext(filepath)[1].lower()
    metrics = defaultdict(lambda: defaultdict(int))

    if ext == '.py':
        res = count_metrics(content, 'python')
        metrics['python'] = res

    elif ext == '.html':
        embedded = parse_html_content(content)

        cleaned_html = re.sub(
            r'(?s)<style[^>]*>.*?</style>|<script[^>]*>.*?</script>',
            '',
            content
        )

        html_metrics = count_metrics(cleaned_html, 'html')
        metrics['html'] = html_metrics

        for css in embedded['css']:
            css_metrics = count_metrics(css, 'css')
            metrics['css']['lines'] += css_metrics['lines']
            metrics['css']['chars'] += css_metrics['chars']

        for js in embedded['js']:
            js_metrics = count_metrics(js, 'js')
            metrics['js']['lines'] += js_metrics['lines']
            metrics['js']['chars'] += js_metrics['chars']

    elif ext == '.css':
        res = count_metrics(content, 'css')
        metrics['css'] = res

    elif ext == '.js':
        res = count_metrics(content, 'js')
        metrics['js'] = res

    else:
        return None

    return {
        'path': filepath,
        'metrics': dict(metrics)
    }


def scan_project(directory):
    """Рекурсивно сканирует проект"""
    stats = defaultdict(lambda: {
        'files': 0,
        'lines': 0,
        'chars': 0,
        'classes': 0,
        'functions': 0
    })

    ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.idea', 'dist', 'build'}
    ignore_files = {'.DS_Store', 'package-lock.json', 'yarn.lock'}
    gitignore = []

    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore = [line.strip() for line in f
                         if line.strip() and not line.startswith('#')]

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs
                   if d not in ignore_dirs
                   and not any(fnmatch.fnmatch(d, p) for p in gitignore)]

        files = [f for f in files
                 if f not in ignore_files
                 and not any(fnmatch.fnmatch(f, p) for p in gitignore)]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ('.py', '.html', '.css', '.js'):
                full_path = os.path.join(root, file)
                result = analyze_file(full_path)
                if result:
                    for lang, lang_metrics in result['metrics'].items():
                        stats[lang]['files'] += 1
                        stats[lang]['lines'] += lang_metrics['lines']
                        stats[lang]['chars'] += lang_metrics['chars']
                        stats[lang]['classes'] += lang_metrics['classes']
                        stats[lang]['functions'] += lang_metrics['functions']

    return stats


def print_report(stats):
    """Выводит форматированный отчет"""
    print("\n{:=^50}".format(" Code Statistics Report "))
    headers = ["Language", "Files", "Lines", "Chars", "Classes", "Functions"]
    row_format = "| {:<8} | {:>6} | {:>8} | {:>10} | {:>7} | {:>8} |"

    print("+" + "-" * 49 + "+")
    print(row_format.format(*headers))
    print("+" + "-" * 49 + "+")

    for lang in ['python', 'html', 'css', 'js']:
        data = [
            lang.upper(),
            stats[lang]['files'],
            stats[lang]['lines'],
            stats[lang]['chars'],
            stats[lang]['classes'] or '-',
            stats[lang]['functions'] or '-'
        ]
        print(row_format.format(*data))

    print("+" + "-" * 49 + "+")
    print("{:=^50}\n".format(" End of Report "))


if __name__ == "__main__":
    import fnmatch

    project_dir = os.getcwd()
    print(f"Analyzing code in: {project_dir}")

    statistics = scan_project(project_dir)
    print_report(statistics)
