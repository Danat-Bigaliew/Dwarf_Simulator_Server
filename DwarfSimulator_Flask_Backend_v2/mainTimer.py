import time
from backend_scripts.Markets.Base.GetStockExchangeData import update_stock_exchange_price


class Timer:
    def __init__(self, test_callback):
        self.start_time = time.time()
        self.test_callback = test_callback

    def reset_timer(self):
        self.start_time = time.time()

    async def run(self):
        while True:
            elapsed_time = time.time() - self.start_time

            if int(elapsed_time) == 3600:
                stock_exchange_data = update_stock_exchange_price()
                await self.send_message(stock_exchange_data)
                self.reset_timer()
                print("Таймер обнулен. Новый цикл начался.")

            time.sleep(1)

    async def send_message(self, message):
        await self.test_callback(message)

async def start_timer(test_callback):
    timer = Timer(test_callback)
    await timer.run()

if __name__ == "__main__":
    print("Таймер запущен. Программа работает в фоне.")
    # Основной поток запускает таймер в фоновом потоке
    start_timer(print)