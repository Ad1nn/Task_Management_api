from fastapi.testclient import TestClient


class TestHealthEndpoints:
    def test_root(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to Task Management API"}

    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestCreateTask:
    def test_create_task_success(self, client: TestClient):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "high",
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_minimal(self, client: TestClient):
        task_data = {"title": "Minimal Task"}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["status"] == "pending"
        assert data["priority"] == "medium"

    def test_create_task_with_status(self, client: TestClient):
        task_data = {
            "title": "In Progress Task",
            "status": "in_progress",
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        assert response.json()["status"] == "in_progress"

    def test_create_task_empty_title_fails(self, client: TestClient):
        task_data = {"title": ""}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422

    def test_create_task_missing_title_fails(self, client: TestClient):
        task_data = {"description": "No title provided"}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422

    def test_create_task_invalid_status_fails(self, client: TestClient):
        task_data = {"title": "Test", "status": "invalid_status"}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422

    def test_create_task_invalid_priority_fails(self, client: TestClient):
        task_data = {"title": "Test", "priority": "invalid_priority"}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422


class TestReadTasks:
    def test_get_tasks_empty(self, client: TestClient):
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tasks_returns_all(self, client: TestClient):
        # Create tasks
        client.post("/tasks", json={"title": "Task 1"})
        client.post("/tasks", json={"title": "Task 2"})
        client.post("/tasks", json={"title": "Task 3"})

        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_tasks_filter_by_status(self, client: TestClient):
        client.post("/tasks", json={"title": "Pending", "status": "pending"})
        client.post("/tasks", json={"title": "In Progress", "status": "in_progress"})
        client.post("/tasks", json={"title": "Completed", "status": "completed"})

        response = client.get("/tasks?status=in_progress")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "in_progress"

    def test_get_tasks_filter_by_priority(self, client: TestClient):
        client.post("/tasks", json={"title": "Low", "priority": "low"})
        client.post("/tasks", json={"title": "High", "priority": "high"})
        client.post("/tasks", json={"title": "High 2", "priority": "high"})

        response = client.get("/tasks?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(t["priority"] == "high" for t in data)

    def test_get_tasks_pagination_skip(self, client: TestClient):
        for i in range(5):
            client.post("/tasks", json={"title": f"Task {i}"})

        response = client.get("/tasks?skip=2")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_get_tasks_pagination_limit(self, client: TestClient):
        for i in range(5):
            client.post("/tasks", json={"title": f"Task {i}"})

        response = client.get("/tasks?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_tasks_pagination_skip_and_limit(self, client: TestClient):
        for i in range(10):
            client.post("/tasks", json={"title": f"Task {i}"})

        response = client.get("/tasks?skip=3&limit=4")
        assert response.status_code == 200
        assert len(response.json()) == 4

    def test_get_task_by_id_success(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "Single Task"})
        task_id = create_response.json()["id"]

        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Single Task"

    def test_get_task_by_id_not_found(self, client: TestClient):
        response = client.get("/tasks/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestUpdateTask:
    def test_update_task_title(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "Original"})
        task_id = create_response.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    def test_update_task_status(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"status": "completed"})
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_update_task_priority(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"priority": "high"})
        assert response.status_code == 200
        assert response.json()["priority"] == "high"

    def test_update_task_multiple_fields(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        update_data = {
            "title": "Updated Task",
            "description": "New description",
            "status": "in_progress",
            "priority": "low",
        }
        response = client.put(f"/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "New description"
        assert data["status"] == "in_progress"
        assert data["priority"] == "low"

    def test_update_task_updated_at_changes(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]

        response = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
        new_updated_at = response.json()["updated_at"]
        assert new_updated_at != original_updated_at

    def test_update_task_not_found(self, client: TestClient):
        response = client.put("/tasks/999", json={"title": "Updated"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_update_task_invalid_status(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.put(f"/tasks/{task_id}", json={"status": "invalid"})
        assert response.status_code == 422


class TestDeleteTask:
    def test_delete_task_success(self, client: TestClient):
        create_response = client.post("/tasks", json={"title": "To Delete"})
        task_id = create_response.json()["id"]

        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204

        # Verify task is deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient):
        response = client.delete("/tasks/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_delete_task_removes_from_list(self, client: TestClient):
        client.post("/tasks", json={"title": "Task 1"})
        create_response = client.post("/tasks", json={"title": "Task 2"})
        task_id = create_response.json()["id"]
        client.post("/tasks", json={"title": "Task 3"})

        # Verify 3 tasks exist
        assert len(client.get("/tasks").json()) == 3

        # Delete one task
        client.delete(f"/tasks/{task_id}")

        # Verify 2 tasks remain
        tasks = client.get("/tasks").json()
        assert len(tasks) == 2
        assert all(t["id"] != task_id for t in tasks)
