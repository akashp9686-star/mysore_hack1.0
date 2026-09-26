from backend.database.database import fetch_all

def resources_for_concept(concept_id: int):
    return fetch_all('SELECT id,title,source,url,description,resource_type FROM learning_resources WHERE concept_id=? ORDER BY id',(concept_id,))
