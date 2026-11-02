"""Контракт данных тикета HelpDesk Lite


1. Поля тикета при создании (TicketCreate -> Ticket):
   Обязательные поля при создании (передаются клиентом):
     title (str, min_length=1) — заголовок/краткая суть тикета.
   Необязательные поля при создании:
      - description (str | None, по умолчанию None) — подробное описание проблемы.
      - priority (Priority, по умолчанию normal) — приоритет тикета.
      - assignee (str | None, по умолчанию None) — назначенный исполнитель.
   Вычисляемые сервером поля:
     - id (int) — уникальный автоинкрементный идентификатор (начиная с 1).
     - status (TicketStatus) — начальный статус тикета, всегда выставляется "open".
     - created_at (datetime) — точное системное время создания тикета.

2. Допустимые значения priority и status:
   - priority (перечисление Priority):
     - "low" — низкий приоритет;
     - "normal" — обычный приоритет (по умолчанию);
     - "high" — высокий приоритет;
     - "urgent" — срочный приоритет.
   - status (перечисление TicketStatus):
     - "open" — открыт ;
     - "in_progress" — в работе;
     - "resolved" — решён;
     - "closed" — закрыт.

3. Разрешённые и запрещённые изменения через PATCH (TicketUpdate):
   - Разрешено изменять:
     - description (str | None) — текст описания;
     - priority (Priority | None) — уровень приоритета;
     - assignee (str | None) — назначенного исполнителя;
     - status (TicketStatus | None) — статус тикета (при валидации
       допустимости перехода согласно ALLOWED_TRANSITIONS).
   - Запрещено изменять:
     - id — системный неизменяемый ключ;
     - title — заголовок фиксируется при создании и не подлежит изменению через PATCH;
     - created_at — дата и время фиксации тикета неизменны.

4. Список разрешённых переходов статуса (ALLOWED_TRANSITIONS):
   - open -> in_progress
   - in_progress -> resolved, open
   - resolved -> closed, in_progress
   - closed -> пустое множество.
   Любые другие переходы запрещены.

5. Поведение сортировки по умолчанию (если параметры не переданы):
   - Параметр sort_by по умолчанию: "created_at".
   - Параметр order по умолчанию: "desc" (сначала новые тикеты).
   - Допустимые поля сортировки: "created_at" и "priority".
     При сортировке по "priority" используется взвешенная шкала важности:
     low (1) < normal (2) < high (3) < urgent (4).
     При order="desc" первыми идут срочные тикеты (urgent -> high -> normal -> low).
   - Недопустимые значения sort_by и order отклоняются валидатором FastAPI (HTTP 422).

6. Границы и значения по умолчанию для пагинации (page_size):
   - Значение по умолчанию: 5
   - Максимально допустимое значение: 20
     Если клиент запрашивает page_size > 20, сервер ограничивает размер страницы до 20.
   - Минимальный номер страницы page: 1

7. Коды ответов при ошибках:
   - При отсутствии тикета с запрашиваемым ticket_id:
     HTTP 404 Not Found (тело: {"detail": "Тикет <id> не найден"}).
   - При попытке запрещённого перехода статуса:
     HTTP 409 Conflict (тело: {"detail": "Переход <current> -> <target> запрещён"})
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .exceptions import InvalidStatusTransitionError, TicketNotFoundError
from .routers.tickets import router as tickets_router

app = FastAPI(
    title="HelpDesk Lite",
    description="Сервис регистрации и обработки тикетов техподдержки",
    version="1.0.0",
)


@app.exception_handler(TicketNotFoundError)
def handle_not_found(request: Request, exc: TicketNotFoundError) -> JSONResponse:
    """Обработчик отсутствия тикета — возвращает 404 Not Found."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidStatusTransitionError)
def handle_invalid_transition(
    request: Request, exc: InvalidStatusTransitionError
) -> JSONResponse:
    """Обработчик недопустимого перехода статуса — возвращает 409 Conflict."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


# Подключение роутера тикетов
app.include_router(tickets_router)

