from yandex_cloud_ml_sdk import YCloudML

API_TOKEN = "TOKEN"
API_FOLDER = "TOKEN"
API_TEMPERATURE = 0.3
API_SDK = YCloudML(
    auth = API_TOKEN,
    folder_id = API_FOLDER,
)
