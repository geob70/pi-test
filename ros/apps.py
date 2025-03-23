from django.apps import AppConfig
import asyncio
import threading
from .tasks import periodic_send_data_usage


class RosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ros"

    def ready(self):
        """
        Starts the periodic async task when the Django app is ready.
        """

        # Start the async loop in a separate thread
        thread = threading.Thread(target=self.start_async_task, daemon=True)
        thread.start()

    def start_async_task(self):
        """
        Starts the asyncio event loop to run the periodic_send_data_usage task.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(periodic_send_data_usage())
