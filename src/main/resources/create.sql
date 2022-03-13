CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients(
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time DATE,  -- date is a discrete time point.
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255), -- Vaccine avaliability doesn't depend on the caregiver.
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Appointments (
    Id INT NOT NULL IDENTITY(1,1),
    PatientName VARCHAR(255) NOT NULL REFERENCES Patients,
    CareGiverName VARCHAR(255) NOT NULL REFERENCES Caregivers,
    AppointmentDate DATE,
    VaccineType VARCHAR(255) NOT NULL REFERENCES Vaccines,
	PRIMARY KEY(Id)
);