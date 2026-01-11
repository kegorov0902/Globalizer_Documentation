import os
import re

def process_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Извлекаем название из title (если есть Globalizer:)
    title_match = re.search(r'<title>(?:Globalizer: )?(.*?)</title>', content)
    page_title = title_match.group(1) if title_match else "Страница"
    
    # Проверяем, является ли это страницей класса (чтобы сохранить оригинальное поведение для классов)
    is_class_page = filepath.startswith('class_') and 'Globalizer:' in content
    
    # Извлекаем основное содержимое
    header_start = content.find('<div class="header">')
    contents_end = content.find('</div><!-- contents -->')
    
    # Если не нашли стандартную разметку Doxygen, пытаемся найти альтернативные варианты
    if header_start == -1:
        header_start = content.find('<div class="PageDoc"><div class="header">')
    
    if contents_end == -1:
        contents_end = content.find('</div><!-- PageDoc -->')
    
    if header_start != -1 and contents_end != -1:
        # Увеличиваем contents_end, чтобы включить закрывающий тег
        contents_end += len('</div><!-- contents -->')
        main_content = content[header_start:contents_end]
        
        # Формируем заголовок для тега title
        title_prefix = "Globalizer: " if is_class_page else ""
        
        # Создаем новый HTML
        template = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"/>
    <title>''' + title_prefix + page_title + '''</title>
    <style type="text/css">
        <!-- ВСТАВИТЬ СТИЛИ ИЗ ШАБЛОНА -->
    </style>
</head>
<body>
''' + main_content + '''
<div class="footer">
    <small>Создано системой Doxygen 1.14.0</small>
</div>
</body>
</html>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"Обработан: {filepath}")
        return True
    else:
        print(f"Не удалось найти основное содержимое в: {filepath}")
        return False

# Обработка всех HTML файлов
processed_count = 0
for filename in os.listdir('.'):
    if filename.endswith('.html'):
        if process_html_file(filename):
            processed_count += 1

print(f"\nОбработка завершена. Обработано файлов: {processed_count}")