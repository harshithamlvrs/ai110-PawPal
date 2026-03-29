from dataclasses import dataclass, field
from datetime import datetime
from typing import List


class Owner:
	"""Represents the pet owner."""

	def __init__(self, name: str = "") -> None:
		self.name = name

	def enter_name(self, name: str) -> None:
		"""Update the owner's name."""
		pass


@dataclass
class Task:
	"""Represents one pet care task."""

	id: int
	description: str
	due_time: datetime
	duration_mins: int
	is_completed: bool = False
	frequency: str = "once"

	def mark_complete(self) -> None:
		"""Mark this task as complete."""
		pass


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
		pass

	def enter_age(self, age: int) -> None:
		"""Update the pet's age."""
		pass

	def enter_breed(self, breed: str) -> None:
		"""Update the pet's breed."""
		pass

	def add_task(self, task: Task) -> None:
		"""Attach a task to this pet."""
		pass


class Scheduler:
	"""Coordinates pets and scheduling operations."""

	def __init__(self) -> None:
		self.pets: List[Pet] = []

	def add_pet(self, pet: Pet) -> None:
		"""Register a pet in the scheduler."""
		pass

	def get_upcoming_tasks(self) -> List[Task]:
		"""Return tasks that should be scheduled soon."""
		pass

	def check_conflicts(self, task: Task) -> bool:
		"""Check whether a task conflicts with existing tasks."""
		pass