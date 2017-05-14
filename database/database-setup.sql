/*
	DB Schema for SP

	cd /SP-db
	in terminal:
		mysql -u root < database-setup.sql
*/

/* CREATES USER for SP and GRANT privileges */
DROP USER IF EXISTS 'aggregator'@'localhost';
CREATE USER 'aggregator'@'localhost' IDENTIFIED BY 'aggregator';

/* CREATES Database newsDB */
DROP DATABASE IF EXISTS newsDB;
CREATE DATABASE newsDB;
USE newsDB;

GRANT ALL PRIVILEGES ON newsDB.* TO 'aggregator'@'localhost';

/* 	CREATES TABLE for USER and ADMIN
 *	User types: 0 - subscriber, 1 - admin */
/*CREATE TABLE IF NOT EXISTS USER (
	user_id INT(4) NOT NULL AUTO_INCREMENT,
	is_admin BIT(1) NOT NULL,
	email varchar(64) NOT NULL,
	PRIMARY KEY (user_id)
); */

CREATE TABLE IF NOT EXISTS ADMIN (
	admin_id INT(4) NOT NULL AUTO_INCREMENT,
	name varchar (64) NOT NULL,
	email varchar(64) NOT NULL UNIQUE,
	username varchar(64) NOT NULL,
	password varchar(20) NOT NULL,
	PRIMARY KEY (admin_id)
);

/* CREATE TABLE for News */
CREATE TABLE IF NOT EXISTS NEWS (
	news_id INT(4) NOT NULL AUTO_INCREMENT,
	title char(255) NOT NULL UNIQUE,
	category varchar(64),
	author varchar(64) NOT NULL,
	link varchar(255) NOT NULL,
	introText text NOT NULL, 
	image varchar(255),
/*	datePub varchar(40) NOT NULL */
	PRIMARY KEY (news_id)
);


/*	POPULATE TABLES	*/
/*	Insert initial admin users	*/
INSERT INTO ADMIN ( name, email, username, password )
	VALUES 
	( 
		'Janel de Ramos', 'joderamos@up.edu.ph', 'joderamos', 'joderamos'
	),
	(
		'Chelseah Blaquera', 'mnblaquera@up.edu.ph', 'mnblaquera', 'mnblaquera'
	)
