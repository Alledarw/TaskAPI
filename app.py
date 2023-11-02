from flask import Flask, request, render_template, jsonify
import json
from numpy.core.defchararray import capitalize

app = Flask(__name__)


def get_task():
    with open("tasks.json") as data:
        return json.load(data)


# API documentation
@app.route("/", methods=["GET"])
def get_api_info():
    return render_template('index.html')


# GET {tasks}
@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = get_task()
    return tasks


# GET {task_id}
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_single_task(task_id):
    tasks = get_task()
    for task in tasks:
        if task["id"] == task_id:
            return task

    return jsonify({"msg": "task not found"})


# GET {categories}
@app.route("/categories", methods=["GET"])
def get_all_categories():
    tasks = get_task()
    categories = []
    for task in tasks:
        categories.append(task["category"])

    return jsonify(categories)

# GET {categories/category}
@app.route("/categories/<category>", methods=["GET"])
def get_category(category):
    found_categories = []
    # Browser automatically turn words into lower capital strings
    Uppercase_category = capitalize(category)
    tasks = get_task()
    for task in tasks:
        # For developement testing
        print(task)
        print(task["category"])
        print(category)
        if task["category"] == Uppercase_category:
            found_categories.append(task)

    return jsonify(found_categories)


# POST
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


# PUT /tasks/{task_id} Uppdaterar en task med ett specifikt id.

# PUT /tasks/{task_id}/complete Markerar en task som färdig.

# GET /tasks/categories/{category_name} Hämtar alla tasks från en specifik kategori.


if __name__ == '__main__':
    app.run(debug=True)
