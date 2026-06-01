-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: May 25, 2025 at 09:58 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `migrant_connect`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`username`, `password`) VALUES
('admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `employer_register`
--

CREATE TABLE `employer_register` (
  `id` int(11) NOT NULL auto_increment,
  `company_name` varchar(255) default NULL,
  `employer_name` varchar(255) default NULL,
  `email` varchar(255) default NULL,
  `contact` varchar(20) default NULL,
  `username` varchar(100) default NULL,
  `password` varchar(255) default NULL,
  `registered_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `photo` varchar(255) default NULL,
  `designation` varchar(100) default NULL,
  `address` text,
  `location` varchar(100) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `employer_register`
--

INSERT INTO `employer_register` (`id`, `company_name`, `employer_name`, `email`, `contact`, `username`, `password`, `registered_at`, `photo`, `designation`, `address`, `location`) VALUES
(2, 'Sangeethas', 'Sam', 'muthu.s@themind.co.in', '6379572469', 'sam', '1234', '2025-05-24 18:28:51', 'sam_person_4-min.jpg', 'Manager', 'Trichy', 'Chatram');

-- --------------------------------------------------------

--
-- Table structure for table `migrant_register`
--

CREATE TABLE `migrant_register` (
  `id` int(11) NOT NULL auto_increment,
  `migrant_id` varchar(10) NOT NULL,
  `name` varchar(100) default NULL,
  `aadhar` varchar(12) NOT NULL,
  `email` varchar(100) default NULL,
  `contact` varchar(20) default NULL,
  `dob` date default NULL,
  `gender` varchar(10) default NULL,
  `nationality` varchar(50) default NULL,
  `district` varchar(50) default NULL,
  `state` varchar(50) default NULL,
  `country` varchar(50) default NULL,
  `occupation` varchar(100) default NULL,
  `language` varchar(100) default NULL,
  `skills` varchar(100) default NULL,
  `username` varchar(50) default NULL,
  `password` varchar(255) default NULL,
  `address` text,
  `id_proof` varchar(255) default NULL,
  `photo` varchar(255) default NULL,
  `registered_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `status` int(11) default NULL,
  `otp` varchar(20) NOT NULL,
  `verified` tinyint(1) default '0',
  `current_address` text,
  `pin` varchar(10) default NULL,
  `aadhar_proof` varchar(255) default NULL,
  `pan_proof` varchar(255) default NULL,
  `ration_proof` varchar(255) default NULL,
  `qr_filename` varchar(255) default NULL,
  `verification_status` varchar(20) default 'pending',
  `job_status` varchar(20) default 'pending',
  `work_latitude` varchar(100) default NULL,
  `work_longitude` varchar(100) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `migrant_id` (`migrant_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `migrant_register`
--

INSERT INTO `migrant_register` (`id`, `migrant_id`, `name`, `aadhar`, `email`, `contact`, `dob`, `gender`, `nationality`, `district`, `state`, `country`, `occupation`, `language`, `skills`, `username`, `password`, `address`, `id_proof`, `photo`, `registered_at`, `status`, `otp`, `verified`, `current_address`, `pin`, `aadhar_proof`, `pan_proof`, `ration_proof`, `qr_filename`, `verification_status`, `job_status`, `work_latitude`, `work_longitude`) VALUES
(8, 'STGKV1952R', 'Kanniyan', '422618106028', 'muthu.s@themind.co.in', '6379572469', '2025-05-05', 'Male', 'India', 'Cuddalore', 'Rajasathan', 'India', 'Labour', 'English, Hindi', NULL, 'kanniyan', '1234', 'Rajasthan', NULL, 'photo_kanniyan_person_6-min.jpg', '2025-05-24 14:55:01', 1, '9245', 0, 'Chennai', '607106', 'aadhar_kanniyan_a4.jpg', 'pan_kanniyan_pan.jpeg', 'ration_kanniyan_ration.jpg', 'mid_qr_8.png', 'verified', 'hired', '10.955012', '76.976689');

-- --------------------------------------------------------

--
-- Table structure for table `scheme_applications`
--

CREATE TABLE `scheme_applications` (
  `id` int(11) NOT NULL auto_increment,
  `migrant_id` varchar(20) default NULL,
  `scheme_id` int(11) default NULL,
  `applied_at` datetime default NULL,
  `status` varchar(20) default 'Pending',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `scheme_applications`
--

INSERT INTO `scheme_applications` (`id`, `migrant_id`, `scheme_id`, `applied_at`, `status`) VALUES
(1, 'kanniyan', 1, '2025-05-25 12:00:05', 'Approved');

-- --------------------------------------------------------

--
-- Table structure for table `welfare_schemes`
--

CREATE TABLE `welfare_schemes` (
  `id` int(11) NOT NULL auto_increment,
  `scheme_name` varchar(255) default NULL,
  `type` varchar(100) default NULL,
  `description` text,
  `eligibility` text,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `welfare_schemes`
--

INSERT INTO `welfare_schemes` (`id`, `scheme_name`, `type`, `description`, `eligibility`) VALUES
(1, 'Railway Track substution', 'Employment', '100 days of guaranteed construction work', 'All migrant laborers');
