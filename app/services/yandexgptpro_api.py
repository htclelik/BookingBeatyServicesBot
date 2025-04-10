# services/ai_assistant_handler.py
from yandex_cloud_ml_sdk import YCloudML
from app.config import YANDEX_API_KEY, FOLDER_ID

sdk = YCloudML(
    folder_id=FOLDER_ID, auth=YANDEX_API_KEY
)

model = sdk.models.completions("yandexgpt", model_version="rc")
model = model.configure(temperature=0.3)
result = model.run(
    [
        {"role": "system", "text": ""},
        {
            "role": "user",
            "text": "Придумай 5 названий для нового смартфона от производителя Тolk. Объясни свои идеи. Напиши ответ в JSON с полями name и description",
        },
    ]
)

for alternative in result:
    print(alternative)
