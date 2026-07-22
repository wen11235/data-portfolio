-- ============================================================
-- ConcertNOW — full setup script for a fresh db4free.net database
-- Run this against the database db4free.net creates for you at signup
-- (no CREATE DATABASE here — db4free already provisions one per account).
--
-- Recommended: run via a real MySQL client, not phpMyAdmin's web SQL box —
-- the DELIMITER blocks for triggers/procedures are more reliable there.
--   mysql -h db4free.net -P 3306 -u YOUR_USER -p YOUR_DB_NAME < setup.sql
-- ============================================================

-- ---------- 1. Schema ----------

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

-- ---------- 2. Triggers ----------

DROP TRIGGER IF EXISTS trg_trip_visibility_before_insert;
DROP TRIGGER IF EXISTS trg_trip_visibility_before_update;

DELIMITER $$

CREATE TRIGGER trg_trip_visibility_before_insert
BEFORE INSERT ON TRIP
FOR EACH ROW
BEGIN
    IF NEW.HotelCode IS NULL
       OR NEW.UserNote IS NULL
       OR CHAR_LENGTH(NEW.UserNote) < 20 THEN
        SET NEW.Visibility = 0;
    END IF;
END$$

CREATE TRIGGER trg_trip_visibility_before_update
BEFORE UPDATE ON TRIP
FOR EACH ROW
BEGIN
    IF NEW.HotelCode IS NULL
       OR NEW.UserNote IS NULL
       OR CHAR_LENGTH(NEW.UserNote) < 20 THEN
        SET NEW.Visibility = 0;
    END IF;
END$$

DELIMITER ;

-- ---------- 3. Stored procedures ----------

DROP PROCEDURE IF EXISTS sp_get_user_trip_stats;

DELIMITER $$

CREATE PROCEDURE sp_get_user_trip_stats(IN p_user_id VARCHAR(20))
BEGIN
    SELECT
        COUNT(*) AS total_trips,
        SUM(CASE WHEN T.Visibility = 1 THEN 1 ELSE 0 END) AS public_trips,
        COUNT(DISTINCT V.City) AS distinct_cities,
        MIN(T.StartDate) AS first_trip_date,
        MAX(T.StartDate) AS last_trip_date
    FROM TRIP T
    JOIN EVENT E ON T.EventId = E.EventId
    JOIN VENUE V ON E.VenueId = V.VenueId
    WHERE T.UserId = p_user_id;
END$$

DELIMITER ;

DROP PROCEDURE IF EXISTS sp_copy_public_trip_to_user;

DELIMITER $$

CREATE PROCEDURE sp_copy_public_trip_to_user(
    IN  p_source_trip_id INT,
    IN  p_target_user_id VARCHAR(20),
    OUT p_new_trip_id INT,
    OUT p_status_code INT
)
BEGIN
    DECLARE v_event_id   VARCHAR(20);
    DECLARE v_start_date DATE;
    DECLARE v_start_time TIME;
    DECLARE v_hotel_code INT;
    DECLARE v_user_note  TEXT;

    SET p_new_trip_id = NULL;
    SET p_status_code = 0;

    SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
    START TRANSACTION;

    SELECT
        T.EventId, T.StartDate, T.StartTime, T.HotelCode, T.UserNote
    INTO
        v_event_id, v_start_date, v_start_time, v_hotel_code, v_user_note
    FROM TRIP T
    JOIN EVENT E ON T.EventId = E.EventId
    WHERE T.TripId = p_source_trip_id
      AND T.Visibility = 1
    FOR UPDATE;

    IF v_event_id IS NULL THEN
        SET p_status_code = 1;
        ROLLBACK;
    ELSEIF EXISTS (
        SELECT 1 FROM TRIP WHERE UserId = p_target_user_id AND EventId = v_event_id
    ) THEN
        SET p_status_code = 2;
        ROLLBACK;
    ELSE
        SELECT COALESCE(MAX(TripId), 0) + 1 INTO p_new_trip_id FROM TRIP;

        INSERT INTO TRIP (
            TripId, UserId, EventId, StartDate, StartTime,
            HotelCode, UserNote, Visibility
        ) VALUES (
            p_new_trip_id, p_target_user_id, v_event_id, v_start_date,
            v_start_time, v_hotel_code, v_user_note, 0
        );

        COMMIT;
        SET p_status_code = 0;
    END IF;
END$$

DELIMITER ;

-- ---------- 4. Seed data (small, realistic demo dataset) ----------

INSERT INTO VENUE (VenueId, VenueName, Address, City, State, Zipcode) VALUES
('V001', 'The Fillmore', '1805 Geary Blvd', 'San Francisco', 'CA', '94115'),
('V002', 'Red Rocks Amphitheatre', '18300 W Alameda Pkwy', 'Morrison', 'CO', '80465'),
('V003', 'Brooklyn Steel', '319 Frost St', 'Brooklyn', 'NY', '11222'),
('V004', 'House of Blues', '329 N Dearborn St', 'Chicago', 'IL', '60654');

INSERT INTO EVENT (EventId, VenueId, EventName, URL, EventDate, EventTime) VALUES
('E001', 'V001', 'Phoebe Bridgers: Reunion Tour', 'https://example.com/e1', '2026-08-02', '20:00:00'),
('E002', 'V001', 'Clairo Live', 'https://example.com/e2', '2026-08-05', '19:30:00'),
('E003', 'V002', 'Tame Impala', 'https://example.com/e3', '2026-08-09', '19:00:00'),
('E004', 'V003', 'Beach House', 'https://example.com/e4', '2026-08-03', '20:30:00'),
('E005', 'V004', 'Japanese Breakfast', 'https://example.com/e5', '2026-08-07', '19:00:00');

INSERT INTO HOTEL (HotelCode, Name, State, City, Address, Zipcode, StarRating, URL) VALUES
(1001, 'Hotel Zephyr', 'CA', 'San Francisco', '250 Beach St', '94133', 4, 'https://example.com/h1'),
(1002, 'Kimpton Buchanan', 'CA', 'San Francisco', '1800 Sutter St', '94115', 4, 'https://example.com/h2'),
(1003, 'The Maven Hotel', 'CO', 'Morrison', '1101 Wynkoop St', '80202', 4, 'https://example.com/h3'),
(1004, 'William Vale', 'NY', 'Brooklyn', '111 N 12th St', '11249', 5, 'https://example.com/h4');

INSERT INTO REVIEW (ReviewId, HotelCode, Title, Content, CommentDate, Rating) VALUES
(1, 1001, 'Great location', 'Walkable to everything, clean rooms.', '2026-05-01', 4.5),
(2, 1001, 'Solid stay', 'Friendly staff, a bit noisy at night.', '2026-05-10', 4.0),
(1, 1002, 'Loved it', 'Beautiful boutique hotel near the venue.', '2026-04-20', 4.8),
(1, 1004, 'Amazing views', 'Rooftop bar and great service.', '2026-06-01', 4.9);

-- Demo login: 5551234567 / demo1234
INSERT INTO USER (UserId, Password, FirstName, LastName, Phone) VALUES
('USR00001', 'demo1234', 'Jordan', 'Rivera', '5551234567');

INSERT INTO TRIP (TripId, UserId, HotelCode, EventId, StartDate, StartTime, UserNote, Visibility) VALUES
(1, 'USR00001', 1002, 'E001', '2026-08-02', '20:00:00', 'Going with friends for Phoebe Bridgers, staying near the venue and grabbing dinner beforehand.', 1),
(2, 'USR00001', 1004, 'E004', '2026-08-03', '20:30:00', 'Beach House in Brooklyn, booked the William Vale for the rooftop view.', 1);
