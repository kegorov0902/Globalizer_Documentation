import os
import re

def process_class_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Извлекаем название класса из title
    title_match = re.search(r'<title>Globalizer: (.*?)</title>', content)
    class_name = title_match.group(1) if title_match else "Класс"
    
    # Извлекаем основное содержимое
    header_start = content.find('<div class="header">')
    contents_end = content.find('</div><!-- contents -->')
    
    if header_start != -1 and contents_end != -1:
        main_content = content[header_start:contents_end + len('</div><!-- contents -->')]
        
        # Создаем новый HTML
        template = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"/>
    <title>Globalizer: ''' + class_name + '''</title>
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

# Обработка всех файлов
for filename in os.listdir('.'):
    if filename.endswith('.html') and filename.startswith('class_'):
        process_class_file(filename)