# table_edit_sql
Редактирование в tableWidget и обновление данных в БД с помощью SQL-запроса

Небольшое оконное приложение, в котором реализовано обращение к базе данных с использованием SQL-запросов для демонстрации прямого редактирования данных в виджете таблицы


Использованы две вида обращения к БД:

1) Запрос в БД для редактирования:
    * позволяет изменить любую ячейку, изменения в ячейке сохраняются автоматически после изменения фокуса курсора на другую ячейку;
    * в этом же запросе реализовано разбиение колонки DateTime на две колонки, на Дата и Время;
    * во время запроса колонка DateTyme разделяется на две части и выводится в поле tableWidget;
    * при сохранении данных колонки Дата и Время снова обединяются в одну колонку DateTime.

2) Запрос в БД для чтения:
    * чтени данных с БД осуществляется без какого либо изменения и сразу выводится в tableWidget;
    * поле tableWidget болкируется для редактировани.
    
  