Вот минимальный пример FastAPI-сервиса, который возвращает `{"message": "hello"}` и доступен через Postman.

## 1. Установка зависимостей

```bash
pip install fastapi uvicorn
```

## 2. Код (`main.py`)

```python
from fastapi import FastAPI

app = FastAPI(title="DG Do Hello Service", version="0.1")

@app.get("/")
@app.get("/hello")
def hello():
    return {"message": "hello"}
```

## 3. Запуск

```bash
uvicorn main:app --reload --port 8000
```

После запуска сервер будет доступен по адресу:  
`http://localhost:8000`

## 4. Проверка через Postman

- **Метод:** `GET`
- **URL:** `http://localhost:8000/hello` (или `http://localhost:8000/`)
- Нажать **Send**

**Ответ:**

```json
{
  "message": "hello"
}
```

## 5. Альтернативный вариант с POST

Если нужен POST-запрос с телом:

```python
from pydantic import BaseModel

class HelloRequest(BaseModel):
    name: str

@app.post("/hello")
def hello_post(body: HelloRequest):
    return {"message": f"hello, {body.name}"}
```

Тогда в Postman:  
- Метод `POST`, URL `http://localhost:8000/hello`  
- Вкладка **Body** → **raw** → **JSON**  
```json
{"name": "world"}
```
Ответ: `{"message": "hello, world"}`

Готово. Запускайте и проверяйте.