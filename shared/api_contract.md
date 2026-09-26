# API Contract — v1

Base URL: `http://localhost:8000/api`

All responses are JSON. IDs use snake_case fields.

## Student
`GET /students/{student_id}`

## Assessment
`GET /assessments/{assessment_id}`

`POST /assessments/{assessment_id}/attempt`
```json
{"student_id":101,"question_id":42,"answer":"x = 5","time_taken":32}
```

## Progress
`GET /students/{student_id}/progress`

## Intervention
`GET /interventions/student/{student_id}`

`POST /interventions`
```json
{"student_id":101,"concept_id":14,"type":"teacher_session","teacher_id":7}
```

## Teachers
`GET /teachers/match?concept_id=14`

## Resources
`GET /resources/{concept_id}`

## Facilitator
`GET /facilitator/students`
