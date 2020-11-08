from typing import Optional, Union
import pytest
import io
import os
from datetime import datetime, timedelta

from aioletterxpress.client import LetterxpressClient
from aioletterxpress.enums import JobStatus, ColorTypes, ShipTypes, PrintModes


def test_get_balance(event_loop, client: LetterxpressClient) -> None:
    response = event_loop.run_until_complete(client.get_balance())
    assert response["status"] == 200
    assert "value" in response["balance"]


def test_get_job(event_loop, client: LetterxpressClient) -> None:
    create_job_response = event_loop.run_until_complete(
        client.set_job(pdf="./tests/test.pdf")
    )
    response = event_loop.run_until_complete(
        client.get_job(id=create_job_response["letter"]["job_id"])
    )
    assert response["status"] == 200
    assert create_job_response["letter"]["job_id"] == response["job"]["jid"]


@pytest.mark.parametrize(
    "address", ["Max Mustermann, Musterstrasse 1, 12345 Musterstadt", None]
)
@pytest.mark.parametrize("color", [color for color in ColorTypes])
@pytest.mark.parametrize("mode", [mode for mode in PrintModes])
@pytest.mark.parametrize("ship", [ship_type for ship_type in ShipTypes])
@pytest.mark.parametrize("c4", [True, False])
@pytest.mark.parametrize("dispatch_date", [None, datetime.now() + timedelta(days=3)])
@pytest.mark.parametrize("pdf", ["./tests/test.pdf"])
def test_set_job(
    event_loop,
    *,
    client: LetterxpressClient,
    pdf: Union[str, io.IOBase],
    dispatch_date: Optional[datetime],
    address: Optional[str],
    color: ColorTypes,
    ship: ShipTypes,
    mode: PrintModes,
    c4: bool
) -> None:
    response = event_loop.run_until_complete(
        client.set_job(
            pdf=pdf,
            dispatch_date=dispatch_date,
            ship=ship,
            color=color,
            mode=mode,
            c4=c4,
        )
    )

    assert response["status"] == 200
    assert response["letter"]["specification"]["color"] == color
    assert response["letter"]["specification"]["mode"] == mode
    assert response["letter"]["specification"]["ship"] == ship


@pytest.mark.parametrize(
    "address", ["Max Mustermann, Musterstrasse 1, 12345 Musterstadt", None]
)
@pytest.mark.parametrize("color", [color for color in ColorTypes])
@pytest.mark.parametrize("mode", [mode for mode in PrintModes])
@pytest.mark.parametrize("ship", [ship_type for ship_type in ShipTypes])
@pytest.mark.parametrize("c4", [True, False])
@pytest.mark.parametrize("pdf", ["./tests/test.pdf"])
def test_get_price(
    event_loop,
    *,
    client: LetterxpressClient,
    pdf: Union[str, io.IOBase],
    address: Optional[str],
    color: ColorTypes,
    ship: ShipTypes,
    mode: PrintModes,
    c4: bool
) -> None:
    response = event_loop.run_until_complete(
        client.get_price(pdf=pdf, ship=ship, color=color, mode=mode, c4=c4)
    )
    assert response["status"] == 200
    assert response["letter"]["specification"]["color"] == color
    assert response["letter"]["specification"]["mode"] == mode
    assert response["letter"]["specification"]["ship"] == ship


@pytest.mark.parametrize(
    "job_status,days",
    [
        (JobStatus.QUEUE, None),
        (JobStatus.SENT, None),
        (JobStatus.DELETED, None),
        (JobStatus.QUEUE, 10),
        (JobStatus.SENT, 10),
        (JobStatus.DELETED, 10),
        (JobStatus.HOLD, None),
        (JobStatus.TIMER, None),
    ],
)
def test_get_jobs(
    event_loop, client: LetterxpressClient, job_status: JobStatus, days: int
):
    response = event_loop.run_until_complete(
        client.get_jobs(job_status=job_status, days=days)
    )
    assert (response["status"] == 200 and "jobs" in response) or (
        response["status"] == 404 and response["message"] == "Keine Daten gefunden"
    )


def test_list_invoices(event_loop, client: LetterxpressClient) -> None:
    response = event_loop.run_until_complete(client.list_invoices())
    assert response["status"] == 200


def test_get_invoice(event_loop, client: LetterxpressClient) -> None:
    invoice_path = event_loop.run_until_complete(client.get_invoice(id=1, path="./"))
    assert os.path.isfile(invoice_path)


def test_delete_job(event_loop, client: LetterxpressClient) -> None:
    create_job_response = event_loop.run_until_complete(
        client.set_job(pdf="./tests/test.pdf")
    )
    response = event_loop.run_until_complete(
        client.delete_job(id=create_job_response["letter"]["job_id"])
    )
    assert response["status"] == 200


@pytest.mark.parametrize(
    "address", ["Max Mustermann, Musterstrasse 1, 12345 Musterstadt", None]
)
@pytest.mark.parametrize("color", [color for color in ColorTypes])
@pytest.mark.parametrize("mode", [mode for mode in PrintModes])
@pytest.mark.parametrize("ship", [ship_type for ship_type in ShipTypes])
@pytest.mark.parametrize("dispatch_date", [None, datetime.now() + timedelta(days=3)])
@pytest.mark.parametrize("c4", [True, False])
def test_update_job(
    event_loop,
    *,
    client: LetterxpressClient,
    address: Optional[str],
    dispatch_date: Optional[datetime],
    color: ColorTypes,
    ship: ShipTypes,
    mode: PrintModes,
    c4: bool
) -> None:
    create_job_response = event_loop.run_until_complete(
        client.set_job(pdf="./tests/test.pdf")
    )
    response = event_loop.run_until_complete(
        client.update_job(
            id=create_job_response["letter"]["job_id"],
            address=address,
            dispatch_date=dispatch_date,
            color=color,
            ship=ship,
            mode=mode,
            c4=c4,
        )
    )

    assert response["status"] == 200
    assert response["letter"]["specification"]["color"] == color
    assert response["letter"]["specification"]["mode"] == mode
    assert response["letter"]["specification"]["ship"] == ship
