from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class Recurrence(str, Enum):
	"""Enumerates supported recurrence patterns for tasks."""

	ONCE = "once"
	DAILY = "daily"
	WEEKLY = "weekly"


class Owner:
	"""Represents the pet owner."""

	def __init__(self, name: str = "") -> None:
		self.name = name
		self.pets: List[Pet] = []

	def enter_name(self, name: str) -> None:
		"""Update the owner's name."""
		self.name = name

	def add_pet(self, pet: "Pet") -> None:
		"""Associate a pet with this owner."""
		if any(existing_pet.id == pet.id for existing_pet in self.pets):
			raise ValueError(f"Pet id {pet.id} already exists for owner.")
		self.pets.append(pet)

	def get_pet(self, pet_id: int) -> Optional["Pet"]:
		"""Return the pet that matches pet_id, if present."""
		for pet in self.pets:
			if pet.id == pet_id:
				return pet
		return None
		
# ─look up pet by name (case-insensitive) ──────────────────────────
	def get_pet_by_name(self, name: str) -> Optional["Pet"]:
        """Return the first pet whose name matches (case-insensitive), or None."""
        name_lower = name.strip().lower()
    	for pet in self.pets:
            if pet.name.strip().lower() == name_lower:
                return pet
        return None
	
	def get_all_tasks(self, include_completed: bool = True) -> List["Task"]:
		"""Collect tasks across all pets owned by this owner."""
		all_tasks = [task for pet in self.pets for task in pet.tasks]
		if include_completed:
			return all_tasks
		return [task for task in all_tasks if not task.is_completed]


@dataclass
class Task:
	"""Represents one pet care task."""

	id: int
	description: str
	start_time: datetime
	duration_mins: int
	priority: str = "medium"
	is_completed: bool = False
	recurrence: Recurrence = Recurrence.ONCE

	def __post_init__(self) -> None:
		if self.duration_mins <= 0:
			raise ValueError("duration_mins must be greater than 0.")
		if not self.description.strip():
			raise ValueError("description cannot be empty.")

	@property
	def end_time(self) -> datetime:
		"""Compute the end time from start and duration."""
		return self.start_time + timedelta(minutes=self.duration_mins)

	def mark_complete(self) -> None:
		"""Mark this task as complete."""
		self.is_completed = True


@dataclass
class Pet:
	"""Represents a pet and its care tasks."""

	id: int
	name: str
	breed: str
	age: int
	tasks: List[Task] = field(default_factory=list)

	def enter_name(self, name: str) -> None:
		"""Update the pet's name."""
		self.name = name

	def enter_age(self, age: int) -> None:
		"""Update the pet's age."""
		self.age = age

	def enter_breed(self, breed: str) -> None:
		"""Update the pet's breed."""
		self.breed = breed

	def add_task(self, task: Task) -> None:
		"""Attach a task to this pet."""
		if self.get_task(task.id) is not None:
			raise ValueError(f"Task id {task.id} already exists for pet {self.id}.")
		self.tasks.append(task)

	def get_task(self, task_id: int) -> Optional[Task]:
		"""Get a task by id if it exists for this pet."""
		for task in self.tasks:
			if task.id == task_id:
				return task
		return None


class Scheduler:
	"""Coordinates pets and scheduling operations."""

	def __init__(self, owner: Owner) -> None:
		self.owner = owner
		self._next_task_id: int = 1 #auto-increment ID for generated tasks

	def _new_id(self) -> int:
        """Return a fresh unique task ID."""
        tid = self._next_task_id
        self._next_task_id += 1
        return tid
	
	def add_pet(self, pet: Pet) -> None:
		"""Register a pet in the scheduler."""
		self.owner.add_pet(pet)

	def get_pets(self) -> List[Pet]:
		"""Return pets from the owner as the single source of truth."""
		return self.owner.pets

	def add_task_to_pet(self, pet_id: int, task: Task) -> None:
		"""Add a new task to a specific pet owned by this scheduler's owner."""
		pet = self.owner.get_pet(pet_id)
		if pet is None:
			raise ValueError(f"Pet id {pet_id} was not found.")
		pet.add_task(task)

	def get_all_tasks(self, include_completed: bool = True) -> List[Task]:
		"""Retrieve every task across all owner pets."""
		return self.owner.get_all_tasks(include_completed=include_completed)

	def get_upcoming_tasks(self) -> List[Task]:
		"""Return tasks that should be scheduled soon."""
		all_tasks = self.get_all_tasks(include_completed=False)
		return sorted(all_tasks, key=lambda task: task.start_time)

	def check_conflicts(self, task: Task) -> bool:
		"""Check whether a task conflicts with existing tasks."""
		for existing_task in self.get_upcoming_tasks():
			if existing_task.id == task.id:
				continue
			overlaps = task.start_time < existing_task.end_time and existing_task.start_time < task.end_time
			if overlaps:
				return True
		return False

	def mark_task_complete(self, task_id: int) -> bool:
		"""Mark a task complete by id and report whether it was found."""
		for task in self.get_all_tasks(include_completed=True):
			if task.id == task_id:
				task.mark_complete()
				return True
		return False

	# ── NEW 1: Expand recurring tasks into concrete instances ────────────────
	def expand_recurring_tasks(
    	self,
    	pet_id: int,
    	start_date: datetime,
    	end_date: datetime,
    ) -> List[Task]:
        """
        For every recurring task on a pet, generate concrete Task instances
        between start_date and end_date (inclusive by day) and attach them
        to the pet.  Returns the list of newly created tasks.

        - DAILY  → one copy per calendar day in the range
        - WEEKLY → one copy per week (same weekday as the template's start_time)
        - ONCE   → skipped (already a one-off)
        """
    	pet = self.owner.get_pet(pet_id)
    	if pet is None:
    		raise ValueError(f"Pet id {pet_id} was not found.")

        # Only templates that are recurring and not yet expanded past end_date
		templates = [t for t in pet.tasks if t.recurrence != Recurrence.ONCE]
		new_tasks: List[Task] = []

		for tmpl in templates:
			if tmpl.recurrence == Recurrence.DAILY:
				step = timedelta(days=1)
			else:  # WEEKLY
				step = timedelta(weeks=1)

            # Start from the template's own date, walk forward until end_date
            cursor = tmpl.start_time
            while cursor.date() <= end_date.date():
                if cursor.date() >= start_date.date() and cursor != tmpl.start_time:
                    new_task = Task(
                        id=self._new_id(),
                        description=tmpl.description,
                        start_time=cursor,
                        duration_mins=tmpl.duration_mins,
                        priority=tmpl.priority,
                        recurrence=Recurrence.ONCE,  # generated copy is a one-off
                    )
                    pet.add_task(new_task)
                    new_tasks.append(new_task)
                cursor += step

        return new_tasks

    # ── NEW 2: Filter tasks by pet name ──────────────────────────────────────
    def get_tasks_by_pet_name(
        self,
        name: str,
        include_completed: bool = True,
    ) -> List[Task]:
        """
        Return all tasks for the pet whose name matches (case-insensitive).
        Raises ValueError if no pet with that name exists.
		Use the helper function: get_pet_name
        """
        pet = self.owner.get_pet_by_name(name)
        if pet is None:
            raise ValueError(f"No pet named '{name}' found.")
        tasks = list(pet.tasks)
        if not include_completed:
            tasks = [t for t in tasks if not t.is_completed]
        return sorted(tasks, key=lambda t: t.start_time)


