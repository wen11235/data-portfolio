-- ============================================================
-- CS 411 Project - Stage 4 Advanced Database Features
-- Team: DataDuck
-- Includes:
--   1) Constraints (PK/FK + attribute-level checks)
--   2) Triggers (visibility rules for TRIP)
--   3) Stored Procedure #1: sp_get_user_trip_stats
--   4) Stored Procedure #2 + Transaction: sp_copy_public_trip_to_user
--      (satisfies Transaction + Stored Procedure requirements)
-- ============================================================

-- 1. CONSTRAINTS (We have it in our previous DDL)

-- ===== 1.1 Primary Keys=====
-- ALTER TABLE USER  ADD CONSTRAINT pk_user  PRIMARY KEY (UserId);
-- ALTER TABLE VENUE ADD CONSTRAINT pk_venue PRIMARY KEY (VenueId);
-- ALTER TABLE EVENT ADD CONSTRAINT pk_event PRIMARY KEY (EventId);
-- ALTER TABLE HOTEL ADD CONSTRAINT pk_hotel PRIMARY KEY (HotelCode);
-- ALTER TABLE TRIP  ADD CONSTRAINT pk_trip  PRIMARY KEY (TripId);

-- ===== 1.2 Foreign Keys=====
-- ALTER TABLE EVENT
--   ADD CONSTRAINT fk_event_venue
--   FOREIGN KEY (VenueId) REFERENCES VENUE(VenueId)
--   ON DELETE CASCADE;

-- ALTER TABLE TRIP
--   ADD CONSTRAINT fk_trip_user
--   FOREIGN KEY (UserId) REFERENCES USER(UserId)
--   ON DELETE CASCADE;

-- ALTER TABLE TRIP
--   ADD CONSTRAINT fk_trip_event
--   FOREIGN KEY (EventId) REFERENCES EVENT(EventId)
--   ON DELETE CASCADE;

-- ALTER TABLE TRIP
--   ADD CONSTRAINT fk_trip_hotel
--   FOREIGN KEY (HotelCode) REFERENCES HOTEL(HotelCode)
--   ON DELETE SET NULL;

-- ===== 1.3 Attribute-level / Tuple-level constraints =====

-- ALTER TABLE USER
--   ADD CONSTRAINT uq_user_phone UNIQUE (Phone);

-- ALTER TABLE TRIP
--   ADD CONSTRAINT chk_trip_visibility
--   CHECK (Visibility IN (0, 1));

-- 2. TRIGGERS:  Visibility Rule



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

-- 3. STORED PROCEDURE #1:
--    sp_get_user_trip_stats  (Trip Satatistic Summary)

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

-- 4. STORED PROCEDURE #2 + TRANSACTION:
--    sp_copy_public_trip_to_user


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
        T.EventId,
        T.StartDate,
        T.StartTime,
        T.HotelCode,
        T.UserNote
    INTO
        v_event_id,
        v_start_date,
        v_start_time,
        v_hotel_code,
        v_user_note
    FROM TRIP T
    JOIN EVENT E ON T.EventId = E.EventId
    WHERE T.TripId = p_source_trip_id
      AND T.Visibility = 1
    FOR UPDATE;

    IF v_event_id IS NULL THEN
        SET p_status_code = 1;
        ROLLBACK;

    
    ELSEIF EXISTS (
        SELECT 1
        FROM TRIP
        WHERE UserId = p_target_user_id
          AND EventId = v_event_id
    ) THEN
        SET p_status_code = 2;
        ROLLBACK;

    
    ELSE
        SELECT COALESCE(MAX(TripId), 0) + 1
        INTO p_new_trip_id
        FROM TRIP;

        INSERT INTO TRIP (
            TripId, UserId, EventId, StartDate, StartTime,
            HotelCode, UserNote, Visibility
        ) VALUES (
            p_new_trip_id,
            p_target_user_id,
            v_event_id,
            v_start_date,
            v_start_time,
            v_hotel_code,
            v_user_note,
            0
        );

        COMMIT;
        SET p_status_code = 0;
    END IF;
END$$

DELIMITER ;

