# order_service/app/messaging.py
import aio_pika
import json

async def listen_for_orders():
    """
    Асинхронное слушание очереди RabbitMQ и обработка сообщений от Auth Service.
    """
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("order_queue", durable=True)  # Очередь с заданным именем

        async for message in queue:
            async with message.process():
                # Получаем данные из сообщения
                message_data = json.loads(message.body.decode())
                user_id = message_data.get("user_id")
                if user_id:
                    print(f"Received user_id: {user_id}")
                    # Здесь можно вызвать функцию, которая будет обрабатывать данные пользователя
                    await handle_new_user_order(user_id)

async def handle_new_user_order(user_id: int):
    """
    Обработка нового пользователя (например, создание заказа).
    """
    print(f"Handling new order for user {user_id}")
    # Здесь можно добавить логику создания заказа для пользователя
