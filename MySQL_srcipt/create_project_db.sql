CREATE DATABASE IF NOT EXISTS test;
USE test;
-- CREATE DATABASE IF NOT EXISTS tfb1031_project;
-- USE tfb1031_project;

CREATE TABLE restaurant
(
  res_id			VARCHAR(20) NOT NULL,
  res_name			VARCHAR(40) NOT NULL,
  address			VARCHAR(60),
  score				FLOAT,
  price 			SMALLINT,
  content			TEXT(65536),
  article_url		VARCHAR(255),
  image_url			TEXT(65536),
  tag				VARCHAR(255),
  CONSTRAINT res_PK PRIMARY KEY (res_id)
) ENGINE = INNODB;

CREATE TABLE bnb
(
  bnb_id			VARCHAR(20) NOT NULL,
  bnb_name			VARCHAR(40) NOT NULL,
  bnb_url			VARCHAR(255),
  star				VARCHAR(60),
  price 			SMALLINT,
  address			VARCHAR(60),
  origin_feature	VARCHAR(200),
  score				FLOAT,
  map_url			VARCHAR(255),
  image_url			TEXT(65536),
  city				VARCHAR(10),
  x_coordinate		FLOAT(20),
  y_coordinate		FLOAT(20),
  CONSTRAINT bnb_PK PRIMARY KEY (bnb_id)
) ENGINE = INNODB;

CREATE TABLE bnb_author
(
  bnb_aut_id		VARCHAR(20) NOT NULL,
  author			VARCHAR(40) NOT NULL,
  bnb_id			VARCHAR(20),
  tag				VARCHAR(255),
  CONSTRAINT bnbAuthor_PK PRIMARY KEY (bnb_aut_id),
  CONSTRAINT bnbAuthor_bnb_id_FK FOREIGN KEY (bnb_id) REFERENCES bnb (bnb_id)
) ENGINE = INNODB;

CREATE TABLE bnb_article
(
  bnb_art_id		VARCHAR(20) NOT NULL,
  title				VARCHAR(225),
  content			TEXT(65536),
  date				DATE,
  art_url			VARCHAR(255),
  image_url			TEXT(65536),
  bnb_aut_id		VARCHAR(20) NOT NULL,
  bnb_id			VARCHAR(20) NOT NULL,
  CONSTRAINT bnbArticle_PK PRIMARY KEY (bnb_art_id),
  CONSTRAINT bnbArticle_bub_aut_id_FK FOREIGN KEY (bnb_aut_id) REFERENCES bnb_author (bnb_aut_id),
  CONSTRAINT bnbArticle_bnb_id_FK FOREIGN KEY (bnb_id) REFERENCES bnb (bnb_id)
  ) ENGINE = INNODB;
  
  
  