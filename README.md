## Задание I

> Есть система, которая состоит из десятка сервисов с фоновым процессингом, общением через API и очереди сообщений. В общем, это некий pipeline, который на вход принимает один JSON, а на выходе отдает другой JSON. В процессе прохода по pipeline данные обогащаются, меняются и оседают в некоторых сервисах.
> Каждую задачу обработки входных данных назовем операцией. По мере прохождения данных по pipeline статус у этой операции меняется и отражает текущее состояние обработки входных данных, на каком этапе она находится в тот или иной момент времени.
> Есть сервис, который создан для отслеживания состояния той или иной операции обработки полученных на вход данных, назовем его Operation. Этот сервис хранит состояние операций в PostgreSQL. Некоторые из сервисов могут много и часто делать запросы по API и обновлять состояние операции в сервисе Operation. Фактически, у каждого набора входных данных есть запись в бд сервиса Operation, которая содержит сквозной уникальный id, статус и набор метаданных.

### Опишите:

1. С какими проблемами можно столкнуться при таком способе хранения состояния обработки входных данных?
 - append only табличка, с вечно-растущим индексом для получения/обновления значения (память/задержка)
 - single point of failure для всех сервисов, которые используют это апи как источник информации
 - жесткая связка с апи этого сервиса, т.е. при любом значительном обновлении схемы запроса на обновление(через апи/очередь) придется, так же трогать все сервисы участвующие в пайплайне.
 - гоночки ниже :)
2. Что предпринять, если происходит “гонка” обновления данных операции в Operation и часть данных может перезаписываться старыми?
 - судя по тексту - данные проходят через пайплайн, если происходит гонка, нам важнее получить последний слепок данных, т.ч.:
   - можно попробовать воспользоваться priority queue (любого рода), но тут сложно будет выбрать вес:
     - либо синхронизировать все сервисы по времени
     - либо задавать жесткий приоритет этапам etl процесса
     - либо добавлять значение, которое будет инкрементироваться на каждом этапе
 - все операции обновления производить через append, с использованием доп. значения, для отслеживания очередности, для последнующего мержа данных.
3. Как решить проблему с большим количеством UPDATE операций в PostgreSQL? И на каком уровне стоит ее решать?
 - архитектурном, выглядит так, что данный сервис нужен всего лишь для мониторинга, почему бы не обойтись простейшим sentry в данном случае ?
4. Как можно спроектировать сервис для отслеживания состояния обработки входных JSON по всему pipeline, чтобы избежать подобных проблем? Какие минусы у вашего варианта реализации такого сервиса?
 - как и в варианте 3 - https://docs.sentry.io/product/cli/send-event/, зачем делать велосипед
 - но если очень хочется, как вариант, можно использовать kafka с топиком под каждую операцию, например и слушать это все в конечном сервисе, который будет отражать актуальный статус по каждому id входных данных.


 > Мы понимаем, что выполнение тестового задания требует времени, которого всегда не хватает. Но нам хотелось бы увидеть как вы пишите код и используете предложенные для этого инструменты. Поэтому мы просим реализовать сильно упрощенный вариант.
>

## Что сделать

Предлагается реализовать очень упрощенный вариант системы с фоновой обработкой задач и отражением статуса задачи.

Система состоит из двух сервисов:

1. Сервис А - приложение с API, которое хранит статусы задач и другую мета-информацию
2. Сервис B - фоновый воркер-обработчик, который получает задания через очередь и выполняет

### Постановка задачи и получение статуса задачи

- Задачи ставятся в очередь выполнения через API Сервиса А.
- Постановка и отслеживание статусы задачи производится через обращение к API.
- Статусы задач можно хранить в памяти Сервиса А, либо в БД (на ваше усмотрение).
- Задача “выполняется” в Сервисе B и по окончании обновляет статус в Сервисе А.

### Методы API:

**Создание задачи**

Метод принимает в теле POST запроса следующие данные:

- человеко-понятное название задачи
- время выполнения задачи в секундах

В ответе возвращается уникальный идентификатор задачи, чтобы с помощью него отслеживать статус выполнения.

```python
POST /tasks

Request Data:
{
	name: str, // человеко-понятное название задачи
	processing_time: int, // время выполнения в секундах
}

Response:
{
	task_id: str, // UUID задачи в БД сервиса А
}
```

**Просмотр статуса задачи**

Через указание id задачи можно получить текущее состояние задачи

```python
GET /tasks/{task_id}

Response:
{
	task_id: str, // UUID задачи в БД сервиса А
	name: str, // человеко-понятное название задачи
	processing_time: int, // время выполнения в секундах
	status: int // статус задачи
}
```

Cтатусы задач:

- NEW (или 1)
- PROCESSING (или 2)
- COMPLETED (или 3)
- ERROR (или 4)

**Просмотр списка задач**

Метод отдает список всех задач с их данными

```python
GET /tasks

Response:
[
	{
		task_id: str, // UUID задачи в БД сервиса А
		name: str, // человеко-понятное название задачи
		processing_time: int, // время выполнения в секундах
		status: int // статус задачи
	},
	{
		task_id: str, // UUID задачи в БД сервиса А
		name: str, // человеко-понятное название задачи
		processing_time: int, // время выполнения в секундах
		status: int // статус задачи
	}
]
```

### Выполнение задач и обновление статусов

Воркер-обработчик (Сервис B) берет задачи из очереди, эмулирует процесс выполнения задачи путем ожидания N количества секунд, которые получили при создании задачи.

Воркер меняет статус у задачи в Сервисе А через API:

- в начале выполнения задачи
- по окончании выполнения
- при ошибке выполнения

Если воркер в задаче получает поле processing_time со значением секунд ожидания равным 13, то ожидает это количество секунд и завершает выполнения задачи с ошибкой, обновляет статус задачи в Сервисе А по HTTP API.

### Технологии

Для задания можно использовать, например, celery, rabbitmq, django, fastapi, postgresql, redis.

Желательно подготовить сервисы для запуска в docker контейнерах, например, подготовить docker compose.

## Ожидаемый результат

Приветствуется использование инструментов для улучшения качества кода (linters, formatters, coverage, автоматическая документация и т.п.)

**Ссылка на github репозиторий с кодом, который содержит:**

- README файл с ответами на вопросы в первом задании
- README файл с описанием как тестировать и запускать код;
- EXTRA: Dockerfile для сервиса;
- EXTRA: docker-compose.yml для запуска API и celery worker’a.