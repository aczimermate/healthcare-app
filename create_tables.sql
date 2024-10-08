CREATE DATABASE HealthcareAppDB;
GO

USE HealthcareAppDB;
GO

-- Patients Table
CREATE TABLE Patients (
    PatientID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    DateOfBirth DATE,
    Gender CHAR(1),
    ContactNumber VARCHAR(20),
    Email VARCHAR(100),
    RegistrationDate DATE
);
GO

-- Doctors Table
CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Specialization VARCHAR(50),
    EmploymentDate DATE
);
GO

-- Services Table
CREATE TABLE Services (
    ServiceID INT PRIMARY KEY,
    ServiceName VARCHAR(100),
    ServiceCategory VARCHAR(50),
    Cost DECIMAL(10, 2)
);
GO

-- Appointments Table
CREATE TABLE Appointments (
    AppointmentID INT PRIMARY KEY,
    PatientID INT,
    DoctorID INT,
    ServiceID INT,
    AppointmentDateTime DATETIME,
    Status VARCHAR(20),
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID),
    FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID)
);
GO

-- Billing Table
CREATE TABLE Billing (
    BillingID INT PRIMARY KEY,
    AppointmentID INT,
    TotalAmount DECIMAL(10, 2),
    AmountPaid DECIMAL(10, 2),
    PaymentDate DATE,
    PaymentMethod VARCHAR(20),
    FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID)
);
GO

-- Employee Table
CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Role VARCHAR(20),
    EmploymentDate DATE,
    Department VARCHAR(50)
);
GO

-- Feedback Table
CREATE TABLE Feedback (
    FeedbackID INT PRIMARY KEY,
    PatientID INT,
    AppointmentID INT,
    Rating INT,
    Comments TEXT,
    FeedbackDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID)
);
GO

-- Referrals Table
CREATE TABLE Referrals (
    ReferralID INT PRIMARY KEY,
    PatientID INT,
    ReferringPhysician VARCHAR(100),
    ReferralDate DATE,
    Notes TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
GO