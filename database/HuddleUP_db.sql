USE `test`;

DROP TABLE IF EXISTS `task_assignee`;
DROP TABLE IF EXISTS `task`;
DROP TABLE IF EXISTS `checklist`;
DROP TABLE IF EXISTS `group_member`;
DROP TABLE IF EXISTS `group`;
DROP TABLE IF EXISTS `user`;

##user profile + login info
CREATE TABLE IF NOT EXISTS `user`(
PK_userID INT(11) NOT NULL AUTO_INCREMENT,
fname VARCHAR(50) NOT NULL,
lname VARCHAR(50) NOT NULL,
userpwd VARCHAR(50) NOT NULL,
email VARCHAR(50) NOT NULL,
PRIMARY KEY(PK_userID)
);

##group attributes
CREATE TABLE IF NOT EXISTS `group`(
PK_groupID INT(11) NOT NULL AUTO_INCREMENT,
group_name VARCHAR(50) NOT NULL,
FK_group_owner INT(11) NOT NULL,
PRIMARY KEY(PK_groupID)
);
ALTER TABLE `group`
ADD FOREIGN KEY(FK_group_owner) REFERENCES `user`(PK_userID);

##junction table for group and user
CREATE TABLE IF NOT EXISTS `group_member`(
PK_gmID INT(11) NOT NULL AUTO_INCREMENT,
FK_memberID INT(11) NOT NULL,
FK_groupID INT(11) NOT NULL,
PRIMARY KEY(PK_gmID)
);
ALTER TABLE `group_member`
ADD FOREIGN KEY(FK_memberID) REFERENCES `user`(PK_userID),
ADD FOREIGN KEY(FK_groupID) REFERENCES `group`(PK_groupID);

##one group can have multiple checklists
CREATE TABLE IF NOT EXISTS `checklist`(
PK_listID INT(11) NOT NULL AUTO_INCREMENT,
FK_groupID INT(11) NOT NULL,
FK_creator INT(11) NOT NULL,
PRIMARY KEY(PK_listID)
);
ALTER TABLE `checklist`
ADD FOREIGN KEY(FK_groupID) REFERENCES `group`(PK_groupID),
ADD FOREIGN KEY(FK_creator) REFERENCES `user`(PK_userID);

##one checklist can have multiple tasks
CREATE TABLE IF NOT EXISTS `task`(
PK_taskID INT(11) NOT NULL AUTO_INCREMENT,
task_title VARCHAR(50) NOT NULL,
task_description TEXT NOT NULL,
FK_task_owner INT(11) NOT NULL,
FK_listID INT(11) NOT NULL,
task_status VARCHAR(50) NOT NULL,
PRIMARY KEY(PK_taskID)
);
ALTER TABLE `task`
ADD FOREIGN KEY(FK_task_owner) REFERENCES `user`(PK_userID),
ADD FOREIGN KEY(FK_listID) REFERENCES `checklist`(PK_listID);

##junction table for task and assignees
CREATE TABLE IF NOT EXISTS `task_assignee`(
PK_taID INT(11) NOT NULL AUTO_INCREMENT,
FK_taskID INT(11) NOT NULL,
FK_assigneeID INT(11) NOT NULL,
PRIMARY KEY(PK_taID)
);
ALTER TABLE `task_assignee`
ADD FOREIGN KEY(FK_taskID) REFERENCES `task`(PK_taskID),
ADD FOREIGN KEY(FK_assigneeID) REFERENCES `user`(PK_userID);


