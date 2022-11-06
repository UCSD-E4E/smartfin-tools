import base64

import pytest

@pytest.fixture
def samplePatternData():
    data = bytearray()
    for i in range(512):
        data.append(i % 256)
    return bytes(data)

