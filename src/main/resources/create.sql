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
)

CREATE TABLE Availabilities (
    Time date,  -- date is a discrete time point.
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255), -- Vaccine avaliability doesn't depend on the caregiver.
    Doses int,
    PRIMARY KEY (Name)
);