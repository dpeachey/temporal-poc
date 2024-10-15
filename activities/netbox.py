import json
import os
from typing import Any

import requests
from temporalio import activity

NETBOX_URL = "https://my-netbox.acme.com"
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


@activity.defn
def get_vlans(name: str) -> Any:
    r = requests.get(
        f"{NETBOX_URL}/api/ipam/vlans/?limit=2000&ordering=vid",
        headers=HEADERS,
        verify=False,
    )
    return json.loads(r.text)


@activity.defn
def get_site_by_name(request: dict[str, str | int]) -> Any:
    r = requests.get(
        f"{NETBOX_URL}/api/dcim/sites/?name={request['dc']}",
        headers=HEADERS,
        verify=False,
    )
    return json.loads(r.text)


@activity.defn
def add_new_vlan(vlan: dict[str, str | int]) -> Any:
    r = requests.post(
        f"{NETBOX_URL}/api/ipam/vlans/",
        data=json.dumps(vlan),
        headers=HEADERS,
        verify=False,
    )
    return json.loads(r.text)


@activity.defn
def get_container_prefix(site_id: int) -> Any:
    r = requests.get(
        f"{NETBOX_URL}/api/ipam/prefixes/?site_id={site_id}&status=container",
        headers=HEADERS,
        verify=False,
    )
    return json.loads(r.text)


@activity.defn
def request_new_prefix(prefix_request: dict[str, str | int]) -> Any:
    r = requests.post(
        f"{NETBOX_URL}/api/ipam/prefixes/{prefix_request['container_prefix_id']}/available-prefixes/",
        data=json.dumps({"prefix_length": prefix_request["prefix_length"]}),
        headers=HEADERS,
        verify=False,
    )
    return json.loads(r.text)
