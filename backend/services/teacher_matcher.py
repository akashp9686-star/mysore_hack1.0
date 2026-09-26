"""Teacher candidate matching using only fields present in Adinath's schema.

The current teachers table has no subject/topic/expertise fields. Therefore
this service must not invent teacher expertise. Until the team agrees on an
expertise schema, matching is limited to verification status and experience.
"""

from backend.database.database import fetch_all, fetch_one


def match_teachers(concept_id: int):
    concept = fetch_one(
        """
        SELECT c.id AS concept_id, c.name AS concept_name,
               t.name AS topic_name, s.name AS subject_name
        FROM concepts c
        JOIN topics t ON t.id = c.topic_id
        JOIN subjects s ON s.id = t.subject_id
        WHERE c.id = ?
        """,
        (concept_id,),
    )
    if not concept:
        return []

    # Do not claim a teacher is an expert when the schema contains no such data.
    return fetch_all(
        """
        SELECT id, name, experience, verification_status
        FROM teachers
        ORDER BY
            CASE verification_status WHEN 'verified' THEN 0 ELSE 1 END,
            experience DESC,
            id ASC
        """
    )
