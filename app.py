from flask import Flask, request, render_template, jsonify
import json
from numpy.core.defchararray import capitalize

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
    def wrapper(*args, **kwargs):
        provided_secret_key = request.headers.get("X-Secret-Key")
        if provided_secret_key != SECRET_KEY:
            return jsonify({"error": "Unauthorized"}), 401
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

    return jsonify({"error": "Task not found"}), 404


@app.route("/search", methods=["GET"])
def search_task_by_id():
    task_id = request.args.get("task_id")
    if task_id:
        tasks = get_task()
        for task in tasks:
            if task["id"] == int(task_id):
                return render_template('index.html', tasks=[task])
    return render_template('index.html', error="Task not found")


# GET {categories}
@app.route("/categories", methods=["GET"])
def get_all_categories():
    tasks = get_task()
    categories = []
    for task in tasks:
        # Check if the category exist, preventing duplicate categories
        category = task["category"]
        if category not in categories:
            categories.append(category)

    return render_template('index.html', categories=categories)


# GET {categories/category}
@app.route("/categories/<category>", methods=["GET"])
def get_category(category):
    found_categories = []
    # Browser automatically turn words into lower capital strings
    Uppercase_category = capitalize(category)
    tasks = get_task()
    for task in tasks:
        # For development testing
        print(task)
        print(task["category"])
        print(category)
        if task["category"] == Uppercase_category:
            found_categories.append(task)

    if found_categories:
        return jsonify(found_categories)
    else:
        return jsonify({"error": "Category not found"}), 404


# POST new task
@app.route("/tasks", methods=["POST"])
def add_new_task():
    tasks = get_task()
    tasks.append({"id": request.json.get("id"),
                  "description": request.json.get("description"),
                  "category": request.json.get("category"),
                  "status": request.json.get("status")})
    with open("tasks.json", "w") as data:
        json.dump(tasks, data)
    return jsonify({"msg": "Task added successfully!"})


# DELETE {task_id}
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@require_secret_key
def delete_task(task_id):
    tasks = get_task()

    # Check if the task with the specified task_id exists
    task_to_remove = None
    for task in tasks:
        if task["id"] == task_id:
            task_to_remove = task
            break

    if task_to_remove is not None:
        tasks.remove(task_to_remove)

        # Update the JSON file with the modified task list
        with open("tasks.json", "w") as data:
            json.dump(tasks, data)

        return jsonify({"msg": "Task deleted successfully!"})
    else:
        return "Task not found", 404


# PUT /tasks/{task_id}
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    tasks = get_task()

    for task in tasks:
        if task["id"] == task_id:
            task["id"] = request.json.get("id")
            task["description"] = request.json.get("description")
            task["category"] = request.json.get("category")
            task["status"] = request.json.get("status")
            with open("tasks.json", "w") as data:
                json.dump(tasks, data)

            return jsonify({"msg": "updated task successfully!"})


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


# GET add new task via frontend
@app.route("/add", methods=["GET"])
def get_page():
    return render_template("post_task.html")


# POST adding the task after form submit
@app.route("/submit", methods=["POST"])
def submit():
    # Get data from the form using request.form
    id = request.form["id"]
    description = request.form["description"]
    category = request.form["category"]
    status = request.form["status"]

    # Create a Python dictionary with the form data
    task_data = {
        "id": id,
        "description": description,
        "category": category,
        "status": status
    }

    # development testing
    print(task_data)

    tasks = get_task()
    tasks.append(task_data)

    with open("tasks.json", "w") as data:
        json.dump(tasks, data)

    return jsonify({"msg": "Task added!"})

# LEFT TO DO---------------------------------------
# Error messages for each endpoint
# flask testing


if __name__ == '__main__':
    app.run(debug=True)
