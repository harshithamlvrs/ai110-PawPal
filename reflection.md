# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

_Briefly describe your initial UML design._

My initial design had four classes connected in a simple hierarchy:

```
User/Owner                          Scheduler
─────────────────             ──────────────────────────────
- name: string                - pets: List[Pet]
──────────────────            ──────────────────────────────
+ EnterName()                 + add_pet(pet: Pet)
                              + get_upcoming_tasks(): List
                              + check_conflicts(task: Task): bool
        |                              |
        | owns (1..*)                  | manages (1..*)
        ▼                              ▼
Pet                           Task
─────────────────────────     ──────────────────────────────
- id: int                     - id: int
- name: string                - description: string
- breed: string               - due_time: datetime
- age: int                    - duration_mins: int
- tasks: List[Task]           - is_completed: bool
─────────────────────────     - frequency: string
+ EnterName()                 ──────────────────────────────
+ EnterAge()                  + mark_complete()
+ EnterBreed()
+ add_task(task: Task)
```

_What classes did you include, and what responsibilities did you assign to each?_

I included four classes:
- **User** — represents the pet owner; stores the owner's name and handles input.
- **Pet** — represents an individual pet; holds the pet's identity (id=Identifies which pet if the owner has multiple pets, name, breed, age) and a list of tasks to care for the pet.
- **Task** — represents a single care activity (e.g., feeding, walk); stores timing, duration, completion status, and recurrence frequency.
- **Scheduler** — the central coordinator; holds all pets and is responsible for ordering upcoming tasks and detecting time conflicts between tasks.

**b. Design changes**

_Did your design change during implementation?_ Yes
_If yes, describe at least one change and why you made it._

Some of the changes I made was:
    1. Added explicit recurrence typing via Recurrence enum near the top of pawpal_system.py. This explicitly defines the recurrance of a specific task (Daily, weekly, monthly)
    2. Strengthened owner relationship: Owner now tracks pets. Added Owner.add_pet(...). Scheduler now takes owner in its constructor and links pets through that owner.
    3. mark_complete sets completion status. add_task appends to pet task list. pets_by_id and tasks_by_id dictionaries so that we can resolve issues in the future by looking at the ID instead of scanning everything
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**
_What constraints does your scheduler consider (for example: time, priority, preferences)?_
_How did you decide which constraints mattered most?_
My scheduler considers the time and priority of the tasks. It categorizes the tasks based on the time (start time of the tasks in sequential order) and then puts the highest priority at first ending with the lowest priority. I constantly tested the website as I was coding to decide on the constraints that mattered the most. 

**b. Tradeoffs**

_Describe one tradeoff your scheduler makes._
_Why is that tradeoff reasonable for this scenario?_
One tradeoff is that the scheduler keeps showing ALL of the time-conflict warnings to the user. But, this tradeoff is reasonable because the user can look over the past warnings and make sure to not repeat them.
---

## 3. AI Collaboration

**a. How you used AI**

_How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?_
I used AI for creating the UML diagram and asking it to debug/suggest changes. 

_What kinds of prompts or questions were most helpful?_
The prompt about asking the AI to create the UML diagram based on my initial plan was very helpful. I plugged that code into the Mermaid Live Editor which generated a UML diagram. This visually explained my thoughts and what I wanted the code to do.


**b. Judgment and verification**

_Describe one moment where you did not accept an AI suggestion as-is._
_How did you evaluate or verify what the AI suggested?_
One moment was that I asked AI to create a skeleton of the classes and what implementation of the UML diagram would like. In the code that it suggested, I noticed that it duplicated the pet_ids in both the Owner class and the Scheduler. So, I asked it to use Scheduler to access each Owner and the Owners will have direct access to the pets and task access.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  Right now, the scheduler warns the user about time conflicts but it doesn't provide them an option to delete or change the task. I would try to improve the design by including this change.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
