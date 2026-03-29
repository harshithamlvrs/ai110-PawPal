#import classes from the pawpal_system.py file
from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

#create an Owner and 2 pets with 3 tasks at different times per pet
#change pet 1 to a bird named Shuka and pet 2 to a monkey named Dadi
from datetime import datetime
owner = Owner(name="Krishna")
pet1 = Pet(id=1, name="Shuka", breed="Parakeet Parrot", age=6)
pet2 = Pet(id=2, name="Dadi", breed="Capuchin Monkey", age=4)

task1 = Task(id=1, description="Morning walk", start_time=datetime(2026, 3, 29, 7, 0), duration_mins=30, priority="high")
task2 = Task(id=2, description="Feed breakfast", start_time=datetime(2026, 3, 29, 8, 0), duration_mins=15, priority="high")
task3 = Task(id=3, description="Playtime", start_time=datetime(2026, 3, 29, 10, 0), duration_mins=20, priority="low")

task4 = Task(id=4, description="Feed breakfast", start_time=datetime(2026, 3, 29, 8, 0), duration_mins=20, priority="high")
task5 = Task(id=5, description="Grooming", start_time=datetime(2026, 3, 29, 9, 0), duration_mins=25, priority="medium")
task6 = Task(id=6, description="Vet appointment", start_time=datetime(2026, 3, 29, 11, 0), duration_mins=60, priority="high")
task7 = Task(id=7, description="Evening walk", start_time=datetime(2026, 3, 29, 17, 0), duration_mins=30, priority="medium")
task8 = Task(id=8, description="Playtime", start_time=datetime(2026, 3, 29, 18, 0), duration_mins=30, priority="low")

pet1.add_task(task1)
pet1.add_task(task2)
pet1.add_task(task3)
pet1.add_task(task6)

pet2.add_task(task4)
pet2.add_task(task5)
pet2.add_task(task6)
pet2.add_task(task7)
pet2.add_task(task8)

owner.add_pet(pet1)
owner.add_pet(pet2)
scheduler = Scheduler(owner=owner)

print("Today's Schedule: \n")
for pet in owner.pets:
    print(f"- {pet.name}:")
    for task in pet.tasks:
        print(f"  - {task.description} ({task.duration_mins} minutes)")

#command to create a new command to enter in teh terminal to create a new file tests/test_pawpal.py
# python -m pytest tests/test_pawpal.py
