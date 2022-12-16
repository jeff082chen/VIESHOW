CREATE DATABASE SEDB;
USE SEDB;
CREATE TABLE Cinema_information (
  Cinema_id             VARCHAR(45)     NOT NULL,
  Cinema_name           VARCHAR(45)     NULL,
  Cinema_address        VARCHAR(45)     NULL,
  Cinema_tel            VARCHAR(45)     NULL,
  Cinema_intro          TEXT            NULL,
  Cinema_traffic_info   TEXT            NULL,
  PRIMARY KEY (Cinema_id)
  );

CREATE TABLE member_account (
  account_id    VARCHAR(45) NOT NULL,
  account       VARCHAR(45) NOT NULL,
  password      VARCHAR(45) NOT NULL,
  PRIMARY KEY ( account_id , account , password )
  );

CREATE TABLE member_information (
  info_id               VARCHAR(45) NOT NULL,
  info_email            VARCHAR(45) NULL,
  info_phone            VARCHAR(45) NULL,
  info_birthday         VARCHAR(45) NULL,
  info_point            VARCHAR(45) NULL,
  info_creditcardnum    VARCHAR(45) NULL,
  PRIMARY KEY (info_id)
  );

CREATE TABLE movie_place (
  movie_place_id	VARCHAR(45) NOT NULL,
  movie_place		VARCHAR(45) NULL,
  PRIMARY KEY (movie_place_id)
  );

CREATE TABLE movie_time (
  mo_time_id	VARCHAR(45) NOT NULL,
  mo_time		DATETIME	NOT NULL,
  PRIMARY KEY (mo_time_id, mo_time)
  );

CREATE TABLE movie_version (
  mo_version_id     VARCHAR(45) NOT NULL,
  mo_version		VARCHAR(45) NOT NULL,
  PRIMARY KEY (mo_version_id)
  );

CREATE TABLE rec_food (
  food_id       VARCHAR(45)  NOT NULL,
  popcorn       VARCHAR(45)  NOT NULL,
  drink         VARCHAR(45)  NOT NULL,
  other         VARCHAR(45)  NOT NULL,
  PRIMARY KEY (food_id, popcorn, drink, other)
  );

CREATE TABLE rec_ticket (
  ticket_id        	VARCHAR(45) NOT NULL,
  ticket_type       VARCHAR(45) NULL,
  ticket_price      VARCHAR(45) NULL,
  rec_ticket        VARCHAR(45) NULL,
  rec_food_id		VARCHAR(45) NULL,
  PRIMARY KEY (ticket_id),
  FOREIGN KEY (rec_food_id) REFERENCES sedb.rec_food (food_id)
  );
  
  CREATE TABLE movie_limit_stage (
  movie_limit_stage_id		VARCHAR(45)  NOT NULL,
  movie_limit_stage			VARCHAR(45)  NULL,
  PRIMARY KEY (movie_limit_stage_id)
  );
  
 CREATE TABLE movie_type (
  movie_type_id		VARCHAR(45)  NOT NULL,
  movie_type		VARCHAR(45)  NULL,
  PRIMARY KEY (movie_type_id)
  );
  
  CREATE TABLE member (
  member_id             VARCHAR(45) NOT NULL,
  member_information_id VARCHAR(45) NOT NULL,
  member_rec_id         VARCHAR(45) NOT NULL,
  member_account_id     VARCHAR(45) NOT NULL,
  PRIMARY KEY (member_id, member_information_id, member_rec_id, member_account_id),
  FOREIGN KEY (member_account_id)REFERENCES sedb.member_account (account_id),
  FOREIGN KEY (member_information_id) REFERENCES sedb.member_information (info_id),
  FOREIGN KEY (member_rec_id) REFERENCES sedb.rec_ticket (ticket_id)
  );

  CREATE TABLE movie (
  movie_name 		VARCHAR(45) NOT NULL,
  movie_lim_id 		VARCHAR(45) NOT NULL,
  movie_place_id 	VARCHAR(45) NOT NULL,
  movie_time_id 	VARCHAR(45) NOT NULL,
  movie_version 	VARCHAR(45) NOT NULL,
  movie_type 		VARCHAR(45) NOT NULL,
  PRIMARY KEY (movie_name, movie_lim_id, movie_place_id, movie_time_id, movie_version, movie_type),
  FOREIGN KEY (movie_lim_id) REFERENCES sedb.movie_limit_stage (movie_limit_stage_id),
  FOREIGN KEY (movie_place_id) REFERENCES sedb.movie_place (movie_place_id),
  FOREIGN KEY (movie_time_id) REFERENCES sedb.movie_time (mo_time_id),
  FOREIGN KEY (movie_version) REFERENCES sedb.movie_version (mo_version_id),
  FOREIGN KEY (movie_type) REFERENCES sedb.movie_type (movie_type_id)
	);
