import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Recurrence
import datetime

#add pet and schedule task ( replace placeholders with calls to methods from pawpal_system.py)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Session state initialization ---
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=Owner(name=""))
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

scheduler: Scheduler = st.session_state.scheduler

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=scheduler.owner.name or "Jordan")
if owner_name != scheduler.owner.name:
    scheduler.owner.enter_name(owner_name)

st.markdown("### Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed / Species", value="Labrador")
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    submitted_pet = st.form_submit_button("Add Pet")

if submitted_pet:
    new_pet = Pet(
        id=st.session_state.next_pet_id,
        name=pet_name,
        breed=breed,
        age=int(age),
    )
    try:
        # Owner.add_pet() registers the pet and prevents duplicate IDs
        scheduler.add_pet(new_pet)
        st.session_state.next_pet_id += 1
        st.success(f"Added pet: {pet_name}")
    except ValueError as e:
        st.error(str(e))

pets = scheduler.get_pets()
if pets:
    st.write("Registered pets:")
    st.table([{"ID": p.id, "Name": p.name, "Breed": p.breed, "Age": p.age} for p in pets])
else:
    st.info("No pets registered yet.")

st.markdown("### Schedule a Task")
if not pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_options = {f"{p.name} (ID {p.id})": p.id for p in pets}
    with st.form("add_task_form"):
        selected_pet_label = st.selectbox("Select pet", list(pet_options.keys()))
        task_desc = st.text_input("Task description", value="Morning walk")
        task_date = st.date_input("Date", value=datetime.date.today())
        task_time = st.time_input("Start time", value=datetime.time(8, 0))
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recurrence_value = st.selectbox(
            "Recurrence",
            [Recurrence.ONCE.value, Recurrence.DAILY.value, Recurrence.WEEKLY.value],
            index=0,
            help="Set this task to repeat automatically when you mark it complete.",
        )
        submitted_task = st.form_submit_button("Add Task")

    if submitted_task:
        start_dt = datetime.datetime.combine(task_date, task_time)
        new_task = Task(
            id=st.session_state.next_task_id,
            description=task_desc,
            start_time=start_dt,
            duration_mins=int(duration),
            priority=priority,
            recurrence=Recurrence(recurrence_value),
        )
        pet_id = pet_options[selected_pet_label]
        conflicts = scheduler.detect_conflicts(new_task)  # Get detailed conflict info instead of boolean
        try:
            # Scheduler.add_task_to_pet() looks up the pet by ID and calls pet.add_task()
            scheduler.add_task_to_pet(pet_id, new_task)
            st.session_state.next_task_id += 1
            if conflicts:
                # Display each conflict as a separate warning with contextual details
                st.warning(f"Task added, but **{len(conflicts)} conflict(s) detected**:")
                for conflict in conflicts:
                    st.warning(conflict.warning_message())
            else:
                st.success(f"'{task_desc}' scheduled for {start_dt.strftime('%b %d at %H:%M')}.")
        except ValueError as e:
            st.error(str(e))

st.divider()

st.subheader("Upcoming Schedule")
st.caption("Calls Scheduler.get_upcoming_tasks() — returns incomplete tasks sorted by start time.")

# Scheduler.get_upcoming_tasks() sorts by start_time and excludes completed tasks
upcoming = scheduler.get_upcoming_tasks()
if upcoming:
    st.table([
        {
            "Description": t.description,
            "Start": t.start_time.strftime("%Y-%m-%d %H:%M"),
            "End": t.end_time.strftime("%H:%M"),
            "Duration (min)": t.duration_mins,
            "Priority": t.priority,
            "Recurrence": t.recurrence.value,
        }
        for t in upcoming
    ])

    task_options = {
        f"{t.description} | {t.start_time.strftime('%Y-%m-%d %H:%M')} | {t.recurrence.value}": t
        for t in upcoming
    }
    with st.form("mark_complete_form"):
        st.markdown("### Mark Task Complete")
        selected_task_label = st.selectbox(
            "Select an upcoming task",
            list(task_options.keys()),
        )
        submitted_complete = st.form_submit_button("Mark Complete")

    if submitted_complete:
        selected_task = task_options[selected_task_label]
        updated = scheduler.mark_task_complete(task_id=selected_task.id)
        if updated:
            st.success(
                f"Marked '{selected_task.description}' complete. "
                "If recurring, the next occurrence was created automatically."
            )
            st.rerun()
        else:
            st.error("Unable to mark task complete. Please refresh and try again.")
else:
    st.info("No upcoming tasks. Add tasks above.")
