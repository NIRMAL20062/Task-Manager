from fastapi import FastAPI, HTTPException, Path, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Replace with your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for tasks
tasks = []

# Task model using Pydantic
class Task(BaseModel):
    name: str
    deadline: str  # Expected format: "YYYY-MM-DDTHH:MM"
    priority: str

# Basic authentication setup
security = HTTPBasic()
users = {"user1": "password1", "user2": "password2"}  # Replace with a database in production

# Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Virtual Personal Assistant!"}

# Add a new task
@app.post("/add-task")
def add_task(task: Task):
    try:
        # Parse the deadline into a datetime object
        deadline_dt = datetime.strptime(task.deadline, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use 'YYYY-MM-DDTHH:MM'."
        )

    # Convert the task to a dictionary and store it
    task_dict = task.dict()
    task_dict["deadline"] = deadline_dt.strftime("%Y-%m-%d %H:%M")  # Store formatted date
    tasks.append(task_dict)
    return {"message": "Task added successfully!", "task_id": len(tasks) - 1}

# Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# Update an existing task
@app.put("/update-task/{task_id}")
def update_task(task_id: int, updated_task: Task):
    # Check if the task ID is valid
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        # Parse the updated deadline
        deadline_dt = datetime.strptime(updated_task.deadline, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use 'YYYY-MM-DDTHH:MM'."
        )

    # Update the task
    tasks[task_id] = {
        "name": updated_task.name,
        "deadline": deadline_dt.strftime("%Y-%m-%d %H:%M"),
        "priority": updated_task.priority
    }
    return {"message": "Task updated successfully!"}

# Delete a task
@app.delete("/delete-task/{task_id}")
def delete_task(task_id: int):
    # Check if the task ID is valid
    if task_id < 0 or task_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")

    # Remove the task
    tasks.pop(task_id)
    return {"message": "Task deleted successfully!"}

# Login endpoint (Basic Authentication)
@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    # Check if the username and password are correct
    if users.get(credentials.username) != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"message": "Login successful!"}

# to run uvicorn main:app --reload