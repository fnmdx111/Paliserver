from _sqlite3 import IntegrityError
import sqlite3
import os

conn = sqlite3.connect(os.path.join('palis', 'palis.db'))
cursor = conn.cursor()

sql = '''
ALTER TABLE paper RENAME TO paper_tmp;
|
CREATE TABLE paper(
	_id INTEGER NOT NULL,
	author VARCHAR,
	title VARCHAR,
	filename VARCHAR,
	upload_date DATE,
	uploader_id INTEGER,
	PRIMARY KEY (_id),
	CONSTRAINT paper_unique_constraint UNIQUE (author, title),
	FOREIGN KEY(uploader_id) REFERENCES user (_id)
)
|
INSERT INTO paper SELECT * FROM paper_tmp;
|
DROP TABLE paper_tmp;
|
ALTER TABLE paper ADD COLUMN url VARCHAR
'''

for stmt in sql.split('|'):
    cursor.execute(stmt.strip())

try:
    conn.commit()
except IntegrityError:
    conn.rollback()

conn.close()


