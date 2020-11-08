# aioletterxpress
asyncio client for letterxpress.de api

## Install

```bash
pip install aioletterxpress
```

## How to use
```python
import asyncio
from aioletterxpress.client import LetterxpressClient

client = LetterxpressClient()  # this will use the env variables LXP_USERNAME, LXP_API_KEY, LXP_BASE_URL

client = LetterxpressClient(
    username="YOUR_USERNAME",
    apikey="YOUR_API_KEY",
    base_url="https://api.letterxpress.de/v1/"  # by default the sandbox is used https://sandbox.letterxpress.de/v1/
)

async def main():
    balance = await client.get_balance()
    print(balance)
    
    jobs = await asyncio.gather(*[client.set_job(pdf="./tests/test.pdf") for _ in range(5)])

    for job in jobs:
        print(job["letter"]["job_id"])

asyncio.run(main())
```
