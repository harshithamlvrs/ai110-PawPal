#Generate tests smart action or Copilot Chat to draft two simple tests:
#Task Completion: Verify that calling mark_complete() actually changes the task's status.
#Task Addition: Verify that adding a task to a Pet increases that pet's task count.

import pytest
from datetime import datetime  # Added for fixed timestamps in new filter tests
from pawpal_system import Task, Pet, Owner, Scheduler, Recurrence, ConflictInfo  # Added Owner/Scheduler for integration-style filter tests

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


# Test filtering by pet name
def test_filter_tasks_by_pet_name():
    owner = Owner(name="Jordan")
    mochi = Pet(id=1, name="Mochi", breed="Dog", age=3)
    luna = Pet(id=2, name="Luna", breed="Cat", age=2)
    
    mochi_task = Task(id=1, description="Walk", start_time=datetime(2026, 3, 30, 8, 0), duration_mins=20)
    luna_task = Task(id=2, description="Groom", start_time=datetime(2026, 3, 30, 10, 0), duration_mins=25)
    
    mochi.add_task(mochi_task)
    luna.add_task(luna_task)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    
    scheduler = Scheduler(owner=owner)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    
    assert len(mochi_tasks) == 1
    assert mochi_tasks[0].description == "Walk"


# Test filtering by completion status
def test_filter_tasks_by_completion_status():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)
    
    done_task = Task(id=1, description="Morning walk", start_time=datetime(2026, 3, 30, 8, 0), duration_mins=30)
    pending_task = Task(id=2, description="Feed breakfast", start_time=datetime(2026, 3, 30, 9, 0), duration_mins=15)
    done_task.mark_complete()
    
    pet.add_task(done_task)
    pet.add_task(pending_task)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner=owner)
    completed = scheduler.filter_tasks(is_completed=True)
    incomplete = scheduler.filter_tasks(is_completed=False)
    
    assert len(completed) == 1
    assert completed[0].description == "Morning walk"
    assert len(incomplete) == 1
    assert incomplete[0].description == "Feed breakfast"


# Test conflict detection with overlap
def test_detect_conflicts_with_overlap():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)
    
    existing_task = Task(id=1, description="Breakfast", start_time=datetime(2026, 3, 30, 8, 0), duration_mins=15)
    overlapping_task = Task(id=2, description="Playtime", start_time=datetime(2026, 3, 30, 8, 10), duration_mins=20)
    
    pet.add_task(existing_task)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts(overlapping_task)
    
    assert len(conflicts) == 1
    assert conflicts[0].conflicting_pet_name == "Mochi"
    assert conflicts[0].conflicting_task_description == "Breakfast"


# Test no conflict when tasks don't overlap
def test_detect_no_conflicts():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)
    
    task1 = Task(id=1, description="Breakfast", start_time=datetime(2026, 3, 30, 8, 0), duration_mins=15)
    task2 = Task(id=2, description="Walk", start_time=datetime(2026, 3, 30, 9, 0), duration_mins=30)
    
    pet.add_task(task1)
    owner.add_pet(pet)
    
    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts(task2)
    
    assert len(conflicts) == 0
def test_filter_tasks_by_completion_status():
    owner = Owner(name="Jordan")  # Added owner+scheduler setup to exercise Scheduler.filter_tasks()
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)

    done_task = Task(id=1, description="Morning walk", start_time=datetime(2026, 3, 30, 8, 0), duration_mins=30)
    pending_task = Task(id=2, description="Feed breakfast", start_time=datetime(2026, 3, 30, 9, 0), duration_mins=15)
    done_task.mark_complete()  # Added explicit completion state for filter assertion

    pet.add_task(done_task)
    pet.add_task(pending_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    completed_tasks = scheduler.filter_tasks(is_completed=True)  # Added status-only filter case
    incomplete_tasks = scheduler.filter_tasks(is_completed=False)  # Added complementary status filter case

    assert completed_tasks == [done_task]
    assert incomplete_tasks == [pending_task]


# Added test: verifies filtering tasks by pet name.
def test_filter_tasks_by_pet_name():
    owner = Owner(name="Jordan")
    mochi = Pet(id=1, name="Mochi", breed="Dog", age=3)
    luna = Pet(id=2, name="Luna", breed="Cat", age=2)

    mochi_task = Task(id=1, description="Walk", start_time=datetime(2026, 3, 30, 8, 0), duration_mins=20)
    luna_task = Task(id=2, description="Groom", start_time=datetime(2026, 3, 30, 10, 0), duration_mins=25)

    mochi.add_task(mochi_task)
    luna.add_task(luna_task)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner=owner)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")  # Added pet-name filter case

    assert mochi_tasks == [mochi_task]


def test_mark_task_complete_creates_next_daily_task():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)
    daily_task = Task(
        id=1,
        description="Morning meds",
        start_time=datetime(2026, 3, 30, 8, 0),
        duration_mins=10,
        recurrence=Recurrence.DAILY,
    )
    pet.add_task(daily_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    updated = scheduler.mark_task_complete(task_id=1)

    assert updated is True
    assert daily_task.is_completed is True
    assert len(pet.tasks) == 2

    next_task = pet.tasks[1]
    assert next_task.description == daily_task.description
    assert next_task.recurrence == Recurrence.DAILY
    assert next_task.start_time == datetime(2026, 3, 31, 8, 0)
    assert next_task.id == 2


def test_mark_task_complete_creates_next_weekly_task():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Luna", breed="Cat", age=2)
    weekly_task = Task(
        id=4,
        description="Weight check",
        start_time=datetime(2026, 3, 30, 9, 30),
        duration_mins=15,
        recurrence=Recurrence.WEEKLY,
    )
    pet.add_task(weekly_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    updated = scheduler.mark_task_complete(task_id=4)

    assert updated is True
    assert len(pet.tasks) == 2
    assert pet.tasks[1].start_time == datetime(2026, 4, 6, 9, 30)
    assert pet.tasks[1].recurrence == Recurrence.WEEKLY


def test_mark_task_complete_once_does_not_create_new_task():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)
    one_time_task = Task(
        id=7,
        description="Grooming",
        start_time=datetime(2026, 3, 30, 11, 0),
        duration_mins=30,
        recurrence=Recurrence.ONCE,
    )
    pet.add_task(one_time_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    updated = scheduler.mark_task_complete(task_id=7)

    assert updated is True
    assert one_time_task.is_completed is True
    assert len(pet.tasks) == 1


# Added tests: lightweight conflict detection returns detailed warning info.
def test_detect_conflicts_single_overlap():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)

    existing_task = Task(
        id=1,
        description="Morning walk",
        start_time=datetime(2026, 3, 30, 8, 0),
        duration_mins=30,  # 8:00-8:30
    )
    new_task = Task(
        id=2,
        description="Breakfast",
        start_time=datetime(2026, 3, 30, 8, 15),  # 8:15-8:30
        duration_mins=15,
    )

    pet.add_task(existing_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    conflicts = scheduler.detect_conflicts(new_task)

    assert len(conflicts) == 1
    assert conflicts[0].conflicting_pet_name == "Mochi"
    assert conflicts[0].conflicting_task_description == "Morning walk"
    assert "Mochi" in conflicts[0].warning_message()
    assert "Morning walk" in conflicts[0].warning_message()


def test_detect_conflicts_multiple_pets():
    owner = Owner(name="Jordan")
    mochi = Pet(id=1, name="Mochi", breed="Dog", age=3)
    luna = Pet(id=2, name="Luna", breed="Cat", age=2)

    mochi_task = Task(
        id=1,
        description="Mochi walk",
        start_time=datetime(2026, 3, 30, 9, 0),
        duration_mins=20,
    )
    luna_task = Task(
        id=2,
        description="Luna grooming",
        start_time=datetime(2026, 3, 30, 9, 10),
        duration_mins=30,
    )

    mochi.add_task(mochi_task)
    luna.add_task(luna_task)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(owner=owner)

    new_task = Task(
        id=3,
        description="Owner break",
        start_time=datetime(2026, 3, 30, 9, 15),  # Overlaps both
        duration_mins=15,
    )

    conflicts = scheduler.detect_conflicts(new_task)

    # Should detect conflicts with both pets' tasks.
    assert len(conflicts) == 2
    conflict_pets = {c.conflicting_pet_name for c in conflicts}
    assert conflict_pets == {"Mochi", "Luna"}


def test_detect_conflicts_no_overlap():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)

    existing_task = Task(
        id=1,
        description="Walk",
        start_time=datetime(2026, 3, 30, 8, 0),
        duration_mins=30,
    )
    new_task = Task(
        id=2,
        description="Feed",
        start_time=datetime(2026, 3, 30, 9, 0),  # Starts after walk ends
        duration_mins=15,
    )

    pet.add_task(existing_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    conflicts = scheduler.detect_conflicts(new_task)

    assert len(conflicts) == 0


def test_detect_conflicts_ignores_completed_tasks():
    owner = Owner(name="Jordan")
    pet = Pet(id=1, name="Mochi", breed="Dog", age=3)

    completed_task = Task(
        id=1,
        description="Old walk",
        start_time=datetime(2026, 3, 30, 8, 0),
        duration_mins=30,
    )
    completed_task.mark_complete()

    new_task = Task(
        id=2,
        description="New walk",
        start_time=datetime(2026, 3, 30, 8, 15),  # Would overlap if not completed
        duration_mins=15,
    )

    pet.add_task(completed_task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    # Completed tasks should be ignored in conflict detection.
    conflicts = scheduler.detect_conflicts(new_task)

    assert len(conflicts) == 0

