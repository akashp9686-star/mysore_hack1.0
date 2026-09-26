# Full-stack integration notes

### Team components
- Adinath: database and seed data in `backend/database/` and `data/`.
- Aakash: FastAPI APIs and deterministic adaptive engine.
- Vedanth/frontend contract: HTML/CSS/JS pages and REST-only integration.
- Jai Ganesh: Gemini diagnostic agent, integrated under `backend/ai/`.

### AI contract
The supplied agent accepts question, student answer, correct answer, and concept, and returns error type, identified concept, confidence, explanation, and recommended action. It is advisory. Persisted learning status remains controlled by the backend adaptive engine.

### Liquid Glass web treatment
The frontend uses CSS glass materials, translucent navigation, blur, layered surfaces, restrained motion, and strong hierarchy inspired by Apple's Liquid Glass guidance. It is a web implementation of the visual language, not Apple's native SwiftUI/UIKit material.
