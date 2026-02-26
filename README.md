# edu‑auditor

Система аудита учебных материалов с использованием современных методов и подходов – RAG, LLM.

## Usage

1. Создать питоновское окружение:

    ```bash
    python3.14 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. Запустить `arxiv_fetcher.py` – статьи должны загрузиться в папку `DataDocs`:

    ```bash
    python dataScripts/arxiv_fetcher.py
    ```

5. Настроить доступ к локальной PostgreSQL‑базе `vector_database_fill.py`

6. В том же файле, в методе `load_and_save_database`, установить аргументы:

   * `folder_path` – путь к папке со статьями,
   * `save_to` – произвольный путь, куда будет сохранена векторная база.

7. Запустить `vector_database_fill.py`. Он чанкует PDF‑ки, загружает куски в Postgres и
   одновременно векторизует их в векторную базу данных. Это может занять некоторое время:

    ```bash
    python vector_database_fill.py
    ```

8. Открыть `modelAPI.py`. Убедиться, что в переменных окружения есть ключ авторизации.
   Его можно получить здесь: https://developers.sber.ru/portal/products/gigachat-api

9. Запустить `modelAPI.py`, выбрав удобный для вас порт:

    ```bash
    export GIGACHAT_API_KEY="ваш_ключ"
    python modelAPI.py --port 8000
    ```

10. Перейти в `relational_database.py`. Настроить подключение к Postgres и векторной базе,
    запустить на удобном порте:

    ```bash
    python relational_database.py --port 8001
    ```

11. Перейти в директорию `frontend` и запустить Streamlit‑сервер:

    ```bash
    cd frontend
    streamlit run app.py --server.port 8501
    ```

12. Убедиться, что все выбранные порты на бэкенде и фронтенде связаны по HTTP.
