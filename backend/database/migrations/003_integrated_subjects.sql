-- Integrated subject picker: broaden the academic subject shell only.
-- Mathematics already exists; INSERT OR IGNORE avoids duplication.
INSERT OR IGNORE INTO subjects (id, name) VALUES (2, 'Science');
INSERT OR IGNORE INTO subjects (id, name) VALUES (3, 'Social Science');
INSERT OR IGNORE INTO subjects (id, name) VALUES (4, 'English');
