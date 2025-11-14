import os
import pathlib

os.environ["GMDB_DATABASE_URL"] = "sqlite:///./test_gmdb.db"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _get_auth_headers(client: TestClient, username: str, password: str) -> dict[str, str]:

    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_full_workflow():

    with TestClient(app) as client:
        headers = _get_auth_headers(client, "admin", "ChangeMe123!")

        # Create a new user
        response = client.post(
            "/api/users",
            json={"username": "operator1", "password": "SecurePass123", "role": "operator"},
            headers=headers,
        )
        assert response.status_code == 200

        # Create a sensitive field configuration
        response = client.post(
            "/api/fields/sensitive",
            json={
                "field_id": "SF001",
                "table_name": "patient_info",
                "field_name": "patient_id_plain",
                "algorithm_type": "SM4",
                "status": "未加密",
                "allow_plain_text_read": False,
            },
            headers=headers,
        )
        assert response.status_code == 200

        # Create a migration task
        response = client.post(
            "/api/migration/tasks",
            json={
                "task_id": "TASK001",
                "table_name": "patient_info",
                "field_name": "patient_id_plain",
                "batch_size": 500,
                "concurrency": 2,
                "overwrite_plaintext": True,
            },
            headers=headers,
        )
        assert response.status_code == 200

        # Retrieve monitor status snapshot
        response = client.get("/api/monitor/status", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert "service" in body and "key" in body




def teardown_module(module):
    db_path = pathlib.Path("test_gmdb.db")
    if db_path.exists():
        db_path.unlink()
