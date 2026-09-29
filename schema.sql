CREATE DATABASE IF NOT EXISTS code_relay
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE code_relay;

CREATE TABLE IF NOT EXISTS teams (
 id INT AUTO_INCREMENT PRIMARY KEY,
 team_name VARCHAR(100) NOT NULL,
 member1 VARCHAR(100) NOT NULL,
 member2 VARCHAR(100) NOT NULL,
 login_code VARCHAR(50) UNIQUE NOT NULL,
 active TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS questions (
 id INT AUTO_INCREMENT PRIMARY KEY,
 round_no INT NOT NULL,
 title VARCHAR(200) NOT NULL,
 description TEXT NOT NULL,
 active TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS submissions (
 id INT AUTO_INCREMENT PRIMARY KEY,
 team_id INT NOT NULL,
 question_id INT NOT NULL,
 member VARCHAR(100) NOT NULL,
 code LONGTEXT NOT NULL,
 elapsed_seconds INT DEFAULT 0,
 submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(team_id) REFERENCES teams(id),
 FOREIGN KEY(question_id) REFERENCES questions(id),
 UNIQUE KEY one_submission(team_id, question_id)
);

CREATE TABLE IF NOT EXISTS event_control (
 id INT PRIMARY KEY,
 round_no INT DEFAULT 1,
 phase VARCHAR(30) DEFAULT 'waiting',
 status VARCHAR(30) DEFAULT 'waiting',
 phase_started_at DATETIME NULL
);

INSERT IGNORE INTO event_control(id) VALUES (1);

INSERT IGNORE INTO teams(team_name,member1,member2,login_code) VALUES
('Team A','Rohith','Arun','TEAM001'),
('Team B','Kumar','Vasanth','TEAM002'),
('Team C','Ajay','Ravi','TEAM003'),
('Team D','Hari','Bala','TEAM004');

INSERT IGNORE INTO questions(round_no,title,description) VALUES
(1,'Second Largest Number','Write a program to find the second largest number in an array.'),
(2,'Palindrome Check','Write a program to check whether a given string is a palindrome.');
