Site Parser
Парсер для сбора контактной информации (email-адресов и телефонных номеров) с веб-сайтов.

Особенности
Рекурсивный обход внутренних страниц сайта

Извлечение email и телефонов из текста и ссылок

Настраиваемое ограничение количества страниц

Фильтрация некорректных данных

Подробное логирование процесса

Установка
bash
# Клонирование репозитория
git clone <repository-url>
cd site-parser

# Установка зависимостей
pip install requests beautifulsoup4
Использование
Быстрый запуск
python
from site_parser import parse_site

result = parse_site("https://example.com")
print(f"Emails: {result['emails']}")
print(f"Phones: {result['phones']}")
Расширенное использование
python
from site_parser import SiteParser

parser = SiteParser(
    start_url="https://example.com",
    max_pages=100,    # максимум 100 страниц
    timeout=15        # таймаут 15 секунд
)

result = parser.run()
Командная строка
bash
python site_parser.py
Параметры класса SiteParser
Параметр	Тип	По умолчанию	Описание
start_url	str	-	Начальный URL для парсинга
max_pages	int	50	Максимальное количество страниц
timeout	int	10	Таймаут HTTP-запросов в секундах
Возвращаемые данные
json
{
  "url": "https://example.com",
  "emails": ["contact@example.com", "info@example.com"],
  "phones": ["+7 (999) 123-45-67", "8-800-123-45-67"]
}
Ограничения
Обрабатывает только внутренние ссылки домена

Только HTML-страницы (пропускает PDF, изображения и др.)

Максимум 50 страниц по умолчанию

Поддерживает основные форматы телефонов

Требования
Python 3.7+

requests >= 2.25.0

beautifulsoup4 >= 4.9.0

Пример вывода
bash
INFO: Processing: https://example.com
INFO: Processing: https://example.com/about
INFO: Processing: https://example.com/contact
{
  "url": "https://example.com",
  "emails": ["info@example.com"],
  "phones": ["+7 (495) 123-45-67"]
}
