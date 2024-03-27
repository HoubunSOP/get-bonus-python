import re
import asyncio


def remove_extra_spaces(text=''):
    return re.sub(r'[ \t]+', ' ', text).strip()


async def retry_fn(fn, options):
    retry = options['retry']
    delay = options.get('delay', 1000)

    last_error = None
    for _ in range(retry):
        try:
            result = await fn()
            return result
        except Exception as error:
            last_error = error
            await sleep(delay)

    raise last_error


def sleep(timeout):
    return asyncio.sleep(timeout / 1000)
