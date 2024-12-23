# auth_service/app/messaging.py
import aio_pika
import json

async def send_message_to_orders_service(user_id: int):
    """
    Асинхронная отправка сообщения в очередь RabbitMQ для сервиса заказов.
    """
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")  # Подключение к RabbitMQ
    async with connection:
        channel = await connection.channel()  # Создание канала
        await channel.default_exchange.publish(  # Отправка сообщения
            aio_pika.Message(
                body=json.dumps({"user_id": user_id}).encode()  # Сообщение с ID пользователя
            ),
            routing_key="order_queue",  # Ключ маршрутизации
        )
        print(f"Message sent to order_queue: {{'user_id': {user_id}}}")
