import datetime
import os
import uuid

import requests
from azure.identity import ManagedIdentityCredential


API_VERSION = "2024-02-01-preview"
TOKEN_SCOPE = "https://management.azure.com/.default"
SOURCE_SYSTEM = "GreyNoiseSample"


def utc_timestamp(value: datetime.datetime) -> str:
    return value.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def create_sample_indicator(ip_address: str, now: datetime.datetime) -> dict:
    indicator_id = uuid.uuid5(uuid.NAMESPACE_URL, f"greynoise-sample:{ip_address}")
    return {
        "type": "indicator",
        "spec_version": "2.1",
        "id": f"indicator--{indicator_id}",
        "created": utc_timestamp(now),
        "modified": utc_timestamp(now),
        "name": f"Sample IP indicator {ip_address}",
        "description": "Sample indicator uploaded with an Azure managed identity.",
        "indicator_types": ["malicious-activity"],
        "pattern": f"[ipv4-addr:value = '{ip_address}']",
        "pattern_type": "stix",
        "valid_from": utc_timestamp(now),
        "valid_until": utc_timestamp(now + datetime.timedelta(days=1)),
        "confidence": 50,
    }


def get_azure_credential() -> ManagedIdentityCredential:
    # No client_id: uses the system-assigned managed identity of the hosting Azure resource.
    return ManagedIdentityCredential()


def upload_sample_indicators() -> dict[str, object]:
    workspace_id = os.environ["WORKSPACE_ID"]
    credential = get_azure_credential()
    access_token = credential.get_token(TOKEN_SCOPE).token
    now = datetime.datetime.now(datetime.timezone.utc)
    indicators = [
        create_sample_indicator("192.0.2.10", now),
        create_sample_indicator("198.51.100.20", now),
    ]

    url = (
        f"https://api.ti.sentinel.azure.com/workspaces/{workspace_id}/"
        "threat-intelligence-stix-objects:upload"
    )
    response = requests.post(
        url,
        params={"api-version": API_VERSION},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"sourcesystem": SOURCE_SYSTEM, "stixobjects": indicators},
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(
            f"Upload Indicators API returned HTTP {response.status_code}: "
            f"{response.text}"
        )

    errors = response.json() if response.text.strip() else []
    return {"status_code": response.status_code, "errors": errors}


if __name__ == "__main__":
    print(upload_sample_indicators())
