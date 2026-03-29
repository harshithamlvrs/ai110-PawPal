#Generate tests smart action or Copilot Chat to draft two simple tests:
#Task Completion: Verify that calling mark_complete() actually changes the task's status.
#Task Addition: Verify that adding a task to a Pet increases that pet's task count.

import pytest
from pawpal_system import Task, Pet

def test_mark_complete():
    task = Task(id=1, description="Test Task", start_time=None, duration_mins=30)
    assert not task.is_completed  # Initially should be False
    task.mark_complete()
    assert task.is_completed  # After marking complete, should be True

def test_add_task_to_pet():
    pet = Pet(id=1, name="Test Pet", breed="Test Breed", age=5)
    initial_task_count = len(pet.tasks)
    new_task = Task(id=2, description="New Task", start_time=None, duration_mins=15)
    pet.add_task(new_task)
    assert len(pet.tasks) == initial_task_count + 1  # Task count should increase by 1

#let owner modify a task's description and verify the change
def test_modify_task_description():
    task = Task(id=3, description="Old Description", start_time=None, duration_mins=20)
    new_description = "Updated Description"
    task.description = new_description  # Modify the description
    assert task.description == new_description  # Verify the change

