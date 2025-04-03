CREATE DATABASE melon_chart;

USE melon_chart;
SELECT user, host FROM mysql.user;

CREATE TABLE chart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `rank` INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL
);
show tables; #테이블 목록 확인
DESCRIBE chart; #특정 테이블 구조 확인.