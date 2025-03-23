import asyncio
import os
import aiohttp
from django.http import HttpResponse
from rest_framework.response import Response
import logging
import routeros_api
import json


def openConnection():
    # Get the current directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the credentials.json file
    credentials_file = os.path.join(current_dir, "credentials.json")

    # Read credentials from the file
    with open(credentials_file, "r") as file:
        data = json.load(file)

    connection = routeros_api.RouterOsApiPool(
        host=data["host"],
        username=data["hostname"],
        password=data["password"],
        plaintext_login=True,
    )
    return connection


async def fetch_user_data(api):
    """
    Fetching user data asynchronously. Replace this with your MikroTik data fetching logic.
    """

    # Fetch user data from the MikroTik router
    # Fetch All Users
    users = api.get_resource("/ip/hotspot/user")
    all_users = users.get()
    return all_users


async def send_to_node_api(data):
    """
    Sends fetched user data to the Node.js API asynchronously.
    """
    logger = logging.getLogger(__name__)
    logger.debug("Send started")
    async with aiohttp.ClientSession() as session:
        try:
            logger.info("Sending data to Node.js API")
            async with session.post(
                "https://4576-77-99-33-6.ngrok-free.app/api/admin/router/data-usage",
                json=data,
                ssl=False,
            ) as response:
                if response.status == 200:
                    return Response({"message": "Data sent successfully"}, status=200)
                else:
                    print(f"Failed to send data. Status code: {response.status}")
                    logger.error(f"Failed to send data. Status code: {response.status}")
                    return Response(
                        {
                            "error": f"Failed to send data. Status code: {response.status}"
                        },
                        status=response.status,
                    )
        except Exception as e:
            print(f"Error sending data to Node.js API: {e}")
            logger.error(f"Error sending data to Node.js API: {e}")
            return Response(
                {"error": f"Error sending data to Node.js API: {e}"}, status=500
            )


async def periodic_send_data_usage():
    """
    Periodically sends user data usage to the Node.js API every 10 seconds.
    """
    print("Task started printer")
    logger = logging.getLogger(__name__)
    logger.debug("Task started")

    connection = openConnection()
    api = connection.get_api()

    while True:
        # Fetch data asynchronously
        data = await fetch_user_data(api)
        logger.info("Data fetch successfully")

        # Send data asynchronously
        await send_to_node_api(data)

        # Wait 10 seconds before the next iteration
        await asyncio.sleep(15)
