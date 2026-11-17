import logging
import os
import time

from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

load_dotenv(override=True)
log = logging.getLogger(__name__)
_client = None


def complete(messages: list[dict], max_retries: int = 4) -> str:
    global _client
    base_url = os.environ["LLM_BASE_URL"]
    if not base_url.startswith(("http://", "https://")):
        raise RuntimeError(f"LLM_BASE_URL must start with http(s)://, got {base_url!r}")
    if _client is None:
        _client = OpenAI(
            base_url=os.environ["LLM_BASE_URL"],
            api_key=os.environ["LLM_API_KEY"],
            timeout=60,
        )
    model = os.environ["LLM_MODEL"]

    for attempt in range(max_retries + 1):
        try:
            start = time.time()
            resp = _client.chat.completions.create(
                model=model, messages=messages, temperature=0
            )
            usage = resp.usage
            log.info(
                "llm ok requested=%s answered=%s latency=%.1fs tokens=%s",
                model, resp.model, time.time() - start, usage.total_tokens if usage else "?",
            )
            return resp.choices[0].message.content or ""
        except (RateLimitError, APIConnectionError, APITimeoutError) as e:
            wait = 2 * 2 ** attempt
            log.warning("llm error (%s); retry %d in %ds", type(e).__name__, attempt + 1, wait)
            time.sleep(wait)
    raise RuntimeError("LLM call failed after retries")