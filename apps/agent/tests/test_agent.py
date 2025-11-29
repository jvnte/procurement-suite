import io

from fastapi.testclient import TestClient

from agent_api.shell import build_app


def test_post_agent_intake_gives_200():
    # given an app
    app = build_app()

    # when we upload a PDF file
    pdf_content = b"%PDF-1.4\n%fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}

    with TestClient(app) as client:
        response = client.post("/agent/intake", files=files)

        # then we get a 200 OK response
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert data["content_type"] == "application/pdf"
        assert data["size"] == len(pdf_content)
        assert "message" in data
