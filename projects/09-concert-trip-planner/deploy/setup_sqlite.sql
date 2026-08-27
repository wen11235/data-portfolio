-- ============================================================
-- ConcertNOW — SQLite schema + seed data.
--
-- Used when no free-tier MySQL host is available/reliable (see the "Live
-- deployment" note in README.md — freesqldatabase.com expired the account
-- about a week after signup). SQLite needs no external service at all: the
-- database is a single file, created automatically by app.py on first
-- request if it doesn't already exist (see init_db() in app.py).
--
-- Two things SQLite can't do that the full MySQL version can (see
-- setup.sql): stored procedures and real row-level locking. Both are
-- reimplemented at the application layer in app.py — sp_get_user_trip_stats
-- and sp_copy_public_trip_to_user as plain Python functions running the
-- same SQL, same as how the trigger logic was already handled for the
-- MySQL free-tier deployment (compute_enforced_visibility()). The original,
-- unmodified trigger/procedure SQL is unchanged in code/ and setup.sql.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ---------- 1. Schema ----------

DROP TABLE IF EXISTS SAVE;
DROP TABLE IF EXISTS TRIP;
DROP TABLE IF EXISTS REVIEW;
DROP TABLE IF EXISTS EVENT;
DROP TABLE IF EXISTS HOTEL;
DROP TABLE IF EXISTS VENUE;
DROP TABLE IF EXISTS USER;

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
    Visibility BOOLEAN NOT NULL DEFAULT 1,
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

-- ---------- 2. Seed data (small, realistic demo dataset) ----------

INSERT INTO VENUE (VenueId, VenueName, Address, City, State, Zipcode) VALUES
('V001', 'The Fillmore', '1805 Geary Blvd', 'San Francisco', 'CA', '94115'),
('V002', 'Red Rocks Amphitheatre', '18300 W Alameda Pkwy', 'Morrison', 'CO', '80465'),
('V003', 'Brooklyn Steel', '319 Frost St', 'Brooklyn', 'NY', '11222'),
('V004', 'House of Blues', '329 N Dearborn St', 'Chicago', 'IL', '60654');

INSERT INTO EVENT (EventId, VenueId, EventName, URL, EventDate, EventTime) VALUES
('E001', 'V001', 'Phoebe Bridgers: Reunion Tour', 'https://example.com/e1', '2026-10-02', '20:00:00'),
('E002', 'V001', 'Clairo Live', 'https://example.com/e2', '2026-10-05', '19:30:00'),
('E003', 'V002', 'Tame Impala', 'https://example.com/e3', '2026-10-09', '19:00:00'),
('E004', 'V003', 'Beach House', 'https://example.com/e4', '2026-10-03', '20:30:00'),
('E005', 'V004', 'Japanese Breakfast', 'https://example.com/e5', '2026-10-07', '19:00:00');

INSERT INTO HOTEL (HotelCode, Name, State, City, Address, Zipcode, StarRating, URL) VALUES
(1001, 'Hotel Zephyr', 'CA', 'San Francisco', '250 Beach St', '94133', 4, 'https://example.com/h1'),
(1002, 'Kimpton Buchanan', 'CA', 'San Francisco', '1800 Sutter St', '94115', 4, 'https://example.com/h2'),
(1003, 'The Maven Hotel', 'CO', 'Morrison', '1101 Wynkoop St', '80202', 4, 'https://example.com/h3'),
(1004, 'William Vale', 'NY', 'Brooklyn', '111 N 12th St', '11249', 5, 'https://example.com/h4');

INSERT INTO REVIEW (ReviewId, HotelCode, Title, Content, CommentDate, Rating) VALUES
(1, 1001, 'Great location', 'Walkable to everything, clean rooms.', '2026-08-01', 4.5),
(2, 1001, 'Solid stay', 'Friendly staff, a bit noisy at night.', '2026-08-10', 4.0),
(1, 1002, 'Loved it', 'Beautiful boutique hotel near the venue.', '2026-07-20', 4.8),
(1, 1004, 'Amazing views', 'Rooftop bar and great service.', '2026-09-01', 4.9);

-- Demo login: 5551234567 / demo1234
INSERT INTO USER (UserId, Password, FirstName, LastName, Phone) VALUES
('USR00001', 'demo1234', 'Jordan', 'Rivera', '5551234567');

INSERT INTO TRIP (TripId, UserId, HotelCode, EventId, StartDate, StartTime, UserNote, Visibility) VALUES
(1, 'USR00001', 1002, 'E001', '2026-10-02', '20:00:00', 'Going with friends for Phoebe Bridgers, staying near the venue and grabbing dinner beforehand.', 1),
(2, 'USR00001', 1004, 'E004', '2026-10-03', '20:30:00', 'Beach House in Brooklyn, booked the William Vale for the rooftop view.', 1);
