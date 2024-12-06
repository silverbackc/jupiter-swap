import logging
import json
from aiohttp import ClientResponse, ClientSession, ClientTimeout
from typing import Any, Optional, Dict

HTTP_REQUEST_TIMEOUT = 10
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RequestException(Exception):
    message = "Request failed"


class BaseHTTPClient:
    def __init__(self):
        pass

    async def _get(
        self,
        url: str,
        headers: Optional[Dict] = None,
        timeout: int = HTTP_REQUEST_TIMEOUT,
        debug: bool = False,
        response_type: str = "json",
    ) -> Any:
        try:
            headers = headers or {}
            async with ClientSession(headers=headers, timeout=ClientTimeout(total=timeout)) as session:
                async with session.get(url, ssl=False) as resp:
                    if debug:
                        log.info(f"Response status for {url} : {resp.status}")
                    if resp.status > 299:
                        log.warning(
                            f"GET request failed for {url} with status code: {resp.status}. Response text: {await resp.text(encoding='utf-8')}"
                        )
                    return await _parse_response(resp, response_type)
        except Exception as e:
            raise e

    async def _post(
        self,
        url: str,
        data: Any,
        headers: Optional[Dict] = None,
        timeout: int = HTTP_REQUEST_TIMEOUT,
        debug: bool = False,
        response_type: str = "json",
    ) -> Any:
        try:
            headers = headers or {}
            async with ClientSession(headers=headers, timeout=ClientTimeout(total=timeout)) as session:
                async with session.post(url=url, json=data, ssl=False) as resp:
                    if debug:
                        log.info(f"Response status for {url} : {resp.status}")
                    if resp.status > 299:
                        log.warning(
                            f"POST request failed for {url} with status code: {resp.status}. Response text: {await resp.text(encoding='utf-8')}"
                        )
                    return await _parse_response(resp, response_type)
        except Exception as e:
            raise e

async def _parse_response(
    response: ClientResponse,
    response_type,
):
    if response_type == "json":
        try:
            resp = await response.json()
            if isinstance(resp, str):
                return json.loads(resp)
            else:
                return resp
        except json.JSONDecodeError as e:
            raise RequestException() from e
    elif response_type == "response_object":
        return response
    return await response.text()
