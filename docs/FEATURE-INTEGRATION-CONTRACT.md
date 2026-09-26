# HACKMYSORE 1.0
# PERSONALIZED LEARNING PLATFORM
# FEATURE & INTEGRATION CONTRACT — VERSION 1.0

==================================================
1. PURPOSE
==================================================

This document defines the additional product features and integrations
that can be built on top of the Master Technical Contract.

The Master Technical Contract remains the primary technical authority.

These features must not break the core adaptive-learning loop:

MEASURE
→ DETECT
→ UNDERSTAND
→ INTERVENE
→ REASSESS
→ ADAPT

The system must continue functioning even if optional AI or Telegram
services are unavailable.

==================================================
2. PRODUCT VISION
==================================================

The platform should support different types of learners:

1. Classes 5–9
2. Class 10
3. PUC / Higher Secondary
4. Working Professionals / Skill Learners

The learner selects their educational level and learning goal.

The platform then adapts:

Learner Type
↓
Learning Goal
↓
Subject / Skill
↓
Assessment
↓
Performance Analysis
↓
Weak Concept / Skill
↓
Recommended Next Step
↓
Targeted Learning
↓
Reassessment
↓
Updated Learning Path

The core principle is:

"Based on what this learner has demonstrated,
determine what they should learn or do next."

==================================================
3. USER ROLES
==================================================

The platform may contain the following roles:

STUDENT / LEARNER
- Takes assessments
- Receives recommendations
- Completes targeted practice
- Views progress
- Receives AI-assisted explanations where available

FACILITATOR / TEACHER
- Views students requiring attention
- Views weak concepts
- Reviews evidence
- Assigns interventions
- Reviews reassessment results

PARENT / GUARDIAN
- Receives optional progress notifications
- Does not directly modify academic records

AI ASSISTANT
- Analyses available learning evidence
- Provides explanations/recommendations
- Does not directly modify core student records

==================================================
4. LEARNING PATH SELECTION
==================================================

The landing flow should allow the learner to select:

A. CLASSES 5–9
B. CLASS 10
C. PUC / HIGHER SECONDARY
D. WORKING PROFESSIONAL / SKILL LEARNER

The selected category determines available subjects, skills,
assessments and learning goals.

The MVP may contain full functionality only for:

Class 8
→ Mathematics
→ Algebra
→ Linear Equations

Other categories may initially contain limited content.

Do not create fake functionality merely to make all categories appear complete.

==================================================
5. PERSONALIZED COURSE ENGINE
==================================================

The platform must not simply provide a fixed course sequence.

The system should determine the next recommended learning action
based on learner performance.

Example:

Student attempts:
Linear Equations

↓
Repeated errors detected

↓
Likely weak concept:
Variables on Both Sides

↓
System recommends:
Targeted Practice

↓
Student completes practice

↓
Reassessment

↓
Performance improves

↓
System recommends:
Continue to next concept

OR

Performance remains low

↓
System recommends:
Facilitator intervention

The recommendation must be based on stored learning evidence.

==================================================
6. AI LEARNING ASSISTANT
==================================================

An optional AI assistant may be provided to the learner.

The AI assistant should help answer:

"What should I learn next?"

"What am I struggling with?"

"Why was this recommended?"

"What should I practice now?"

Example:

Student:
"I completed the Linear Equations assessment."

System:
"You repeatedly struggled with Variables on Both Sides."

AI Assistant:
"Your next step is to practice Variables on Both Sides.
Start with the targeted practice set before moving to the
next Linear Equations concept."

==================================================
7. AI EXPLANATION FEATURE
==================================================

The AI may explain:

- Why a concept was identified as weak
- Why a resource was recommended
- What the learner should practice
- What prerequisite concept may be useful
- How to approach a topic
- Why the learner should not move to the next concept yet

The AI must NOT invent student performance data.

The AI must use actual information supplied by the backend.

Example input:

Student accuracy:
43%

Weak concept:
Variables on Both Sides

Previous attempts:
7

Status:
needs_intervention

The AI may explain the recommendation using these facts.

==================================================
8. AI NEXT-STEP RECOMMENDATION
==================================================

The AI may recommend one of the following actions:

1. Continue to next concept
2. Practice current concept
3. Review prerequisite concept
4. Attempt targeted questions
5. Review a learning resource
6. Request facilitator intervention
7. Take reassessment

The final application decision remains controlled by the
adaptive engine.

AI recommendations are advisory.

The system must not depend entirely on AI.

==================================================
9. AI FAILURE BEHAVIOUR
==================================================

If AI:

- fails
- times out
- returns invalid data
- reaches an API limit
- is unavailable

the platform must continue functioning.

The rule-based adaptive engine must still determine the student's
learning status and next action.

The UI should gracefully show:

"AI assistance is currently unavailable.
Your personalized learning path is still available."

==================================================
10. MCQ DIAGNOSTIC SYSTEM
==================================================

The primary assessment format is MCQ.

The system must NOT claim to observe the student's complete
working steps.

Instead, questions may contain diagnostic distractors.

Example:

Question:
Solve 3x + 7 = 22

A. 3
B. 5      ← correct
C. 15
D. 29

Each distractor may be mapped to a possible misconception.

Example:

C → likely stopped after subtracting 7
D → likely used incorrect operation

Repeated selection of similar distractors across related questions
can provide evidence of a possible misconception.

The system must describe this as a diagnostic signal,
not proof of the exact reasoning process.

==================================================
11. MISCONCEPTION ANALYSIS
==================================================

Each diagnostic question may contain:

question_id
concept_id
correct_answer
distractor mapping

Example:

Question:
3x + 7 = 22

Concept:
Variable Isolation

Correct:
B

Distractors:

A → incorrect isolation
C → incomplete operation
D → incorrect arithmetic operation

The adaptive engine can use repeated patterns to identify
likely weak concepts.

==================================================
12. TARGETED PRACTICE
==================================================

When a weak concept is detected, the system should generate or
retrieve targeted practice.

Example:

Detected:
Variables on Both Sides

Instead of:

"Practice Linear Equations"

show:

"Practice Variables on Both Sides"

The targeted practice should contain questions mapped to
the same concept.

==================================================
13. RESOURCE RECOMMENDATION
==================================================

Resources must be connected to concepts.

Example:

Weak concept:
Variables on Both Sides

Recommended:

- Short explanation
- Practice questions
- Video/resource
- Example problems

The system should not become a generic internet search engine.

Resources must be recommended because a learning gap was detected.

==================================================
14. REASSESSMENT
==================================================

After intervention, the system should provide a new assessment
targeting the same concept.

Example:

Before:
43%

Intervention:
Targeted Practice

After:
80%

System status:
Improved

Next action:
Continue to next concept

If performance remains low:

Status:
Still struggling

Next action:
Facilitator intervention

==================================================
15. TELEGRAM PARENT NOTIFICATION
==================================================

The platform may provide an optional Telegram notification system
for parents/guardians.

Telegram must NOT expose unnecessary student information.

Notifications should communicate meaningful progress.

Examples:

--------------------------------------------------
NORMAL PROGRESS

"Learning Update

Rahul completed his Mathematics assessment.

Topic:
Linear Equations

Status:
Assessment completed.

No intervention is currently required."
--------------------------------------------------

--------------------------------------------------
WEAK CONCEPT DETECTED

"Learning Update

Rahul may need additional support in:

Variables on Both Sides

The system has recommended targeted practice."
--------------------------------------------------

--------------------------------------------------
IMPROVEMENT

"Learning Update

Rahul completed targeted reassessment.

Variables on Both Sides

Previous:
43%

Current:
80%

Status:
Improved"
--------------------------------------------------

--------------------------------------------------
TEACHER INTERVENTION REQUIRED

"Learning Update

Rahul continues to struggle with:

Variables on Both Sides

Facilitator intervention has been recommended."
--------------------------------------------------

Telegram messages should not include:
- passwords
- API keys
- unnecessary personal information
- private assessment details beyond what is required

==================================================
16. PARENT NOTIFICATION TRIGGERS
==================================================

Notifications should NOT be sent for every question.

Possible notification events:

1. Assessment completed
2. Significant weak concept detected
3. Intervention recommended
4. Student continues struggling
5. Student improves after intervention
6. Major learning milestone reached

The exact notification policy should be configurable.

==================================================
17. TELEGRAM ARCHITECTURE
==================================================

Student
↓
Assessment
↓
Backend
↓
Adaptive Engine
↓
Learning State Updated
↓
Notification Service
↓
Telegram Bot
↓
Parent / Guardian

Telegram must never directly access SQLite.

The backend controls what information is sent.

==================================================
18. TELEGRAM FAILURE
==================================================

If Telegram is unavailable:

The core learning system must continue functioning.

The notification should be marked:

pending / failed

and the student learning flow must not break.

==================================================
19. FACILITATOR DASHBOARD
==================================================

The facilitator dashboard must answer:

"Who needs my attention?"

Show:

Student
Weak Concept
Accuracy
Current Status
Previous Intervention
Reassessment Result
Recommended Next Action

Example:

RAHUL

Weak Concept:
Variables on Both Sides

Accuracy:
43%

Intervention:
Targeted Practice

Reassessment:
80%

Status:
Improved

Next:
Continue Learning

==================================================
20. STUDENT AI ASSISTANT UI
==================================================

The student dashboard may contain:

"Learning Assistant"

Example:

--------------------------------------------------
LEARNING ASSISTANT

Based on your recent assessment:

You should focus on:
Variables on Both Sides

Why:
You made repeated errors on questions mapped
to this concept.

Recommended next step:
Targeted Practice

[Start Practice]

[Ask Why]
--------------------------------------------------

The learner may ask:

"Why am I being asked to practice this?"

"What should I learn after this?"

"Why can't I move to the next topic?"

"What did I improve in?"

The AI should answer using actual backend learning data.

==================================================
21. COURSE NAVIGATION
==================================================

The course interface should show:

Completed
Current
Needs Practice
Locked / Not Recommended Yet

Example:

ALGEBRA

✓ Basic Linear Equations
⚠ Variables on Both Sides
○ Substitution
○ Word Problems

The current concept should be visually highlighted.

The learner should understand:

"What have I mastered?"

"What am I currently learning?"

"What should I do next?"

==================================================
22. ADAPTIVE COURSE LOGIC
==================================================

The course should NOT simply unlock everything in order.

Example:

Student performs well:

Concept A
↓
Concept B
↓
Concept C

Student struggles:

Concept A
↓
Concept B
↓
Weakness detected
↓
Targeted Practice
↓
Reassessment
↓
Improved
↓
Concept C

If still struggling:

Concept B
↓
Targeted Practice
↓
Still struggling
↓
Facilitator Intervention

==================================================
23. LEARNING STATE
==================================================

Every important concept should have a learning state.

Possible states:

NORMAL
ADDITIONAL_PRACTICE
NEEDS_INTERVENTION
IN_PROGRESS
SUCCESSFUL
UNSUCCESSFUL

These states should come from the backend.

The frontend must not independently invent the student's status.

==================================================
24. NOTIFICATION + AI + ADAPTIVE ENGINE RELATIONSHIP
==================================================

The three systems have different responsibilities.

ADAPTIVE ENGINE
Determines the student's learning state.

AI
Explains/recommends using available evidence.

TELEGRAM
Communicates important updates to parents/guardians.

Architecture:

                 ┌───────────────┐
                 │    STUDENT    │
                 └───────┬───────┘
                         ↓
                    Assessment
                         ↓
                 ┌───────────────┐
                 │    FastAPI    │
                 └───────┬───────┘
                         ↓
              ┌─────────────────────┐
              │  Adaptive Engine    │
              └─────────┬───────────┘
                        ↓
                  Learning State
                   ↙          ↘
                  ↓            ↓
               AI Assistant   Telegram
                  ↓            ↓
              Student       Parent
                  ↓
             Next Learning
                Action

==================================================
25. SECURITY AND PRIVACY
==================================================

Student data must be treated as private.

The system must:

- collect minimal personal information
- avoid unnecessary sensitive data
- separate student/facilitator/parent access
- keep Telegram credentials in .env
- keep AI API keys in .env
- never expose API keys in frontend JavaScript
- never commit .env
- never expose raw database errors

==================================================
26. MVP PRIORITY
==================================================

Features must be implemented in this order:

PRIORITY 1
Core adaptive-learning loop

PRIORITY 2
MCQ diagnostic system

PRIORITY 3
Targeted practice + reassessment

PRIORITY 4
Facilitator dashboard

PRIORITY 5
AI learning assistant

PRIORITY 6
Telegram parent notifications

PRIORITY 7
Additional learner categories and subjects

Optional features must never delay the working core loop.

==================================================
27. PRIMARY DEMONSTRATION
==================================================

The main demonstration remains:

Rahul
↓
Class 8
↓
Mathematics
↓
Algebra
↓
Linear Equations
↓
Diagnostic MCQs
↓
Repeated misconception pattern
↓
Variables on Both Sides
↓
Targeted Practice
↓
Reassessment
↓
Improvement / Continued Struggle
↓
Facilitator Dashboard
↓
Parent Telegram Notification

If AI is enabled:

AI explains:
"What was detected?"

"What should I do next?"

"Why was this recommended?"

==================================================
28. DEFINITION OF SUCCESS
==================================================

The platform is successful when it can demonstrate:

1. A learner takes an assessment.
2. Answers are stored.
3. MCQ response patterns are analysed.
4. A weak concept can be identified.
5. Targeted practice is recommended.
6. The learner completes intervention.
7. The learner is reassessed.
8. Progress changes based on the result.
9. Facilitator sees the student's updated state.
10. AI can explain the recommended next step when available.
11. Parent can receive an important progress notification through Telegram.
12. The core system still works if AI or Telegram is unavailable.

==================================================
29. FINAL PRINCIPLE
==================================================

The platform must never become:

"An AI chatbot + a quiz + a Telegram bot."

All features must serve the same central purpose:

"Based on what the learner has demonstrated,
identify what they need next and help the learner,
facilitator and parent understand that progress."

CORE LOOP:

MEASURE
→ DETECT
→ UNDERSTAND
→ INTERVENE
→ REASSESS
→ ADAPT