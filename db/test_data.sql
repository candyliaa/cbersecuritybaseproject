-- password: qwerty
INSERT INTO student_accounts (username, password) VALUES ('opiskelija1', 'pbkdf2:sha256:260000$HHWL0QFoXWCiMlTE$a3b2c9caf3b3122ac3990e34fc4eaabff1d1c5554ab1c038eb16dd58f253bd0c');
-- password: 12345
INSERT INTO student_accounts (username, password) VALUES ('opiskelija2', 'pbkdf2:sha256:260000$IvRYVAf9fjF4PBt6$a231f057c2347ed6449aa63ac376fe0c7d0b18bfc1cc4ba6dda922672df03a86');

-- password: asdfg
INSERT INTO teacher_accounts (username, password) VALUES ('opettaja1', 'pbkdf2:sha256:260000$4bKOnHM1pM0Sh9Vj$58328dcb69c30b99b7ab4e7080cb68ceb68fa49cf15588bf9ad9578b310ea331');
-- password: 67890
INSERT INTO teacher_accounts (username, password) VALUES ('opettaja2', 'pbkdf2:sha256:260000$8cKJzkyNOD1dPxgM$a6e97ce36f23842a90d5907bf221d6b399198ec9b870dc0cb5ca98088fca2d54');

INSERT INTO courses (name, credits, teacher_id) VALUES ('ohpe', 5, 1);

INSERT INTO course_participants(course_id, student_id) VALUES (1, 1);

INSERT INTO exercises (question, choices, course_id) VALUES ('Mikä on elämän merkitys?', '"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."', 1)
