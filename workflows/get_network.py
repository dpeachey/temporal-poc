from datetime import timedelta

from pydantic import BaseModel
from temporalio import workflow

# Import our activity, passing it through the sandbox
with workflow.unsafe.imports_passed_through():
    from activities.netbox import (
        add_new_vlan,
        get_container_prefix,
        get_site_by_name,
        get_vlans,
        request_new_prefix,
    )


class Request(BaseModel):
    name: str
    dc: str
    vrf: str
    size: int


class Vlan(BaseModel):
    vid: int
    site: int
    name: str
    status: str = "reserved"


class Network(BaseModel):
    vlan: int
    network: str


@workflow.defn
class GetNetwork:
    @workflow.run
    async def run(self, request: dict[str, str | int]) -> str:
        # First get a list of all VLANs from NetBox
        vlans_dict = await workflow.execute_activity(
            get_vlans, "GetNetwork", schedule_to_close_timeout=timedelta(seconds=10)
        )
        vlans = {vlan["vid"] for vlan in vlans_dict["results"]}

        # Find the first available VLAN ID
        vlan_range = range(1, len(vlans))
        vlan_id = min(set(vlan_range) - vlans)

        # Get the ID of the site from the DC name that is in the request
        site_dict = await workflow.execute_activity(
            get_site_by_name, request, schedule_to_close_timeout=timedelta(seconds=10)
        )
        site_id = site_dict["results"][0]["id"]

        # Create a new VLAN in NetBox
        vlan = Vlan(vid=vlan_id, site=site_id, name=request["name"])
        await workflow.execute_activity(
            add_new_vlan, vlan, schedule_to_close_timeout=timedelta(seconds=10)
        )

        # Get the container prefix of the site
        container_prefix_dict = await workflow.execute_activity(
            get_container_prefix,
            site_id,
            schedule_to_close_timeout=timedelta(seconds=10),
        )
        container_prefix_id = container_prefix_dict["results"][0]["id"]

        # Request a new prefix assignment for the size requested
        prefix_request: dict[str, int] = {
            "container_prefix_id": container_prefix_id,
            "prefix_length": request["size"],
        }
        prefix_dict = await workflow.execute_activity(
            request_new_prefix,
            prefix_request,
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        # Return the assigned VLAN and Prefix
        network = Network(vlan=vlan_id, network=prefix_dict["prefix"])
        return network.model_dump_json(indent=4)
