import base64
import hashlib
import io
import os
from datetime import datetime
from typing import Any, Dict, Optional, Union

import aiofiles
import httpx

from .enums import ColorTypes, PrintModes, ShipTypes, JobStatus


class LetterxpressClient:
    def __init__(
        self,
        username: str = os.environ.get("LXP_USERNAME", None),
        apikey: str = os.environ.get("LXP_API_KEY", None),
        base_url: str = os.environ.get(
            "LXP_BASE_URL", "https://sandbox.letterxpress.de/v1/"
        ),
    ) -> None:
        self.base_url = base_url
        self.username = username
        self.apikey = apikey

    async def _request(
        self,
        *,
        method: str = "GET",
        endpoint: str,
        json: Optional[Dict[str, Any]] = {},
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                url=f"{self.base_url}{endpoint}",
                method=method,
                json={
                    **json,
                    "auth": {"username": self.username, "apikey": self.apikey},
                },
            )

            if raw_response:
                return response

            return response.json()

    async def _encode_file(self, file: str) -> str:
        async with aiofiles.open(file, "rb") as file:
            content = await file.read()

        return base64.b64encode(content)

    def _get_checksum(self, base64_file: str) -> str:
        md5 = hashlib.md5()
        md5.update(base64_file)
        return md5.hexdigest()

    async def get_balance(self) -> Dict[str, Any]:
        """
        Get the current balance
        """
        return await self._request(endpoint="getBalance")

    async def get_price(
        self,
        *,
        pdf: str,
        address: Optional[str] = None,
        dispatch_date: Optional[datetime] = None,
        page: int = 1,
        color: ColorTypes = ColorTypes.BLACK,
        mode: PrintModes = PrintModes.SIMPLEX,
        ship: ShipTypes = ShipTypes.NATIONAL,
        c4: bool = False,
    ) -> Dict[str, Any]:
        """
        Gets the price for a letter
        """
        encoded_content = await self._encode_file(pdf)
        checksum = self._get_checksum(encoded_content)

        job = await self._request(
            method="POST",
            endpoint="getPrice",
            json={
                "letter": {
                    "base64_file": encoded_content.decode("utf-8"),
                    "base64_checksum": checksum,
                    "address": address,
                    "dispatchdate": dispatch_date,
                    "specification": {
                        "page": page,
                        "color": color,
                        "mode": mode,
                        "ship": ship,
                        "c4": "y" if c4 else "n",
                    },
                }
            },
        )
        return job

    async def get_jobs(
        self, job_status: JobStatus = JobStatus.QUEUE, days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Gets all jobs with a specific status
        """
        endpoint = f"getJobs/{job_status}"

        if days:
            endpoint += f"/{days}"

        return await self._request(endpoint=endpoint)

    async def get_job(self, id: int) -> Dict[str, Any]:
        """
        Get a job by id
        """
        return await self._request(endpoint=f"getJob/{id}")

    async def set_job(
        self,
        *,
        pdf: str,
        address: Optional[str] = None,
        dispatch_date: Optional[datetime] = None,
        page: int = 1,
        color: ColorTypes = ColorTypes.BLACK,
        mode: PrintModes = PrintModes.SIMPLEX,
        ship: ShipTypes = ShipTypes.NATIONAL,
        c4: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a job
        """
        encoded_content = await self._encode_file(pdf)
        checksum = self._get_checksum(encoded_content)

        job = await self._request(
            method="POST",
            endpoint="setJob",
            json={
                "letter": {
                    "base64_file": encoded_content.decode("utf-8"),
                    "base64_checksum": checksum,
                    "address": address,
                    "dispatchdate": dispatch_date.strftime("%d.%m.%Y")
                    if dispatch_date
                    else None,
                    "specification": {
                        "page": page,
                        "color": color,
                        "mode": mode,
                        "ship": ship,
                        "c4": "y" if c4 else "n",
                    },
                }
            },
        )
        return job

    async def update_job(
        self,
        *,
        id: int,
        address: Optional[str] = None,
        dispatch_date: Optional[datetime] = None,
        page: int = 1,
        color: ColorTypes = ColorTypes.BLACK,
        mode: PrintModes = PrintModes.SIMPLEX,
        ship: ShipTypes = ShipTypes.NATIONAL,
        c4: bool = False,
    ) -> Dict[str, Any]:
        """
        Updates a job by id
        """
        job = await self._request(
            method="PUT",
            endpoint=f"updateJob/{id}",
            json={
                "letter": {
                    "address": address,
                    "dispatchdate": dispatch_date.strftime("%d.%m.%Y")
                    if dispatch_date
                    else None,
                    "specification": {
                        "page": page,
                        "color": color,
                        "mode": mode,
                        "ship": ship,
                        "c4": "y" if c4 else "n",
                    },
                }
            },
        )
        return job

    async def delete_job(self, id: int) -> Dict[str, Any]:
        """
        Deletes a job by id
        """
        job = await self._request(method="DELETE", endpoint=f"deleteJob/{id}")
        return job

    async def list_invoices(self) -> Dict[str, Any]:
        """
        Lists all invoices
        """
        invoices = await self._request(endpoint="listInvoices")
        return invoices

    async def get_invoice(self, id: int, path: str) -> Dict[str, Any]:
        """
        Downloads an invoice PDF by id
        """
        response = await self._request(endpoint=f"getInvoice/{id}", raw_response=True)

        full_path = os.path.join(path, f"invoice_{id}.pdf")

        async with aiofiles.open(full_path, "wb") as file:
            await file.write(response.content)

        return full_path
