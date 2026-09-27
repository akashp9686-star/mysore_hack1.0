-- Record the exact MCQ option selected by the learner.
ALTER TABLE attempts ADD COLUMN selected_option_id INTEGER REFERENCES question_options(id);
