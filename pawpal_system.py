from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class Recurrence(str, Enum):
	"""Enumerates supported recurrence patterns for tasks."""

	ONCE = "once"
	DAILY = "daily"
	WEEKLY = "weekly"


@dataclass
class ConflictInfo:
	"""Lightweight conflict warning info for a task overlap."""

	conflicting_pet_name: str
	conflicting_task_description: str
	conflicting_task_start: datetime
	conflicting_task_end: datetime

	def warning_message(self) -> str:
		"""Return a human-readable warning message for this conflict."""
		return (
			f"⚠️ Overlaps with '{self.conflicting_task_description}' "
			f"for {self.conflicting_pet_name} "
			f"({self.conflicting_task_start.strftime('%H:%M')}–{self.conflicting_task_end.strftime('%H:%M')})"
		)


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

	def filter_tasks(self, is_completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
		"""Filter tasks by completion status and/or pet name.

		If both filters are provided, a task must match both.
		"""
		normalized_pet_name = pet_name.strip().lower() if pet_name is not None else None
		filtered_tasks: List[Task] = []

		for pet in self.owner.pets:
			if normalized_pet_name is not None and pet.name.lower() != normalized_pet_name:
				continue
			for task in pet.tasks:
				if is_completed is not None and task.is_completed != is_completed:
					continue
				filtered_tasks.append(task)

		return filtered_tasks

	def get_upcoming_tasks(self) -> List[Task]:
		"""Return tasks that should be scheduled soon."""
		all_tasks = self.get_all_tasks(include_completed=False)
		return sorted(all_tasks, key=lambda task: task.start_time)

	def detect_conflicts(self, task: Task) -> List[ConflictInfo]:
		"""Detect conflicts and return detailed warning info for each overlap.
		
		Lightweight: scans all pets' upcoming tasks once and returns structured conflict data.
		Each conflict includes the pet name, conflicting task details, and timing.
		"""
		conflicts: List[ConflictInfo] = []
		for pet in self.owner.pets:
			for existing_task in pet.tasks:
				if existing_task.id == task.id or existing_task.is_completed:
					continue
				overlaps = task.start_time < existing_task.end_time and existing_task.start_time < task.end_time
				if overlaps:
					conflicts.append(
						ConflictInfo(
							conflicting_pet_name=pet.name,
							conflicting_task_description=existing_task.description,
							conflicting_task_start=existing_task.start_time,
							conflicting_task_end=existing_task.end_time,
						)
					)
		return conflicts

	def check_conflicts(self, task: Task) -> bool:
		"""Check whether a task conflicts with existing tasks (deprecated: use detect_conflicts instead)."""
		return len(self.detect_conflicts(task)) > 0

	def _next_task_id_for_pet(self, pet: Pet) -> int:
		"""Return the next available task id for a given pet."""
		if not pet.tasks:
			return 1
		return max(existing_task.id for existing_task in pet.tasks) + 1

	def _next_start_time(self, task: Task) -> Optional[datetime]:
		"""Compute the next start time for recurring tasks."""
		if task.recurrence == Recurrence.DAILY:
			return task.start_time + timedelta(days=1) 
		if task.recurrence == Recurrence.WEEKLY:
			return task.start_time + timedelta(days=7)
		return None

	def mark_task_complete(self, task_id: int) -> bool:
		"""Mark a task complete by id and report whether it was found."""
		for pet in self.owner.pets:
			task = pet.get_task(task_id)
			if task is None:
				continue

			if task.is_completed:
				return True

			task.mark_complete()

			next_start = self._next_start_time(task)
			if next_start is not None:
				next_task = Task(
					id=self._next_task_id_for_pet(pet),
					description=task.description,
					start_time=next_start,
					duration_mins=task.duration_mins,
					priority=task.priority,
					is_completed=False,
					recurrence=task.recurrence,
				)
				pet.add_task(next_task)

			return True
		return False
	