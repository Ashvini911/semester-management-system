CREATE DATABASE  IF NOT EXISTS `semester_mgt` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `semester_mgt`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: semester_mgt
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `academic_staff_member`
--

DROP TABLE IF EXISTS `academic_staff_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `academic_staff_member` (
  `Staff_ID` varchar(10) NOT NULL,
  `First_Name` varchar(50) NOT NULL,
  `Last_Name` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Contact_No` varchar(15) DEFAULT NULL,
  `Staff_Type` enum('LECTURER','VISITING','INTERNAL') NOT NULL,
  `Employment` enum('PERMANENT','TEMPORARY') DEFAULT NULL,
  `Timetable_ID` int DEFAULT NULL,
  PRIMARY KEY (`Staff_ID`),
  UNIQUE KEY `Email` (`Email`),
  KEY `Timetable_ID` (`Timetable_ID`),
  CONSTRAINT `academic_staff_member_ibfk_1` FOREIGN KEY (`Timetable_ID`) REFERENCES `time_table` (`Timetable_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `academic_staff_member`
--

LOCK TABLES `academic_staff_member` WRITE;
/*!40000 ALTER TABLE `academic_staff_member` DISABLE KEYS */;
INSERT INTO `academic_staff_member` VALUES ('ST001','Nuwan','Perera','nuwan@example.com','0711234567','LECTURER','PERMANENT',1),('ST002','Kumari','Silva','kumari@example.com','0771234567','INTERNAL','PERMANENT',2);
/*!40000 ALTER TABLE `academic_staff_member` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ar_officer`
--

DROP TABLE IF EXISTS `ar_officer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ar_officer` (
  `Email` varchar(100) NOT NULL,
  PRIMARY KEY (`Email`),
  CONSTRAINT `ar_officer_ibfk_1` FOREIGN KEY (`Email`) REFERENCES `users` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ar_officer`
--

LOCK TABLES `ar_officer` WRITE;
/*!40000 ALTER TABLE `ar_officer` DISABLE KEYS */;
INSERT INTO `ar_officer` VALUES ('ar@example.com');
/*!40000 ALTER TABLE `ar_officer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clerk`
--

DROP TABLE IF EXISTS `clerk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clerk` (
  `Email` varchar(100) NOT NULL,
  PRIMARY KEY (`Email`),
  CONSTRAINT `clerk_ibfk_1` FOREIGN KEY (`Email`) REFERENCES `users` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clerk`
--

LOCK TABLES `clerk` WRITE;
/*!40000 ALTER TABLE `clerk` DISABLE KEYS */;
INSERT INTO `clerk` VALUES ('clerk@example.com');
/*!40000 ALTER TABLE `clerk` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `Course_Code` varchar(10) NOT NULL,
  `Course_Name` varchar(100) NOT NULL,
  `Credit` tinyint NOT NULL,
  `Semester_ID` varchar(10) NOT NULL,
  PRIMARY KEY (`Course_Code`),
  KEY `idx_course_sem` (`Semester_ID`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`Semester_ID`) REFERENCES `semester` (`Semester_ID`),
  CONSTRAINT `course_chk_1` CHECK ((`Credit` between 1 and 6))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` VALUES ('ICT1306','Object Oriented Programming',2,'SEM1'),('ICT1402','Principles of Programming',1,'SEM2'),('ICT1407','Database Systems',1,'SEM1');
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dean`
--

DROP TABLE IF EXISTS `dean`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dean` (
  `Email` varchar(100) NOT NULL,
  PRIMARY KEY (`Email`),
  CONSTRAINT `dean_ibfk_1` FOREIGN KEY (`Email`) REFERENCES `users` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dean`
--

LOCK TABLES `dean` WRITE;
/*!40000 ALTER TABLE `dean` DISABLE KEYS */;
INSERT INTO `dean` VALUES ('dean@example.com');
/*!40000 ALTER TABLE `dean` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `degree`
--

DROP TABLE IF EXISTS `degree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `degree` (
  `Degree_Name` varchar(100) NOT NULL,
  `Credit` smallint NOT NULL,
  `Duration` tinyint NOT NULL,
  `Dep_Name` varchar(100) NOT NULL,
  PRIMARY KEY (`Degree_Name`),
  KEY `Dep_Name` (`Dep_Name`),
  CONSTRAINT `degree_ibfk_1` FOREIGN KEY (`Dep_Name`) REFERENCES `department` (`Dep_Name`),
  CONSTRAINT `degree_chk_1` CHECK ((`Credit` > 0)),
  CONSTRAINT `degree_chk_2` CHECK ((`Duration` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `degree`
--

LOCK TABLES `degree` WRITE;
/*!40000 ALTER TABLE `degree` DISABLE KEYS */;
INSERT INTO `degree` VALUES ('BSc Information Technology',120,4,'Computing');
/*!40000 ALTER TABLE `degree` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `demonstrator`
--

DROP TABLE IF EXISTS `demonstrator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `demonstrator` (
  `Demonstrator_ID` int NOT NULL AUTO_INCREMENT,
  `First_Name` varchar(50) NOT NULL,
  `Last_Name` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Contact_No` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`Demonstrator_ID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `demonstrator`
--

LOCK TABLES `demonstrator` WRITE;
/*!40000 ALTER TABLE `demonstrator` DISABLE KEYS */;
INSERT INTO `demonstrator` VALUES (1,'Kasun','Perera','kasun@example.com','0714567890'),(2,'Nadeesha','Silva','nadeesha@example.com','0774567890');
/*!40000 ALTER TABLE `demonstrator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `demonstrator_requirement`
--

DROP TABLE IF EXISTS `demonstrator_requirement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `demonstrator_requirement` (
  `Demonstrator_ID` int NOT NULL,
  `Requirement_ID` int NOT NULL,
  PRIMARY KEY (`Demonstrator_ID`,`Requirement_ID`),
  KEY `Requirement_ID` (`Requirement_ID`),
  CONSTRAINT `demonstrator_requirement_ibfk_1` FOREIGN KEY (`Demonstrator_ID`) REFERENCES `demonstrator` (`Demonstrator_ID`),
  CONSTRAINT `demonstrator_requirement_ibfk_2` FOREIGN KEY (`Requirement_ID`) REFERENCES `requirement` (`Requirement_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `demonstrator_requirement`
--

LOCK TABLES `demonstrator_requirement` WRITE;
/*!40000 ALTER TABLE `demonstrator_requirement` DISABLE KEYS */;
INSERT INTO `demonstrator_requirement` VALUES (1,1),(2,2);
/*!40000 ALTER TABLE `demonstrator_requirement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `Dep_Name` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  PRIMARY KEY (`Dep_Name`),
  KEY `Email` (`Email`),
  CONSTRAINT `department_ibfk_1` FOREIGN KEY (`Email`) REFERENCES `hod` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES ('Computing','hod@example.com');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam`
--

DROP TABLE IF EXISTS `exam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam` (
  `Exam_ID` int NOT NULL AUTO_INCREMENT,
  `Semester_ID` varchar(10) NOT NULL,
  `Course_Code` varchar(10) NOT NULL,
  `Type` varchar(30) NOT NULL,
  `Date` date NOT NULL,
  `Time` time NOT NULL,
  PRIMARY KEY (`Exam_ID`),
  KEY `Semester_ID` (`Semester_ID`),
  KEY `Course_Code` (`Course_Code`),
  KEY `idx_exam_date` (`Date`),
  CONSTRAINT `exam_ibfk_1` FOREIGN KEY (`Semester_ID`) REFERENCES `semester` (`Semester_ID`),
  CONSTRAINT `exam_ibfk_2` FOREIGN KEY (`Course_Code`) REFERENCES `course` (`Course_Code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam`
--

LOCK TABLES `exam` WRITE;
/*!40000 ALTER TABLE `exam` DISABLE KEYS */;
INSERT INTO `exam` VALUES (1,'SEM1','ICT1407','Midterm','2026-09-10','09:00:00'),(2,'SEM1','ICT1306','Final','2026-12-10','09:00:00');
/*!40000 ALTER TABLE `exam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hod`
--

DROP TABLE IF EXISTS `hod`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hod` (
  `Email` varchar(100) NOT NULL,
  PRIMARY KEY (`Email`),
  CONSTRAINT `hod_ibfk_1` FOREIGN KEY (`Email`) REFERENCES `users` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hod`
--

LOCK TABLES `hod` WRITE;
/*!40000 ALTER TABLE `hod` DISABLE KEYS */;
INSERT INTO `hod` VALUES ('hod@example.com');
/*!40000 ALTER TABLE `hod` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lecture`
--

DROP TABLE IF EXISTS `lecture`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lecture` (
  `Lecture_ID` int NOT NULL AUTO_INCREMENT,
  `Course_Code` varchar(10) NOT NULL,
  `Staff_ID` varchar(10) NOT NULL,
  `Venue_No` varchar(10) NOT NULL,
  `Moderator_Email` varchar(100) DEFAULT NULL,
  `Date` date NOT NULL,
  `Time` time NOT NULL,
  `Mode` enum('Physical','Online') NOT NULL,
  PRIMARY KEY (`Lecture_ID`),
  KEY `Venue_No` (`Venue_No`),
  KEY `Moderator_Email` (`Moderator_Email`),
  KEY `idx_lecture_course` (`Course_Code`),
  KEY `idx_lecture_staff` (`Staff_ID`),
  CONSTRAINT `lecture_ibfk_1` FOREIGN KEY (`Course_Code`) REFERENCES `course` (`Course_Code`),
  CONSTRAINT `lecture_ibfk_2` FOREIGN KEY (`Staff_ID`) REFERENCES `academic_staff_member` (`Staff_ID`),
  CONSTRAINT `lecture_ibfk_3` FOREIGN KEY (`Venue_No`) REFERENCES `venue` (`Venue_No`),
  CONSTRAINT `lecture_ibfk_4` FOREIGN KEY (`Moderator_Email`) REFERENCES `moderator` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lecture`
--

LOCK TABLES `lecture` WRITE;
/*!40000 ALTER TABLE `lecture` DISABLE KEYS */;
INSERT INTO `lecture` VALUES (1,'ICT1407','ST001','V001','mod@example.com','2026-08-10','09:00:00','Physical'),(2,'ICT1306','ST002','V002','mod@example.com','2026-08-11','10:00:00','Physical');
/*!40000 ALTER TABLE `lecture` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `moderator`
--

DROP TABLE IF EXISTS `moderator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `moderator` (
  `Email` varchar(100) NOT NULL,
  `First_Name` varchar(50) NOT NULL,
  `Last_Name` varchar(50) NOT NULL,
  `Contact_No` varchar(15) DEFAULT NULL,
  `Official_Address` varchar(200) DEFAULT NULL,
  `Designation` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `moderator`
--

LOCK TABLES `moderator` WRITE;
/*!40000 ALTER TABLE `moderator` DISABLE KEYS */;
INSERT INTO `moderator` VALUES ('mod@example.com','Anusha','Perera','0719876543','Anuradhapura','Senior Lecturer');
/*!40000 ALTER TABLE `moderator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `requirement`
--

DROP TABLE IF EXISTS `requirement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `requirement` (
  `Requirement_ID` int NOT NULL AUTO_INCREMENT,
  `Requirement_Name` varchar(100) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Requirement_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `requirement`
--

LOCK TABLES `requirement` WRITE;
/*!40000 ALTER TABLE `requirement` DISABLE KEYS */;
INSERT INTO `requirement` VALUES (1,'Computer Skills','Basic computer knowledge required'),(2,'Programming Skills','Basic programming knowledge required');
/*!40000 ALTER TABLE `requirement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `second_examiner`
--

DROP TABLE IF EXISTS `second_examiner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `second_examiner` (
  `Email` varchar(100) NOT NULL,
  `Moderator_Email` varchar(100) NOT NULL,
  PRIMARY KEY (`Email`),
  KEY `Moderator_Email` (`Moderator_Email`),
  CONSTRAINT `second_examiner_ibfk_1` FOREIGN KEY (`Moderator_Email`) REFERENCES `moderator` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `second_examiner`
--

LOCK TABLES `second_examiner` WRITE;
/*!40000 ALTER TABLE `second_examiner` DISABLE KEYS */;
INSERT INTO `second_examiner` VALUES ('examiner@example.com','mod@example.com');
/*!40000 ALTER TABLE `second_examiner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semester`
--

DROP TABLE IF EXISTS `semester`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semester` (
  `Semester_ID` varchar(10) NOT NULL,
  `Academic_Year` varchar(9) NOT NULL,
  `Start_Date` date NOT NULL,
  `End_Date` date NOT NULL,
  PRIMARY KEY (`Semester_ID`),
  CONSTRAINT `semester_chk_1` CHECK ((`End_Date` > `Start_Date`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semester`
--

LOCK TABLES `semester` WRITE;
/*!40000 ALTER TABLE `semester` DISABLE KEYS */;
INSERT INTO `semester` VALUES ('SEM1','2026/2027','2026-07-13','2026-12-31'),('SEM2','2026/2027','2027-01-15','2027-06-30');
/*!40000 ALTER TABLE `semester` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_table`
--

DROP TABLE IF EXISTS `time_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `time_table` (
  `Timetable_ID` int NOT NULL AUTO_INCREMENT,
  `Semester_ID` varchar(10) NOT NULL,
  `Year` varchar(9) NOT NULL,
  `Place` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`Timetable_ID`),
  KEY `Semester_ID` (`Semester_ID`),
  CONSTRAINT `time_table_ibfk_1` FOREIGN KEY (`Semester_ID`) REFERENCES `semester` (`Semester_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_table`
--

LOCK TABLES `time_table` WRITE;
/*!40000 ALTER TABLE `time_table` DISABLE KEYS */;
INSERT INTO `time_table` VALUES (1,'SEM1','2026/2027','FAS'),(2,'SEM2','2026/2027','FAS');
/*!40000 ALTER TABLE `time_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `Email` varchar(100) NOT NULL,
  `First_Name` varchar(50) NOT NULL,
  `Last_Name` varchar(50) NOT NULL,
  `Username` varchar(50) NOT NULL,
  `Password_Hash` varchar(255) NOT NULL,
  `Role` enum('AR_OFFICER','HOD','DEAN','CLERK') NOT NULL,
  PRIMARY KEY (`Email`),
  UNIQUE KEY `Username` (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('ar@example.com','Amali','Perera','amali_ar','hash_ar_123','AR_OFFICER'),('clerk@example.com','Saman','Kumara','saman_clerk','hash_clerk_123','CLERK'),('dean@example.com','Nimal','Fernando','nimal_dean','hash_dean_123','DEAN'),('hod@example.com','Kamal','Silva','kamal_hod','hash_hod_123','HOD');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_exam_schedule`
--

DROP TABLE IF EXISTS `v_exam_schedule`;
/*!50001 DROP VIEW IF EXISTS `v_exam_schedule`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_exam_schedule` AS SELECT 
 1 AS `Course_Code`,
 1 AS `Type`,
 1 AS `Date`,
 1 AS `Time`,
 1 AS `Academic_Year`,
 1 AS `Semester_ID`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_lecture_timetable`
--

DROP TABLE IF EXISTS `v_lecture_timetable`;
/*!50001 DROP VIEW IF EXISTS `v_lecture_timetable`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_lecture_timetable` AS SELECT 
 1 AS `Course_Code`,
 1 AS `Course_Name`,
 1 AS `Date`,
 1 AS `Time`,
 1 AS `Mode`,
 1 AS `Lecturer`,
 1 AS `Venue_Name`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `venue`
--

DROP TABLE IF EXISTS `venue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venue` (
  `Venue_No` varchar(10) NOT NULL,
  `Venue_Name` varchar(100) NOT NULL,
  `Capacity` smallint NOT NULL,
  `Floor` tinyint DEFAULT NULL,
  `Building` varchar(50) DEFAULT NULL,
  `Venue_Type` enum('LAB','LECTURE_HALL') NOT NULL,
  PRIMARY KEY (`Venue_No`),
  CONSTRAINT `venue_chk_1` CHECK ((`Capacity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venue`
--

LOCK TABLES `venue` WRITE;
/*!40000 ALTER TABLE `venue` DISABLE KEYS */;
INSERT INTO `venue` VALUES ('V001','Lecture Hall 1',100,1,'Main Building','LECTURE_HALL'),('V002','Computer Lab 1',40,2,'IT Building','LAB');
/*!40000 ALTER TABLE `venue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'semester_mgt'
--

--
-- Final view structure for view `v_exam_schedule`
--

/*!50001 DROP VIEW IF EXISTS `v_exam_schedule`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_exam_schedule` AS select `exam`.`Course_Code` AS `Course_Code`,`exam`.`Type` AS `Type`,`exam`.`Date` AS `Date`,`exam`.`Time` AS `Time`,`semester`.`Academic_Year` AS `Academic_Year`,`semester`.`Semester_ID` AS `Semester_ID` from (`exam` join `semester` on((`exam`.`Semester_ID` = `semester`.`Semester_ID`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_lecture_timetable`
--

/*!50001 DROP VIEW IF EXISTS `v_lecture_timetable`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_lecture_timetable` AS select `course`.`Course_Code` AS `Course_Code`,`course`.`Course_Name` AS `Course_Name`,`lecture`.`Date` AS `Date`,`lecture`.`Time` AS `Time`,`lecture`.`Mode` AS `Mode`,concat(`academic_staff_member`.`First_Name`,' ',`academic_staff_member`.`Last_Name`) AS `Lecturer`,`venue`.`Venue_Name` AS `Venue_Name` from (((`lecture` join `course` on((`lecture`.`Course_Code` = `course`.`Course_Code`))) join `academic_staff_member` on((`lecture`.`Staff_ID` = `academic_staff_member`.`Staff_ID`))) left join `venue` on((`lecture`.`Venue_No` = `venue`.`Venue_No`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 20:28:50
