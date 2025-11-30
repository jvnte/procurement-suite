import tempfile
from pathlib import Path

import pytest

from procurement_api.intake import CommodityGroupNotFoundException, Intake
from procurement_api.models.commodity_group import CommodityGroupInfo
from procurement_api.models.procurement import OrderLine, ProcurementRequestCreate
from procurement_api.repository import (
    InMemoryRepository,
    ProcurementRequestStatus,
    Repository,
)


@pytest.fixture
def temp_commodity_groups_file():
    """Create a temporary commodity groups JSON file for testing."""
    content = """[
        {"category": "Information Technology", "name": "Software"},
        {"category": "Information Technology", "name": "Hardware"},
        {"category": "General Services", "name": "Consulting"}
    ]"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def repository():
    """Create a fresh in-memory repository for each test."""
    return InMemoryRepository()


@pytest.fixture
def intake(temp_commodity_groups_file: str, repository: Repository):
    """Create an Intake instance with test data."""
    return Intake(temp_commodity_groups_file, repository)


def test_load_commodity_groups(intake: Intake):
    # given an intake instance
    # when we get the commodity groups
    commodity_groups = intake.get_commodity_groups()

    # then we get the expected commodity groups
    assert len(commodity_groups) == 3
    assert (
        CommodityGroupInfo(category="Information Technology", name="Software")
        in commodity_groups
    )
    assert (
        CommodityGroupInfo(category="Information Technology", name="Hardware")
        in commodity_groups
    )
    assert (
        CommodityGroupInfo(category="General Services", name="Consulting")
        in commodity_groups
    )


def test_is_valid_commodity_group_returns_true_for_valid_name(intake: Intake):
    # given an intake instance
    # when we check a valid commodity group name
    is_valid = intake.is_valid_commodity_group("Software")

    # then it returns true
    assert is_valid is True


def test_is_valid_commodity_group_returns_false_for_invalid_name(intake: Intake):
    # given an intake instance
    # when we check an invalid commodity group name
    is_valid = intake.is_valid_commodity_group("InvalidGroup")

    # then it returns false
    assert is_valid is False


def test_create_procurement_request_with_valid_commodity_group(intake: Intake):
    # given a valid procurement request
    request = ProcurementRequestCreate(
        requestor_name="Alice Smith",
        title="Software Licenses",
        vendor_name="Adobe Inc",
        vat_id="DE123456789",
        commodity_group="Software",
        order_lines=[
            OrderLine(
                position_description="Adobe Creative Cloud",
                unit_price=500.0,
                amount=10,
                unit="licenses",
                total_price=5000.0,
            )
        ],
        total_cost=5000.0,
        department="Design",
    )

    # when we create the procurement request
    result = intake.create_procurement_request(request)

    # then we get a successful response
    assert result["message"] == "Procurement request successful"
    assert "id" in result
    assert result["status"] == "open"


def test_create_procurement_request_with_invalid_commodity_group(intake: Intake):
    # given a procurement request with invalid commodity group
    request = ProcurementRequestCreate(
        requestor_name="Bob Jones",
        title="Invalid Request",
        vendor_name="Some Vendor",
        vat_id="DE987654321",
        commodity_group="InvalidGroup",
        order_lines=[
            OrderLine(
                position_description="Some Item",
                unit_price=100.0,
                amount=1,
                unit="pieces",
                total_price=100.0,
            )
        ],
        total_cost=100.0,
        department="Admin",
    )

    # when we try to create the procurement request
    # then it raises CommodityGroupNotFoundException
    with pytest.raises(CommodityGroupNotFoundException):
        intake.create_procurement_request(request)


def test_get_all_requests_returns_empty_list_initially(intake: Intake):
    # given a new intake instance
    # when we get all requests
    requests = intake.get_all_requests()

    # then we get an empty list
    assert requests == []


def test_get_all_requests_returns_created_requests(intake: Intake):
    # given we create some requests
    request1 = ProcurementRequestCreate(
        requestor_name="Charlie Brown",
        title="Hardware Purchase",
        vendor_name="Dell",
        vat_id="DE111111111",
        commodity_group="Hardware",
        order_lines=[
            OrderLine(
                position_description="Dell Monitor",
                unit_price=300.0,
                amount=2,
                unit="pieces",
                total_price=600.0,
            )
        ],
        total_cost=600.0,
        department="IT",
    )
    request2 = ProcurementRequestCreate(
        requestor_name="Diana Prince",
        title="Consulting Services",
        vendor_name="Accenture",
        vat_id="DE222222222",
        commodity_group="Consulting",
        order_lines=[
            OrderLine(
                position_description="Management Consulting",
                unit_price=150.0,
                amount=40,
                unit="hours",
                total_price=6000.0,
            )
        ],
        total_cost=6000.0,
        department="Strategy",
    )

    intake.create_procurement_request(request1)
    intake.create_procurement_request(request2)

    # when we get all requests
    requests = intake.get_all_requests()

    # then we get all created requests
    assert len(requests) == 2
    assert requests[0].request.requestor_name == "Charlie Brown"
    assert requests[1].request.requestor_name == "Diana Prince"


def test_get_request_by_id_returns_correct_request(intake: Intake):
    # given we create a request
    request = ProcurementRequestCreate(
        requestor_name="Edward Norton",
        title="Software Development",
        vendor_name="GitHub",
        vat_id="DE333333333",
        commodity_group="Software",
        order_lines=[
            OrderLine(
                position_description="GitHub Enterprise",
                unit_price=21.0,
                amount=50,
                unit="licenses",
                total_price=1050.0,
            )
        ],
        total_cost=1050.0,
        department="Engineering",
    )

    result = intake.create_procurement_request(request)
    request_id = result["id"]

    # when we get the request by id
    stored_request = intake.get_request_by_id(request_id)

    # then we get the correct request
    assert stored_request is not None
    assert stored_request.id == request_id
    assert stored_request.request.requestor_name == "Edward Norton"
    assert stored_request.status == ProcurementRequestStatus.OPEN


def test_get_request_by_id_returns_none_for_nonexistent_id(intake: Intake):
    # given an intake instance
    # when we try to get a non-existent request
    stored_request = intake.get_request_by_id("non-existent-id")

    # then we get None
    assert stored_request is None


def test_update_request_status_updates_correctly(intake: Intake):
    # given we create a request
    request = ProcurementRequestCreate(
        requestor_name="Frank Miller",
        title="Office Equipment",
        vendor_name="Staples",
        vat_id="DE444444444",
        commodity_group="Hardware",
        order_lines=[
            OrderLine(
                position_description="Standing Desk",
                unit_price=500.0,
                amount=5,
                unit="pieces",
                total_price=2500.0,
            )
        ],
        total_cost=2500.0,
        department="Facilities",
    )

    result = intake.create_procurement_request(request)
    request_id = result["id"]

    # when we update the status
    updated_request = intake.update_request_status(
        request_id, ProcurementRequestStatus.IN_PROGRESS
    )

    # then the status is updated
    assert updated_request is not None
    assert updated_request.status == ProcurementRequestStatus.IN_PROGRESS

    # and when we retrieve it again, the status persists
    retrieved_request = intake.get_request_by_id(request_id)
    assert retrieved_request is not None
    assert retrieved_request.status == ProcurementRequestStatus.IN_PROGRESS


def test_update_request_status_returns_none_for_nonexistent_id(intake: Intake):
    # given an intake instance
    # when we try to update a non-existent request
    updated_request = intake.update_request_status(
        "non-existent-id", ProcurementRequestStatus.CLOSED
    )

    # then we get None
    assert updated_request is None


def test_update_request_status_through_lifecycle(intake: Intake):
    # given we create a request
    request = ProcurementRequestCreate(
        requestor_name="Grace Hopper",
        title="Computing Resources",
        vendor_name="AWS",
        vat_id="DE555555555",
        commodity_group="Software",
        order_lines=[
            OrderLine(
                position_description="Cloud Computing Credits",
                unit_price=10000.0,
                amount=1,
                unit="annual",
                total_price=10000.0,
            )
        ],
        total_cost=10000.0,
        department="Cloud Operations",
    )

    result = intake.create_procurement_request(request)
    request_id = result["id"]

    # when we transition through the lifecycle
    # OPEN -> IN_PROGRESS
    intake.update_request_status(request_id, ProcurementRequestStatus.IN_PROGRESS)
    req = intake.get_request_by_id(request_id)
    assert req is not None
    assert req.status == ProcurementRequestStatus.IN_PROGRESS

    # IN_PROGRESS -> CLOSED
    intake.update_request_status(request_id, ProcurementRequestStatus.CLOSED)
    req = intake.get_request_by_id(request_id)
    assert req is not None
    assert req.status == ProcurementRequestStatus.CLOSED


def test_commodity_groups_are_immutable(intake: Intake):
    # given we get the commodity groups
    groups1 = intake.get_commodity_groups()
    groups2 = intake.get_commodity_groups()

    # then they are the same set
    assert groups1 == groups2
    assert groups1 is groups2  # Same object reference
