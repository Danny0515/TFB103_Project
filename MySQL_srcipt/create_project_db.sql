CREATE DATABASE IF NOT EXISTS tfb1031_project;
USE tfb1031_project;

CREATE TABLE restaurant
(
  res_id			INT NOT NULL,
  res_name			VARCHAR(255) NOT NULL,
  address			VARCHAR(255),
  content			LONGTEXT,
  score				FLOAT,
  price 			FLOAT,
  article_url		VARCHAR(255),
  image_url			TEXT,
  tag				TEXT,
  CONSTRAINT res_PK PRIMARY KEY (res_id)
) ENGINE = INNODB;

CREATE TABLE bnb
(
  bnb_id			INT NOT NULL,
  bnb_name			VARCHAR(100) NOT NULL,
  bnb_url			TEXT,
  star				INT,
  price 			INT,
  address			VARCHAR(255),
  origin_feature	TEXT,
  score				FLOAT,
  image_url			TEXT,
  city				VARCHAR(10),
  x					FLOAT(20),
  y					FLOAT(20),
  CONSTRAINT bnb_PK PRIMARY KEY (bnb_id)
) ENGINE = INNODB;

CREATE TABLE author_feature
(
  aut_id			INT NOT NULL,
  author			VARCHAR(40) NOT NULL,
  tag				TEXT,
  CONSTRAINT autFeature_PK PRIMARY KEY (aut_id)
) ENGINE = INNODB;

CREATE TABLE bnb_article
(
  bnb_art_id		INT NOT NULL,
  title				VARCHAR(225),
  content			LONGTEXT,
  date				DATE,
  art_url			VARCHAR(255),
  image_url			TEXT,
  aut_id			INT,
  bnb_id			INT,
  CONSTRAINT bnbArticle_PK PRIMARY KEY (bnb_art_id),
  CONSTRAINT bnbArticle_bub_aut_id_FK FOREIGN KEY (aut_id) REFERENCES author_feature (aut_id) ON UPDATE CASCADE ,
  CONSTRAINT bnbArticle_bnb_id_FK FOREIGN KEY (bnb_id) REFERENCES bnb (bnb_id) ON UPDATE CASCADE 
  ) ENGINE = INNODB;
  
