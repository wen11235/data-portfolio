-- ============================================================
-- CS 411 Project - Schema (DDL)
-- Team: DataDucks / Team 092
-- ============================================================

CREATE TABLE USER (
    UserId VARCHAR(20) PRIMARY KEY,
    Password VARCHAR(20) NOT NULL,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Phone VARCHAR(15)
);

CREATE TABLE VENUE (
    VenueId VARCHAR(20) PRIMARY KEY,
    VenueName VARCHAR(255),
    Address VARCHAR(255),
    City VARCHAR(50),
    State VARCHAR(20),
    Zipcode CHAR(5)
);

CREATE TABLE EVENT (
    EventId VARCHAR(20) PRIMARY KEY,
    VenueId VARCHAR(20),
    EventName VARCHAR(255),
    URL VARCHAR(2083),
    EventDate DATE,
    EventTime TIME,
    FOREIGN KEY (VenueId) REFERENCES VENUE(VenueId) ON DELETE CASCADE
);

CREATE TABLE HOTEL (
    HotelCode INT PRIMARY KEY,
    Name VARCHAR(255),
    State VARCHAR(20),
    City VARCHAR(50),
    Address VARCHAR(255),
    Zipcode CHAR(5),
    StarRating INT,
    URL VARCHAR(2083)
);

CREATE TABLE REVIEW (
    ReviewId INT NOT NULL,
    HotelCode INT NOT NULL,
    Title VARCHAR(255),
    Content TEXT,
    CommentDate DATE,
    Rating DECIMAL(2,1),
    PRIMARY KEY (ReviewId, HotelCode),
    FOREIGN KEY (HotelCode) REFERENCES HOTEL(HotelCode) ON DELETE CASCADE
);

CREATE TABLE TRIP (
    TripId INT PRIMARY KEY,
    UserId VARCHAR(20) NOT NULL,
    HotelCode INT NULL,
    EventId VARCHAR(20) NOT NULL,
    StartDate DATE,
    StartTime TIME,
    UserNote TEXT,
    Visibility BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (UserId) REFERENCES USER(UserId) ON DELETE CASCADE,
    FOREIGN KEY (HotelCode) REFERENCES HOTEL(HotelCode) ON DELETE SET NULL,
    FOREIGN KEY (EventId) REFERENCES EVENT(EventId) ON DELETE CASCADE
);

CREATE TABLE SAVE (
    UserId VARCHAR(20) NOT NULL,
    TripId INT NOT NULL,
    PRIMARY KEY (UserId, TripId),
    FOREIGN KEY (UserId) REFERENCES USER(UserId) ON DELETE CASCADE,
    FOREIGN KEY (TripId) REFERENCES TRIP(TripId) ON DELETE CASCADE
);

-- Location modeled as Address + Zipcode + City + State rather than
-- Latitude/Longitude — the original design used lat/long, which implied a
-- functional dependency (Latitude, Longitude) -> (State, City) and left the
-- schema short of 3NF. Revised to the current design during Stage 2 review.
