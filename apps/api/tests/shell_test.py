import asyncio

from fastapi.testclient import TestClient

from procurement_api.config import AppConfig
from procurement_api.intake import CommodityGroupNotFoundException, IntakeApi
from procurement_api.models.commodity_group import CommodityGroupInfo
from procurement_api.models.procurement import OrderLine, ProcurementRequestCreate
from procurement_api.repository import (
    ProcurementRequestStatus,
    ProcurementRequestStored,
)
from procurement_api.shell import Shell, build_app


class StubIntake(IntakeApi):
    def __init__(self) -> None:
        self.commodity_groups: set[CommodityGroupInfo] = set()
        self.requests: dict[str, ProcurementRequestStored] = {}

    def get_commodity_groups(self) -> set[CommodityGroupInfo]:
        return {CommodityGroupInfo(category="Information Technology", name="Software")}

    def is_valid_commodity_group(self, name: str) -> bool:
        return name == "Software"

    def create_procurement_request(
        self, request: ProcurementRequestCreate
    ) -> dict[str, str]:
        if not self.is_valid_commodity_group(request.commodity_group):
            raise CommodityGroupNotFoundException()
        stored = ProcurementRequestStored(request)
        self.requests[stored.id] = stored
        return {
            "message": "Procurement request successful",
            "id": stored.id,
            "status": stored.status.value,
        }

    def get_all_requests(self) -> list[ProcurementRequestStored]:
        return list(self.requests.values())

    def get_request_by_id(self, request_id: str) -> ProcurementRequestStored | None:
        return self.requests.get(request_id)

    def update_request_status(
        self, request_id: str, status: ProcurementRequestStatus
    ) -> ProcurementRequestStored | None:
        request = self.requests.get(request_id)
        if request:
            request.status = status
        return request


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
        response_data = response.json()
        assert response_data["message"] == "Procurement request successful"
        assert "id" in response_data
        assert response_data["status"] == "open"


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


def test_get_all_requests_gives_200():
    # given an app with some requests
    stub_intake = StubIntake()
    app = build_app(stub_intake)

    # create some requests
    request1 = ProcurementRequestCreate(
        requestor_name="Alice Smith",
        title="Laptop Purchase",
        vendor_name="Tech Corp",
        vat_id="DE111111111",
        commodity_group="Software",
        order_lines=[
            OrderLine(
                position_description="Dell Laptop",
                unit_price=1000.0,
                amount=1,
                unit="pieces",
                total_price=1000.0,
            )
        ],
        total_cost=1000.0,
        department="IT",
    )
    request2 = ProcurementRequestCreate(
        requestor_name="Bob Jones",
        title="Software Licenses",
        vendor_name="Software Inc",
        vat_id="DE222222222",
        commodity_group="Software",
        order_lines=[
            OrderLine(
                position_description="MS Office License",
                unit_price=100.0,
                amount=5,
                unit="licenses",
                total_price=500.0,
            )
        ],
        total_cost=500.0,
        department="Engineering",
    )
    stub_intake.create_procurement_request(request1)
    stub_intake.create_procurement_request(request2)

    # when we call the get all requests endpoint
    with TestClient(app) as client:
        response = client.get("/intake/requests")

        # then we get a 200 OK response
        assert response.status_code == 200
        # and we get a list of requests
        requests = response.json()
        assert isinstance(requests, list)
        assert len(requests) == 2
        assert requests[0]["request"]["requestor_name"] == "Alice Smith"
        assert requests[1]["request"]["requestor_name"] == "Bob Jones"


def test_get_request_by_id_gives_200():
    # given an app with a request
    stub_intake = StubIntake()
    app = build_app(stub_intake)

    request = ProcurementRequestCreate(
        requestor_name="Charlie Brown",
        title="Office Supplies",
        vendor_name="Office Depot",
        vat_id="DE333333333",
        commodity_group="Software",
        order_lines=[
            OrderLine(
                position_description="Paper Reams",
                unit_price=25.0,
                amount=10,
                unit="reams",
                total_price=250.0,
            )
        ],
        total_cost=250.0,
        department="Admin",
    )
    result = stub_intake.create_procurement_request(request)
    request_id = result["id"]

    # when we call the get request by id endpoint
    with TestClient(app) as client:
        response = client.get(f"/intake/requests/{request_id}")

        # then we get a 200 OK response
        assert response.status_code == 200
        # and we get the correct request
        request_data = response.json()
        assert request_data["id"] == request_id
        assert request_data["request"]["requestor_name"] == "Charlie Brown"
        assert request_data["status"] == "open"


def test_get_request_by_id_gives_404():
    # given an app
    app = build_app(StubIntake())

    # when we call the get request by id endpoint with a non-existent id
    with TestClient(app) as client:
        response = client.get("/intake/requests/non-existent-id")

        # then we get a 404 not found response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_update_request_status_gives_200():
    # given an app with a request
    stub_intake = StubIntake()
    app = build_app(stub_intake)

    request = ProcurementRequestCreate(
        requestor_name="Diana Prince",
        title="Hardware Purchase",
        vendor_name="Hardware Inc",
        vat_id="DE444444444",
        commodity_group="Software",
        order_lines=[
            OrderLine(
                position_description="Network Switch",
                unit_price=750.0,
                amount=1,
                unit="pieces",
                total_price=750.0,
            )
        ],
        total_cost=750.0,
        department="Operations",
    )
    result = stub_intake.create_procurement_request(request)
    request_id = result["id"]

    # when we update the request status
    with TestClient(app) as client:
        response = client.patch(
            f"/intake/requests/{request_id}/status",
            json={"status": "in-progress"},
        )

        # then we get a 200 OK response
        assert response.status_code == 200
        # and the status is updated
        updated_request = response.json()
        assert updated_request["id"] == request_id
        assert updated_request["status"] == "in-progress"


def test_update_request_status_gives_404():
    # given an app
    app = build_app(StubIntake())

    # when we try to update a non-existent request
    with TestClient(app) as client:
        response = client.patch(
            "/intake/requests/non-existent-id/status",
            json={"status": "in-progress"},
        )

        # then we get a 404 not found response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
