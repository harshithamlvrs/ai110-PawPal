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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
