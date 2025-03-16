-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 16, 2025 at 07:09 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `exam_scheduler`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `generate_exam_schedule` ()   BEGIN
    -- Example logic to create a schedule based on classroom capacity and availability
    DECLARE done INT DEFAULT FALSE;
    DECLARE c_id INT;
    DECLARE c_name VARCHAR(255);
    DECLARE c_students INT;
    DECLARE c_duration INT;
    DECLARE cur CURSOR FOR SELECT course_id, course_name, students_registered, duration FROM courses;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO c_id, c_name, c_students, c_duration;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Example: Find an available classroom and time slot
        INSERT INTO exam_schedule (course_id, course_name, students_registered, time_slot, classroom_name)
        SELECT c_id, c_name, c_students, '09:00-11:00', classroom_name
        FROM classrooms
        WHERE capacity >= c_students
        LIMIT 1;
    END LOOP;
    CLOSE cur;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `classrooms`
--

CREATE TABLE `classrooms` (
  `classroom_id` varchar(12) DEFAULT NULL,
  `classroom_name` varchar(14) DEFAULT NULL,
  `capacity` varchar(8) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `classrooms`
--

INSERT INTO `classrooms` (`classroom_id`, `classroom_name`, `capacity`) VALUES
('classroom_id', 'classroom_name', 'capacity'),
('1', 'Room A', '100'),
('2', 'Room B', '30'),
('123', 'abc', '20');

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `course_id` varchar(9) DEFAULT NULL,
  `course_name` varchar(11) DEFAULT NULL,
  `students_registered` varchar(19) DEFAULT NULL,
  `duration` varchar(8) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`course_id`, `course_name`, `students_registered`, `duration`) VALUES
('course_id', 'course_name', 'students_registered', 'duration'),
('1', 'Math', '50', '2'),
('2', 'Physics', '30', '2'),
('123', 'abc', '20', '1');

-- --------------------------------------------------------

--
-- Table structure for table `exam_schedule`
--

CREATE TABLE `exam_schedule` (
  `day` varchar(20) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `time_slot` varchar(20) DEFAULT NULL,
  `course_id` int(11) DEFAULT NULL,
  `course_name` varchar(100) DEFAULT NULL,
  `classroom_id` int(11) DEFAULT NULL,
  `classroom_name` varchar(100) DEFAULT NULL,
  `students_registered` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `exam_schedule`
--

INSERT INTO `exam_schedule` (`day`, `date`, `time_slot`, `course_id`, `course_name`, `classroom_id`, `classroom_name`, `students_registered`) VALUES
('Day 1', '2025-03-16', '09:00-11:00', 1, 'Math', 1, 'Room A', 50),
('Day 1', '2025-03-16', '09:00-11:00', 2, 'Physics', 2, 'Room B', 30),
('Day 1', '2025-03-16', '09:00-11:00', 123, 'abc', 123, 'abc', 20);

-- --------------------------------------------------------

--
-- Table structure for table `preferences`
--

CREATE TABLE `preferences` (
  `student_id` varchar(10) DEFAULT NULL,
  `preferred_time_slot` varchar(19) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `preferences`
--

INSERT INTO `preferences` (`student_id`, `preferred_time_slot`) VALUES
('student_id', 'preferred_time_slot'),
('1', 'Morning'),
('2', 'Afternoon');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `student_id` varchar(10) DEFAULT NULL,
  `name` varchar(10) DEFAULT NULL,
  `course_id` varchar(9) DEFAULT NULL,
  `preference` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`student_id`, `name`, `course_id`, `preference`) VALUES
('student_id', 'name', 'course_id', 'preference'),
('1', 'John Doe', '1', 'Morning'),
('2', 'Jane Smith', '2', 'Afternoon'),
('123', 'abc', '456', '12:00-14:0');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
