import asyncio
import inspect
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test to run with asyncio")

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        marker = pyfuncitem.get_closest_marker("asyncio")
        if marker is not None:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                loop.run_until_complete(pyfuncitem.obj(**pyfuncitem.funcargs))
            finally:
                asyncio.set_event_loop(None)
                loop.close()
            return True
