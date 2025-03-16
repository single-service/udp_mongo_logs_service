import json
import socket

def send_udp_message(message, host, port):
    """
    Отправка сообщения на UDP-сервер.
    
    :param message: Сообщение, которое нужно отправить.
    :param host: IP-адрес или доменное имя сервера.
    :param port: Порт, на который отправляется сообщение.
    """
    # Создаем UDP-сокет
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Преобразуем строку сообщения в байты
        data = message.encode()
        
        # Отправляем данные на указанный хост и порт
        sock.sendto(data, (host, port))
        
        print(f"Сообщение '{message}' успешно отправлено на {host}:{port}")
    
    except Exception as e:
        print(f"Произошла ошибка при отправке сообщения: {e}")
    
    finally:
        # Закрываем сокет
        sock.close()

if __name__ == "__main__":
    # Параметры отправки сообщения
    message = json.dumps({
        "type": "logs",
        "collection": "logs",
        "message": {
            "created_dt": "2024-01-01 00:00:00",
            "message": "new message"
        }
    })
    host = "127.0.0.1"  # Локальный хост
    port = 9999          # Порт, на котором слушает сервер
    
    # Вызываем функцию отправки сообщения
    send_udp_message(message, host, port)