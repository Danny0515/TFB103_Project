USE tfb1031_project;

### user_info
INSERT INTO user_info VALUES('U8a6e3915313149a9d5b445862b79725a', '使用者1', 'Female', null, now());
INSERT INTO user_info VALUES('U8a6e3915313149a9d5b445862b79726a', '使用者2', 'Female', null, now());
INSERT INTO user_info VALUES('U8a6e3915313149a9d5b445862b79727a', '使用者3', 'Male', null, now());
INSERT INTO user_info VALUES('U8a6e3915313149a9d5b445862b79728a', '使用者4', 'Male', null, now());
INSERT INTO user_info VALUES('U8a6e3915313149a9d5b445862b79729a', '使用者5', 'Female', null, now());

### user_questionnaire
INSERT INTO user_questionnaire 
	VALUES(50000001, 'U8a6e3915313149a9d5b445862b79725a', 10000001, 'groupA', 20000001, 20000);
INSERT INTO user_questionnaire 
	VALUES(50000002, 'U8a6e3915313149a9d5b445862b79726a', 10000002, 'groupB', 20000002, 40000);
INSERT INTO user_questionnaire 
	VALUES(50000003, 'U8a6e3915313149a9d5b445862b79727a', 10000003, 'groupC', 20000003, 60000);
INSERT INTO user_questionnaire 
	VALUES(50000004, 'U8a6e3915313149a9d5b445862b79727a', 10000004, 'groupD', 20000004, 80000);
INSERT INTO user_questionnaire 
	VALUES(50000005, 'U8a6e3915313149a9d5b445862b79729a', 10000005, 'groupE', 20000005, 100000);

### res_recommend_w2v
INSERT INTO res_recommend_w2v VALUES(92000001, 20000001, 20000011, 0.97, 20000021, 0.88, 20000031, 0.86);
INSERT INTO res_recommend_w2v VALUES(92000002, 20000002, 20000012, 0.95, 20000022, 0.60, 20000032, 0.59);
INSERT INTO res_recommend_w2v VALUES(92000003, 20000003, 20000013, 0.93, 20000023, 0.89, 20000033, 0.74);
INSERT INTO res_recommend_w2v VALUES(92000004, 20000004, 20000014, 0.98, 20000024, 0.91, 20000034, 0.87);
INSERT INTO res_recommend_w2v VALUES(92000005, 20000005, 20000015, 0.96, 20000025, 0.81, 20000035, 0.79);

### 要刪除再開 (因為有 foreign key 要依序刪除才能執行)
# DELETE from user_info LIMIT 100;
# DELETE from user_questionnaire LIMIT 100;
# DELETE from res_recommend_w2v LIMIT 100;