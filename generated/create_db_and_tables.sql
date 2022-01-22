CREATE DATABASE generated_db;
USE generated_db;
CREATE TABLE `Books` (
	`isbn` varchar(100) NOT NULL, 
	`title` varchar(100) NOT NULL, 
	`year_of_publishing` int(11) NOT NULL, 
	PRIMARY KEY (`isbn`), 
	UNIQUE KEY `books_un_1` (`title`, `year_of_publishing`)
);

