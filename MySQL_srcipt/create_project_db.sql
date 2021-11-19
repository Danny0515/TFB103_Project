CREATE DATABASE IF NOT EXISTS tfb1031_project;
USE tfb1031_project;

### For cleaned data
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
  area				VARCHAR(10),
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
  author_group		VARCHAR(20),
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
  

### For LINE bot
CREATE TABLE user_info
(
  user_id			VARCHAR(80) NOT NULL,
  name				VARCHAR(80),
  gender			VARCHAR(6),
  budget			INT,
  sign_in_time		TIMESTAMP,
  CONSTRAINT user_info_PK PRIMARY KEY (user_id)
) ENGINE = INNODB;

CREATE TABLE user_cost
(
  cost_id			INT NOT NULL,
  user_id			VARCHAR(80) NOT NULL,
  cost				INT NOT NULL,
  TIME 				DATETIME,
  item 				VARCHAR(15),
  CONSTRAINT user_cost_PK PRIMARY KEY (cost_id)
) ENGINE = INNODB;

CREATE TABLE user_questionnaire
(
  ques_id			INT NOT NULL,
  user_id			VARCHAR(80) NOT NULL,
  bnb_id			INT NOT NULL,
  bub_grouping		VARCHAR(20) NOT NULL,
  res_id			INT NOT NULL,
  travel_budget 	INT NOT NULL,
  CONSTRAINT ques_PK PRIMARY KEY (ques_id),
  CONSTRAINT ques_FK_user_id FOREIGN KEY (user_id) REFERENCES user_info (user_id) ON UPDATE CASCADE,
  CONSTRAINT ques_FK_bnb_id FOREIGN KEY (bnb_id) REFERENCES bnb (bnb_id) ON UPDATE CASCADE,
  CONSTRAINT ques_FK_restautant_id FOREIGN KEY (res_id) REFERENCES restaurant (res_id) ON UPDATE CASCADE
) ENGINE = INNODB;


### For recommend system
CREATE TABLE bnb_recommend_w2v
(
  bnb_w2v_id		INT NOT NULL,
  bnb_id			INT NOT NULL,
  w2v_first			INT,
  similarity_1		FLOAT,
  w2v_second		INT,
  similarity_2		FLOAT,
  w2v_third			INT,
  similarity_3		FLOAT,
  CONSTRAINT bnb_w2v_PK PRIMARY KEY (bnb_w2v_id),
  CONSTRAINT bnb_w2v_FK_bnb_id FOREIGN KEY (bnb_id) REFERENCES bnb (bnb_id) ON UPDATE CASCADE
) ENGINE = INNODB;

CREATE TABLE res_recommend_w2v
(
  res_w2v_id		INT NOT NULL,
  res_id			INT NOT NULL,
  w2v_first			INT,
  similarity_1		FLOAT,
  w2v_second		INT,
  similarity_2		FLOAT,
  w2v_third			INT,
  similarity_3		FLOAT,
  CONSTRAINT rest_w2v_PK PRIMARY KEY (res_w2v_id),
  CONSTRAINT rest_w2v_FK_restautant_id FOREIGN KEY (res_id) REFERENCES restaurant (res_id) ON UPDATE CASCADE
) ENGINE = INNODB;

### 還沒確定
CREATE TABLE author_recommend_cf
(
  _id				VARCHAR(80) NOT NULL,
  bnb_id			INT NOT NULL,
  bnb_grouping		VARCHAR(20) NOT NULL,
  CONSTRAINT _id_PK PRIMARY KEY (_id),
  CONSTRAINT _FK_bnb_id FOREIGN KEY (bnb_id) REFERENCES bnb (bnb_id) ON UPDATE CASCADE
) ENGINE = INNODB;