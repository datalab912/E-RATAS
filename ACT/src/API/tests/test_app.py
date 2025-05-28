import pytest
from werkzeug.datastructures import FileStorage
from API.app import app, allowed_file
from ACT.tests.mock import SAMPLE_FILEPATH


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_allowed_file():
    # Test for allowed file extensions
    assert allowed_file("test.txt") is True
    assert allowed_file("test.pdf") is True


def test_upload_file(client):
    # Test file upload functionality
    file = FileStorage(stream=open(SAMPLE_FILEPATH, "rb"), filename="test.pdf")
    response = client.post("/build-act", data={"file": file})
    assert response.status_code == 200
    assert b"ACKNOWLEDGEMENT" in response.data
