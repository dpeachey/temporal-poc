import asyncio
import os

from temporalio.client import Client
from workflows.get_network import GetNetwork, Request

WORKER_TASK_QUEUE = os.getenv("WORKER_TASK_QUEUE")


async def main():
    request = Request(name="test_network", dc="DC1", vrf="VRF1", size=24)
    print(f"Request: {request.model_dump_json(indent=4)}")

    # Create client connected to server at the given address
    client = await Client.connect(
        "my-temporal-server.acme.com:7233", namespace="my-namespace"
    )

    # Execute a workflow
    result = await client.execute_workflow(
        GetNetwork.run,
        request,
        id="get-network",
        task_queue=WORKER_TASK_QUEUE,
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
