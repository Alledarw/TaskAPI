from flask import Flask, request, render_template, jsonify, abort
import json
from numpy.core.defchararray import capitalize
from functools import wraps

app = Flask(__name__)


def get_task():
    try:
        with open("tasks.json") as data:
            return json.load(data)
    except FileNotFoundError:
        return []


# For using DELETE
SECRET_KEY = "Testkey"


# Custom decorator to check the secret key
def require_secret_key(func):
    @wraps(func)  # Preserve metadata of the original function
    def wrapper(*args, **kwargs):
        provided_secret_key = request.headers.get("X-Secret-Key")
        if provided_secret_key != SECRET_KEY:
            abort(401, "Unauthorized")
        return func(*args, **kwargs)

    return wrapper


# API documentation
@app.route("/docs", methods=["GET"])
def get_api_info():
    return render_template('docs.html')


# GET homepage
@app.route("/", methods=["GET"])
def get_homepage():
    return render_template('index.html')


# GET {tasks}
@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = get_task()
    return render_template('index.html', tasks=tasks)


# GET {task_id}
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_single_task(task_id):
    tasks = get_task()
    for task in tasks:
        if task["id"] == task_id:
            return task
    abort(404, "Task not found")


@app.route("/search", methods=["GET"])
def search_task_by_id():
    task_id = request.args.get("task_id")
    if task_id:
        tasks = get_task()
        for task in tasks:
            if task["id"] == int(task_id):
                return render_template('index.html', tasks=[task])
    abort(404, "Task not found")


# GET {categories}
@app.route("/categories", methods=["GET"])
def get_all_categories():
    tasks = get_task()
    categories = []
    for task in tasks:
        # Check if the category exists, preventing duplicate categories
        category = task["category"]
        if category not in categories:
            categories.append(category)
    return render_template('index.html', categories=categories)


# GET {categories/category}
@app.route("/categories/<category>", methods=["GET"])
def get_category(category):
    found_categories = []
    # Browser automatically turns words into lowercase strings
    uppercase_category = capitalize(category)
    tasks = get_task()
    for task in tasks:
        if task["category"] == uppercase_category:
            found_categories.append(task)
    if found_categories:
        return jsonify(found_categories)
    abort(404, "Category not found")


# POST new task
@app.route("/tasks", methods=["POST"])
def add_new_task():
    # Check if the required fields are present in the JSON data
    required_fields = ["id", "description", "category", "status"]
    if not all(field in request.json for field in required_fields):
        return jsonify({"error": "Incomplete data. Please provide all required fields."}), 400

    # Extract data from the JSON request and make sure that the id is an int
    id_str = request.json.get("id")

    try:
        id = int(id_str)
    except ValueError:
        return jsonify({"error": "Invalid 'id' value. Please provide a valid integer."}), 400

    description = request.json.get("description")
    category = request.json.get("category")
    status = request.json.get("status")

    # Validate the data
    if not id or not description or not category or not status:
        return jsonify({"error": "Invalid data. Please provide valid values for all fields."}), 400

    new_task = {
        "id": id,
        "description": description,
        "category": category,
        "status": status
    }

    tasks = get_task()
    tasks.append(new_task)

    with open("tasks.json", "w") as data:
        json.dump(tasks, data)

    return jsonify({"msg": "Task added successfully!"})


# DELETE {task_id}
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@require_secret_key
def delete_task(task_id):
    tasks = get_task()
    task_to_remove = next((task for task in tasks if task["id"] == task_id), None)
    if task_to_remove is not None:
        tasks.remove(task_to_remove)
        with open("tasks.json", "w") as data:
            json.dump(tasks, data)
        return jsonify({"msg": "Task deleted successfully!"})
    abort(404, "Task not found")


# PUT /tasks/{task_id}
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    tasks = get_task()
    for task in tasks:
        if task["id"] == task_id:
            if "id" in request.json:
                task["id"] = request.json["id"]
            if "description" in request.json:
                task["description"] = request.json["description"]
            if "category" in request.json:
                task["category"] = request.json["category"]
            if "status" in request.json:
                task["status"] = request.json["status"]

            with open("tasks.json", "w") as data:
                json.dump(tasks, data)
            return jsonify({"msg": "Task updated successfully!"})
    abort(404, "Task not found")


# PUT complete
@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def change_status(task_id):
    tasks = get_task()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "complete"
            with open("tasks.json", "w") as data:
                json.dump(tasks, data)
            return jsonify({"msg": "Status changed successfully!"})
    abort(404, "Task not found")


# GET add new task via frontend
@app.route("/add", methods=["GET"])
def get_page():
    return render_template("post_task.html")


# POST adding the task after form submit
@app.route("/submit", methods=["POST"])
def submit():
    # Check if the required fields are present in the form data
    if "id" not in request.form or "description" not in request.form or "category" not in request.form or "status" not in request.form:
        return jsonify({"error": "Incomplete data. Please provide all required fields."}), 400

    # Extract data from the index.html form and make sure that the id is an int
    id_str = request.form["id"]

    try:
        id = int(id_str)
    except ValueError:
        return jsonify({"error": "Invalid 'id' value. Please provide a valid integer."}), 400

    description = request.form["description"]
    category = request.form["category"]
    status = request.form["status"]

    # validate data
    if not id or not description or not category or not status:
        return jsonify({"error": "Invalid data. Please provide valid values for all fields."}), 400

    # Create a Python dictionary with the form data
    task_data = {
        "id": id,
        "description": description,
        "category": category,
        "status": status
    }

    tasks = get_task()
    tasks.append(task_data)

    with open("tasks.json", "w") as data:
        json.dump(tasks, data)

    return jsonify({"msg": "Task added successfully!"})


# PUT /tasks/{task_id}
@app.route("/tasks/<int:task_id>/incomplete", methods=["PUT"])
def change_status_incomplete(task_id):
    tasks = get_task()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "incomplete"
            with open("tasks.json", "w") as data:
                json.dump(tasks, data)
            return jsonify({"msg": "Status changed successfully!"})
    abort(404, "Task not found")


# PUT  add new value in task {important}
@app.route("/tasks/<int:task_id>/important", methods=["PUT"])
def set_important(task_id):
    tasks = get_task()
    for task in tasks:
        if task["id"] == task_id:
            # Check if only one key is provided in the JSON data
            if len(request.json) != 1:
                return jsonify({"error": "Only one key is allowed in the request."}), 400

            # Check if the key is "value"
            if "value" not in request.json:
                return jsonify({"error": "The 'value' key is required."}), 400

            # Update the task's "value" key
            task["value"] = request.json["value"]

            with open("tasks.json", "w") as data:
                json.dump(tasks, data)

            return jsonify({"msg": "Value added successfully!"})

        return jsonify({"error": "Task not found."}), 404


# DELETE all tasks
@app.route("/tasks/delete-all", methods=["DELETE"])
@require_secret_key
def delete_all_tasks():
    tasks = []
    with open("tasks.json", "w") as data:
        json.dump(tasks, data)
    return jsonify({"msg": "All tasks deleted successfully!"})


# GET completed tasks in a specific category
@app.route("/completed-tasks/<category>", methods=["GET"])
def get_completed_tasks_in_category(category):
    tasks = get_task()
    completed_tasks = []

    for task in tasks:
        if task["category"] == category and task["status"] == "complete":
            completed_tasks.append(task)

    if not completed_tasks:
        abort(404, "No completed tasks found in the specified category.")

    return jsonify(completed_tasks)


if __name__ == '__main__':
    app.run(debug=True)
