import json
import pytest
from app import app


# Run via pytest test_app.py in terminal
# Run after app.py is started on the localhost

# Define a test client for our app
@pytest.fixture
def client():
    # Configure the Flask app in testing mode
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Test the homepage route
def test_get_homepage(client):
    response = client.get('/')
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200


# Test the route to get all tasks
def test_get_all_tasks(client):
    response = client.get('/tasks')
    assert response.status_code == 200


# Test the route to get a single task by ID
def test_get_single_task(client):
    response = client.get('/tasks/1')
    assert response.status_code == 200


# Test the route to get a single task by ID when the task is not found
def test_get_single_task_not_found(client):
    response = client.get('/tasks/999')
    # Assert that the response status code is 404 (Not Found)
    assert response.status_code == 404


# Test adding a new task
def test_add_new_task(client):
    task_data = {
        "id": 5,
        "description": "New Task",
        "category": "Test",
        "status": "Incomplete"
    }
    response = client.post('/tasks', json=task_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    # Assert that the response message indicates success
    assert data["msg"] == "Task added successfully!"


# Test deleting a task
def test_delete_task(client):
    response = client.delete('/tasks/1', headers={"X-Secret-Key": "Testkey"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["msg"] == "Task deleted successfully!"


# Test deleting a task that is not found
def test_delete_task_not_found(client):
    response = client.delete('/tasks/999', headers={"X-Secret-Key": "Testkey"})
    assert response.status_code == 404


# Test updating a task
def test_update_task(client):
    task_data = {
        "id": 1,
        "description": "Updated Task",
        "category": "Test",
        "status": "Complete"
    }
    response = client.put('/tasks/1', json=task_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["msg"] == "Task updated successfully!"


# Test changing the status of a task to complete
def test_change_status(client):
    response = client.put('/tasks/1/complete')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["msg"] == "Status changed successfully!"


# Test the route to get the page for adding a new task via the frontend
def test_get_page(client):
    response = client.get('/add')
    assert response.status_code == 200


# Test submitting a new task via the frontend
def test_submit_task(client):
    task_data = {
        "id": 6,
        "description": "Submitted Task",
        "category": "Test",
        "status": "Incomplete"
    }
    response = client.post('/submit', data=task_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["msg"] == "Task added successfully!"


# Test changing the status of a task to incomplete
def test_change_status_incomplete(client):
    response = client.put('/tasks/1/incomplete')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["msg"] == "Status changed successfully!"


if __name__ == '__main__':
    pytest.main()
