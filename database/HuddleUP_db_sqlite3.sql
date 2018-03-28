DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS group_member;
DROP TABLE IF EXISTS checklist;
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS task_assignee;


CREATE TABLE IF NOT EXISTS user(
PK_userID INTEGER PRIMARY KEY AUTOINCREMENT,
fname VARCHAR NOT NULL,
lname VARCHAR NOT NULL,
userpwd VARCHAR NOT NULL,
email VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS groups(
PK_groupID INTEGER PRIMARY KEY AUTOINCREMENT,
group_name VARCHAR NOT NULL,
FK_group_owner INTEGER NOT NULL,
FOREIGN KEY (FK_group_owner) REFERENCES user(PK_userID)
);

CREATE TABLE IF NOT EXISTS group_member(
PK_gmID INTEGER PRIMARY KEY AUTOINCREMENT,
FK_memberID INTEGER NOT NULL,
FK_groupID INTEGER NOT NULL,
FOREIGN KEY (FK_memberID) REFERENCES user(PK_userID),
FOREIGN KEY (FK_groupID) REFERENCES groups(PK_groupID)
);


CREATE TABLE IF NOT EXISTS checklist(
PK_listID INTEGER PRIMARY KEY AUTOINCREMENT,
FK_groupID INTEGER NOT NULL,
FK_creator INTEGER NOT NULL,
FOREIGN KEY (FK_groupID) REFERENCES groups(PK_groupID),
FOREIGN KEY (FK_creator) REFERENCES user(PK_userID)
);


CREATE TABLE IF NOT EXISTS task(
PK_taskID INTEGER PRIMARY KEY AUTOINCREMENT,
task_title VARCHAR NOT NULL,
task_description TEXT NOT NULL,
FK_task_owner INTEGER NOT NULL,
FK_listID INTEGER NOT NULL,
task_status VARCHAR NOT NULL,
FOREIGN KEY (FK_task_owner) REFERENCES user(PK_userID),
FOREIGN KEY (FK_listID) REFERENCES checklist(PK_listID)
);


CREATE TABLE IF NOT EXISTS task_assignee(
PK_taID INTEGER PRIMARY KEY AUTOINCREMENT,
FK_taskID INTEGER NOT NULL,
FK_assigneeID INTEGER NOT NULL,
FOREIGN KEY (FK_taskID) REFERENCES task(PK_taskID),
FOREIGN KEY (FK_assigneeID) REFERENCES user(PK_userID)
);
