import asyncio

from fastapi.testclient import TestClient

from asklio_api.config import AppConfig
from asklio_api.intake import IntakeApi
from asklio_api.models.commodity_group import CommodityGroupInfo
from asklio_api.repository import ProcurementRequestStatus
from asklio_api.shell import Shell, build_app


class StubIntake(IntakeApi):
    def __init__(self) -> None:
        self.commodity_groups: set[CommodityGroupInfo] = set()

    def get_commodity_groups(self) -> set[CommodityGroupInfo]:
        return {CommodityGroupInfo(category="Information Technology", name="Software")}

    def is_valid_commodity_group(self, name: str) -> bool:
        return name == "Software"

    def create_procurement_request(self): ...
    def get_all_requests(self): ...
    def get_request_by_id(self, request_id: str): ...
    def update_request_status(
        self, request_id: str, status: ProcurementRequestStatus
    ): ...


async def test_shell_can_be_shutdown(config: AppConfig):
    # Given a running shell
    intake = StubIntake()
    shell = Shell(config, intake)
    loop = asyncio.get_event_loop()
    task = loop.create_task(shell.run())

    # wait for the server to start
    await asyncio.sleep(0.01)

    # When the shell is shutdown
    shell.shutdown()

    # Then the shell task is done after 1 second
    await asyncio.wait_for(task, timeout=1.0)


def test_post_intake_request_gives_201():
    # given an app
    app = build_app(StubIntake())

    # when we call the intake router with a valid procurement request
    payload = {
        "requestor_name": "John Doe",
        "title": "Adobe Creative Cloud Subscription",
        "vendor_name": "Adobe Systems",
        "vat_id": "DE123456789",
        "commodity_group": "Software",
        "order_lines": [
            {
                "position_description": "Adobe Photoshop License",
                "unit_price": 200.0,
                "amount": 5,
                "unit": "licenses",
                "total_price": 1000.0,
            },
            {
                "position_description": "Adobe Illustrator License",
                "unit_price": 150.0,
                "amount": 3,
                "unit": "licenses",
                "total_price": 450.0,
            },
        ],
        "total_cost": 1450.0,
        "department": "Marketing",
    }

    with TestClient(app) as client:
        response = client.post("/intake/request", json=payload)

        # then we get a 201 created response
        assert response.status_code == 201
        assert response.json() == {
            "message": "Procurement request created successfully"
        }


def test_post_intake_request_raises_400():
    # given an app
    app = build_app(StubIntake())

    # when we call the intake router with an invalid commodity group
    payload = {
        "requestor_name": "John Doe",
        "title": "Office Supplies",
        "vendor_name": "Office Depot",
        "vat_id": "DE987654321",
        "commodity_group": "InvalidGroup",
        "order_lines": [
            {
                "position_description": "Printer Paper",
                "unit_price": 10.0,
                "amount": 5,
                "unit": "boxes",
                "total_price": 50.0,
            }
        ],
        "total_cost": 50.0,
        "department": "Administration",
    }

    with TestClient(app) as client:
        response = client.post("/intake/request", json=payload)

        # then we get a 400 bad request response
        assert response.status_code == 400
        assert "Invalid commodity_group" in response.json()["detail"]


def test_get_intake_commodity_groups_gives_200():
    # given an app
    app = build_app(StubIntake())

    # when we call the commodity groups endpoint
    with TestClient(app) as client:
        response = client.get("/intake/commodity_groups")

        # then we get a 200 OK response
        assert response.status_code == 200
        # and we get a list of commodity groups
        commodity_groups = response.json()
        assert isinstance(commodity_groups, list)
        assert len(commodity_groups) == 1
        assert commodity_groups[0]["category"] == "Information Technology"
        assert commodity_groups[0]["name"] == "Software"
