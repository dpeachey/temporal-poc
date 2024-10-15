import asyncio
import concurrent.futures
import os

# Import the activity and workflow from our other files
from activities.netbox import (
    add_new_vlan,
    get_container_prefix,
    get_site_by_name,
    get_vlans,
    request_new_prefix,
)
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.get_network import GetNetwork

WORKER_TASK_QUEUE = os.getenv("WORKER_TASK_QUEUE")


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(
        "my-temporal-server.acme.com:7233", namespace="my-namespace"
    )

    # Run the worker
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        worker = Worker(
            client,
            task_queue=WORKER_TASK_QUEUE,
            workflows=[GetNetwork],
            activities=[
                get_vlans,
                add_new_vlan,
                get_site_by_name,
                get_container_prefix,
                request_new_prefix,
            ],
            activity_executor=activity_executor,
        )
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
