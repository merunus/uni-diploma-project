from plantuml import PlantUML

# Визначення UML-діаграми послідовності взаємодії клієнта, серверної частини та бази даних
uml_code = """
@startuml
participant "Клієнт (Користувач)" as Client
participant "Веб-інтерфейс (Frontend)" as Frontend
participant "Сервер (FastAPI)" as Server
participant "База даних (SQLite)" as Database

Client -> Frontend: Вхід у систему / реєстрація
Frontend -> Server: Надсилає дані користувача (логін, пароль)
Server -> Database: Перевіряє користувача у базі даних
Database --> Server: Повертає інформацію про користувача
Server --> Frontend: Відповідь про успішний вхід

Client -> Frontend: Вибір рівня складності слів
Frontend -> Server: Запит слів для вибраного рівня складності
Server -> Database: Отримує список слів
Database --> Server: Повертає список слів
Server --> Frontend: Відправляє список слів
Frontend --> Client: Відображає картки слів

Client -> Frontend: Позначає слово як вивчене
Frontend -> Server: Надсилає оновлення прогресу
Server -> Database: Оновлює статус вивченого слова
Database --> Server: Підтверджує оновлення
Server --> Frontend: Повідомляє про успішне збереження

Client -> Frontend: Перегляд прогресу
Frontend -> Server: Запит на отримання прогресу
Server -> Database: Отримання прогресу користувача
Database --> Server: Повертає дані про прогрес
Server --> Frontend: Відправляє прогрес
Frontend --> Client: Відображає прогрес користувача
@enduml
"""

# Генерація діаграми
plantuml = PlantUML(url="http://www.plantuml.com/plantuml/png/")
image_url = plantuml.processes(uml_code)
image_url
