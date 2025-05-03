import os
import ast
import re
import fnmatch
from collections import defaultdict


class HTMLExtractor:
    @staticmethod
    def extract(content):
        """Извлекает встроенные CSS и JS из HTML"""
        css_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)
        js_blocks = []
        for match in re.finditer(r'<script\b(?:\s+[^>]*)?>(.*?)</script>', content, re.DOTALL | re.IGNORECASE):
            tag, script = match.group(0), match.group(1)
            if re.search(r'type\s*=\s*["\'](?!text/javascript|application/javascript)', tag, re.IGNORECASE):
                continue
            if script.strip():
                js_blocks.append(script.strip())
        return {
            'css': [c.strip() for c in css_blocks if c.strip()],
            'js': js_blocks
        }


class MetricsCounter:
    @staticmethod
    def count(content, lang):
        """Подсчитывает метрики для произвольного контента"""
        lines = content.splitlines()
        stats = {
            'lines': len(lines),
            'chars': sum(len(line) for line in lines)
        }
        if lang == 'python':
            stats.update(MetricsCounter._count_py(content))
        else:
            stats.update({'classes': 0, 'functions': 0})
        return stats

    @staticmethod
    def _count_py(content):
        classes = set()
        functions = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.add(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.add(node.name)
        except (SyntaxError, TypeError):
            return {'classes': 0, 'functions': 0}
        return {'classes': len(classes), 'functions': len(functions)}


class FileAnalyzer:
    """Анализирует одиночный файл и собирает метрики"""

    def __init__(self, path):
        self.path = path
        self.ext = os.path.splitext(path)[1].lower()

    def analyze(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, IOError, PermissionError):
            return None

        metrics = defaultdict(lambda: defaultdict(int))
        if self.ext == '.py':
            metrics['python'] = MetricsCounter.count(content, 'python')
        elif self.ext == '.html':
            embedded = HTMLExtractor.extract(content)
            cleaned = re.sub(
                r'(?s)<style[^>]*>.*?</style>|<script[^>]*>.*?</script>',
                '', content
            )
            metrics['html'] = MetricsCounter.count(cleaned, 'html')
            for css in embedded['css']:
                m = MetricsCounter.count(css, 'css')
                metrics['css']['lines'] += m['lines']
                metrics['css']['chars'] += m['chars']
            for js in embedded['js']:
                m = MetricsCounter.count(js, 'js')
                metrics['js']['lines'] += m['lines']
                metrics['js']['chars'] += m['chars']
        elif self.ext in ('.css', '.js'):
            lang = self.ext.lstrip('.')
            metrics[lang] = MetricsCounter.count(content, lang)
        else:
            return None

        return {'path': self.path, 'metrics': dict(metrics)}


class ProjectScanner:
    """Рекурсивно сканирует проект и агрегирует метрики"""

    def __init__(self, directory):
        self.directory = directory
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.idea', 'dist', 'build'}
        self.ignore_files = {'.DS_Store', 'package-lock.json', 'yarn.lock'}
        self.gitignore = self._load_gitignore()

    def _load_gitignore(self):
        path = os.path.join(self.directory, '.gitignore')
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            return [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]

    def scan(self):
        stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'chars': 0, 'classes': 0, 'functions': 0})
        for root, dirs, files in os.walk(self.directory):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs
                       and not any(fnmatch.fnmatch(d, p) for p in self.gitignore)]
            files = [f for f in files if f not in self.ignore_files
                     and not any(fnmatch.fnmatch(f, p) for p in self.gitignore)]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.py', '.html', '.css', '.js'):
                    result = FileAnalyzer(os.path.join(root, f)).analyze()
                    if result:
                        for lang, m in result['metrics'].items():
                            s = stats[lang]
                            s['files'] += 1
                            s['lines'] += m.get('lines', 0)
                            s['chars'] += m.get('chars', 0)
                            s['classes'] += m.get('classes', 0)
                            s['functions'] += m.get('functions', 0)
        return stats


class ReportPrinter:
    """Выводит форматированный отчет"""

    @staticmethod
    def print(stats):
        print("\n{:=^50}".format(" Code Statistics Report "))
        headers = ["Language", "Files", "Lines", "Chars", "Classes", "Functions"]
        row = "| {:<8} | {:>6} | {:>8} | {:>10} | {:>7} | {:>8} |"

        print("+" + "-" * 49 + "+")
        print(row.format(*headers))
        print("+" + "-" * 49 + "+")

        for lang in ['python', 'html', 'css', 'js']:
            d = stats.get(lang, {})
            print(row.format(
                lang.upper(),
                d.get('files', 0),
                d.get('lines', 0),
                d.get('chars', 0),
                d.get('classes') or '-',
                d.get('functions') or '-'
            ))
        print("+" + "-" * 49 + "+")
        print("{:=^50}\n".format(" End of Report "))


if __name__ == "__main__":
    project_dir = os.getcwd()
    print(f"Analyzing code in: {project_dir}")
    stats = ProjectScanner(project_dir).scan()
    ReportPrinter.print(stats)
