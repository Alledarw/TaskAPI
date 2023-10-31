from flask import Flask, request, render_template, jsonify
import json

app = Flask(__name__)


def get_task():
    with open("task.json") as data:
        return json.load(data)


# API documentation
@app.route("/", methods=["GET"])
def get_api_info():
    return render_template('index.html')


# GET
@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = get_task()
    return tasks


# GET {task_id}
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_single_task(task_id):
    tasks = get_task()
    # return tasks[0]
    for task in tasks:
        if task["id"] == task_id:
            return task

    return "task not found"


# POST (Not finished)
@app.route("/tasks", methods=["POST"])
def add_new_task():
    tasks = get_task()
    tasks.append({"category": request.json.get("category"), "description": request.json.get("description")})
    with open("task.json", "w") as data:
        json.dump(tasks, data)
    return {"msg": "Task added successfully!"}


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
        with open("task.json", "w") as data:
            json.dump(tasks, data)

        return jsonify({"msg": "Task deleted successfully!"})
    else:
        return "Task not found", 404


if __name__ == '__main__':
    app.run(debug=True)
