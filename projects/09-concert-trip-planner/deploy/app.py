import os
from datetime import date, datetime, time, timedelta

import mysql.connector
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db_connection():
    """Create and return a MySQL connection using .env settings."""
    try:
        db_host = os.getenv("DB_HOST")
        db_port = int(os.getenv("DB_PORT", 3307))
        db_database = os.getenv("DB_DATABASE")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            database=db_database,
            user=db_user,
            password=db_password,
        )
        return conn
    except Exception as e:
        print(f"!!! MySQL Database Connection FAILED !!! Error: {e}")
        return None


def generate_next_user_id(conn):

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MAX(UserId) AS max_id FROM `USER` WHERE UserId LIKE 'USR%'")
        result = cursor.fetchone()
        cursor.close()

        max_id = result.get("max_id")
        if max_id:
            current_num = int(max_id[3:])
            next_num = current_num + 1
        else:
            next_num = 1

        return f"USR{next_num:05d}"
    except Exception as e:
        print(f"Error generating UserId: {e}")
        return None


def generate_next_trip_id(conn):

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT MAX(TripId) AS max_id FROM TRIP")
        result = cursor.fetchone()
        cursor.close()

        max_id = result.get("max_id")
        if max_id:
            current_num = int(max_id)
            next_num = current_num + 1
        else:
            next_num = 1
        return next_num
    except Exception as e:
        print(f"Error generating TripId: {e}")
        return None



@app.route("/")
def home_page():
    # templates/auth/login.html
    return render_template("auth/login.html")


@app.route("/index")
def index_page():
    return render_template("search/index.html")


@app.route("/concerts")
def concerts_page():
    return render_template("search/concert.html")

@app.route("/concerts/detail")
def concert_detail_page():
    return render_template("search/concert_detail.html")

@app.route("/itinerary")
def itinerary_page():
    return render_template("itinerary/itinerary.html")


@app.route("/itinerary/hotel")
def hotel_page():
    return render_template("itinerary/hotel.html")


@app.route("/itinerary/saved")
def saved_itinerary_page():
    return render_template("itinerary/saved.html")


@app.route("/community")
def community_page():
    return render_template("community/community.html")



@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json() or {}

    phone_num = data.get("username", "").strip()
    password = data.get("password", "").strip()
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()

    if not all([phone_num, password, first_name, last_name]):
        return jsonify({"message": "Missing required fields."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT 1 FROM `USER` WHERE Phone = %s", (phone_num,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"message": "Phone number already registered."}), 409

        new_id = generate_next_user_id(conn)
        if new_id is None:
            raise Exception("Failed to generate user ID.")

        cursor.execute(
            "INSERT INTO `USER` (UserId, Phone, `Password`, FirstName, LastName) "
            "VALUES (%s, %s, %s, %s, %s)",
            (new_id, phone_num, password, first_name, last_name),
        )
        conn.commit()
        cursor.close()

        return (
            jsonify(
                {
                    "message": "User registered successfully.",
                    "userId": new_id,
                    "firstName": first_name,
                }
            ),
            201,
        )
    except Exception as e:
        conn.rollback()
        print(f"!!! Error during registration: {e} !!!")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}

    phone_num = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not phone_num or not password:
        return jsonify({"message": "Login ID and password are required."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT UserId, FirstName, LastName
            FROM `USER`
            WHERE Phone = %s AND `Password` = %s
        """
        cursor.execute(sql, (phone_num, password))
        print(">>> Executed SQL:", cursor.statement)

        user = cursor.fetchone()
        cursor.close()

        if user:
            return (
                jsonify(
                    {
                        "message": "Login successful.",
                        "userId": user["UserId"],
                        "firstName": user["FirstName"],
                    }
                ),
                200,
            )
        else:
            return jsonify({"message": "Invalid login ID or password."}), 401
    except Exception as e:
        print(f"!!! Error during login query: {e} !!!")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()



def serialize_concert(row):
    event_date = row.get("EventDate")
    event_time = row.get("EventTime")

    if isinstance(event_date, (date, datetime)):
        event_date_str = event_date.isoformat()
    else:
        event_date_str = str(event_date) if event_date is not None else None

    if isinstance(event_time, time):
        event_time_str = event_time.strftime("%H:%M:%S")
    elif isinstance(event_time, timedelta):
        event_time_str = str(event_time)
    else:
        event_time_str = str(event_time) if event_time is not None else None

    return {
        "EventId": row.get("EventId"),
        "EventName": row.get("EventName"),
        "EventDate": event_date_str,
        "EventTime": event_time_str,
        "City": row.get("City"),
        "URL": row.get("URL"),  # ticket link
    }


@app.route("/api/concerts", methods=["GET"])
def search_concerts():
    location = (request.args.get("location") or "").strip()
    search_date = (request.args.get("date") or "").strip()

    if not location or not search_date:
        return (
            jsonify({"message": "Location and date parameters are required for search."}),
            400,
        )

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                E.EventId,
                E.EventName,
                E.EventDate,
                E.EventTime,
                V.City,
                E.URL
            FROM EVENT E
            JOIN VENUE V ON E.VenueId = V.VenueId
            WHERE V.City LIKE %s
              AND E.EventDate = %s
        """
        cursor.execute(sql, (f"%{location}%", search_date))
        rows = cursor.fetchall()
        cursor.close()

        concerts = [serialize_concert(r) for r in rows]

        return (
            jsonify(
                {
                    "concerts": concerts,
                    "count": len(concerts),
                    "search_params": {
                        "location": location,
                        "date": search_date,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        print(f"Error during concert search query: {e}")
        return jsonify({"message": f"Server error executing search: {e}"}), 500
    finally:
        conn.close()


@app.route("/api/itinerary", methods=["POST"])
def add_itinerary_item():
    data = request.get_json() or {}
    user_id = data.get("userId")
    event_id = data.get("eventId")
    hotel_code = data.get("hotelCode")  # optional
    user_note = data.get("note")  # optional
    visibility = data.get("visibility", 1)  # default public

    print(">>> /api/itinerary payload:", data)

    if not user_id or not event_id:
        return jsonify({"message": "Missing userId or eventId."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)


        cursor.execute(
            "SELECT EventDate, EventTime FROM EVENT WHERE EventId = %s",
            (event_id,),
        )
        event = cursor.fetchone()

        if not event:
            cursor.close()
            return jsonify({"message": f"EventId {event_id} not found."}), 404

        cursor.execute(
            "SELECT TripId FROM TRIP WHERE UserId = %s AND EventId = %s",
            (user_id, event_id),
        )
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            return jsonify(
                {"message": "Trip already exists", "tripId": existing["TripId"]}, 409
            )

        trip_id = generate_next_trip_id(conn)
        if trip_id is None:
            cursor.close()
            return jsonify({"message": "Failed to generate TripId."}), 500

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO TRIP (
                TripId, UserId, EventId, StartDate, StartTime,
                HotelCode, UserNote, Visibility
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                trip_id,
                user_id,
                event_id,
                event["EventDate"],
                event["EventTime"],
                hotel_code,
                user_note,
                visibility,
            ),
        )
        conn.commit()
        cursor.close()

        print(f">>> Added TRIP: TripId={trip_id}, UserId={user_id}, EventId={event_id}")

        return (
            jsonify({"message": "Event successfully added to your trip!", "tripId": trip_id}),
            201,
        )
    except Exception as e:
        conn.rollback()
        print(">>> Error adding TRIP:", e)
        return jsonify({"message": f"Error adding TRIP item: {e}"}), 500
    finally:
        conn.close()


@app.route("/api/itineraries/<user_id>", methods=["GET"])
def get_user_itineraries(user_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                T.TripId,
                E.EventName,
                E.EventDate,
                V.City,
                T.UserNote,
                T.Visibility,
                H.Name AS HotelName
            FROM TRIP T
            JOIN EVENT E ON T.EventId = E.EventId
            JOIN VENUE V ON E.VenueId = V.VenueId
            LEFT JOIN HOTEL H ON T.HotelCode = H.HotelCode
            WHERE T.UserId = %s
        """
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        cursor.close()

        return jsonify({"itineraries": rows, "count": len(rows)}), 200
    except Exception as e:
        print(f"Error fetching itineraries: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


@app.route("/api/users/<user_id>/trip_stats", methods=["GET"])
def get_user_trip_stats(user_id):

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:

        cursor = conn.cursor()
        cursor.callproc("sp_get_user_trip_stats", [user_id])

        total_trips = 0
        public_trips = 0
        distinct_cities = 0
        first_trip_date = None
        last_trip_date = None

        for result in cursor.stored_results():
            row = result.fetchone()
            if row:
                # from the stored procedure
                # SELECT
                #   COUNT(*) AS total_trips,
                #   SUM(CASE WHEN T.Visibility = 1 THEN 1 ELSE 0 END) AS public_trips,
                #   COUNT(DISTINCT V.City) AS distinct_cities,
                #   MIN(T.StartDate) AS first_trip_date,
                #   MAX(T.StartDate) AS last_trip_date
                total_trips, public_trips, distinct_cities, first_trip_date, last_trip_date = row
            break

        cursor.close()


        if total_trips is None:
            total_trips = 0
        if public_trips is None:
            public_trips = 0
        if distinct_cities is None:
            distinct_cities = 0

        return jsonify({
            "userId": user_id,
            "total_trips": int(total_trips or 0),
            "public_trips": int(public_trips or 0),
            "distinct_cities": int(distinct_cities or 0),
            "first_trip_date": first_trip_date,
            "last_trip_date": last_trip_date,
        }), 200

    except Exception as e:
        print(f"Error fetching stats for user {user_id}:", e)
        return jsonify({"message": "Error fetching user trip stats."}), 500
    finally:
        conn.close()



@app.route("/api/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TRIP WHERE TripId = %s", (trip_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": f"Trip {trip_id} not found."}), 404

        return jsonify({"message": f"Trip {trip_id} deleted."}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error deleting trip {trip_id}: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()

@app.route('/api/trips/<int:trip_id>/visibility', methods=['PUT'])
def update_trip_visibility(trip_id):

    data = request.get_json() or {}
    visibility = data.get('visibility', None)


    if visibility in ['0', '1']:
        visibility = int(visibility)

    if visibility not in (0, 1):
        return jsonify({"message": "Invalid visibility, must be 0 or 1."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor()


        cursor.execute("SELECT 1 FROM TRIP WHERE TripId = %s", (trip_id,))
        exists = cursor.fetchone()
        if not exists:
            cursor.close()
            return jsonify({"message": f"Trip {trip_id} not found."}), 404


        cursor.execute(
            "UPDATE TRIP SET Visibility = %s WHERE TripId = %s",
            (visibility, trip_id)
        )
        conn.commit()
        cursor.close()


        cursor = conn.cursor()
        cursor.execute("SELECT Visibility FROM TRIP WHERE TripId = %s", (trip_id,))
        row = cursor.fetchone()
        cursor.close()

        actual_visibility = int(row[0]) if row and row[0] is not None else 0

        msg = "Visibility updated."

        if visibility == 1 and actual_visibility == 0:
            msg = ("Visibility attempted set to Public, "
                   "but the rule forced it to Private (missing hotel or short note).")

        return jsonify({
            "message": msg,
            "visibility": actual_visibility
        }), 200

    except Exception as e:
        conn.rollback()
        print(f"Error updating visibility for trip {trip_id}: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


@app.route("/api/trips/<int:trip_id>", methods=["PUT"])
def update_trip(trip_id):
    data = request.get_json() or {}
    user_note = data.get("userNote", "")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE TRIP SET UserNote = %s WHERE TripId = %s", (user_note, trip_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": f"Trip {trip_id} not found."}), 404

        return jsonify({"message": f"Trip {trip_id} updated."}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error updating trip {trip_id}: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


@app.route("/api/hotels/<event_id>", methods=["GET"])
def get_hotels_for_event(event_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT 
                E.EventName,
                E.EventDate,
                E.EventTime,
                V.VenueName,
                V.City
            FROM EVENT E
            JOIN VENUE V ON E.VenueId = V.VenueId
            WHERE E.EventId = %s
        """,
            (event_id,),
        )
        event = cursor.fetchone()

        if not event:
            cursor.close()
            return jsonify({"message": f"EventId {event_id} not found."}), 404

        target_city = event["City"]
        event_name = event["EventName"]
        venue_name = event["VenueName"]
        event_date = event["EventDate"]
        event_time = event["EventTime"]

        cursor.execute(
            """
            SELECT 
                HotelCode,
                Name,
                City,
                Address,
                StarRating,
                URL
            FROM HOTEL
            WHERE City = %s
        """,
            (target_city,),
        )
        hotel_rows = cursor.fetchall()
        cursor.close()

        hotels = [
            {
                "HotelCode": h["HotelCode"],
                "Name": h["Name"],
                "City": h["City"],
                "Address": h["Address"],
                "StarRating": h.get("StarRating"),
                "URL": h.get("URL"),
            }
            for h in hotel_rows
        ]

        event_time_str = str(event_time) if event_time is not None else ""
        venue_info = f"Venue: {venue_name} | Date: {event_date} | Time: {event_time_str}"

        return (
            jsonify(
                {
                    "event_name": event_name,
                    "venue_info": venue_info,
                    "target_city": target_city,
                    "hotels": hotels,
                    "count": len(hotels),
                }
            ),
            200,
        )
    except Exception as e:
        print(f"Error fetching hotels for event {event_id}: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


@app.route("/api/hotel/<int:hotel_code>", methods=["GET"])
def get_hotel_by_code(hotel_code):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                HotelCode,
                Name,
                City,
                Address,
                StarRating,
                URL
            FROM HOTEL
            WHERE HotelCode = %s
        """,
            (hotel_code,),
        )
        row = cursor.fetchone()
        cursor.close()

        if not row:
            return jsonify({"message": f"Hotel {hotel_code} not found."}), 404

        return jsonify(row), 200
    except Exception as e:
        print(f"Error fetching hotel {hotel_code}: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


@app.route("/api/events/<event_id>", methods=["GET"])
def get_event_detail(event_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                E.EventId,
                E.EventName,
                E.EventDate,
                E.EventTime,
                E.URL AS TicketURL,
                V.VenueName,
                V.City,
                V.State
            FROM EVENT E
            JOIN VENUE V ON E.VenueId = V.VenueId
            WHERE E.EventId = %s
        """,
            (event_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        if not row:
            return jsonify({"message": f"Event {event_id} not found."}), 404

        # Format date
        event_date = row["EventDate"]
        if isinstance(event_date, (date, datetime)):
            event_date_str = event_date.isoformat()
        else:
            event_date_str = str(event_date) if event_date else None

        # Format time
        event_time = row["EventTime"]
        if isinstance(event_time, time):
            event_time_str = event_time.strftime("%H:%M:%S")
        else:
            event_time_str = str(event_time) if event_time else None

        return jsonify({
            "EventId": row["EventId"],
            "EventName": row["EventName"],
            "EventDate": event_date_str,
            "EventTime": event_time_str,
            "VenueName": row["VenueName"],
            "City": row["City"],
            "State": row["State"],
            "URL": row["TicketURL"]  # ⭐ include ticket URL here!
        }), 200

    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()




@app.route("/api/trips/community", methods=["GET"])
def get_community_trips():
    city = (request.args.get("city") or "").strip()
    artist = (request.args.get("artist") or "").strip()

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor(dictionary=True)

        base_sql = """
            SELECT
                T.TripId,
                U.FirstName,
                U.LastName,
                E.EventName,
                E.EventDate,
                V.VenueName,
                V.City AS VenueCity,
                H.Name AS HotelName,
                H.StarRating,
                T.UserNote
            FROM TRIP T
            JOIN `USER` U ON T.UserId = U.UserId
            JOIN EVENT E ON T.EventId = E.EventId
            JOIN VENUE V ON E.VenueId = V.VenueId
            LEFT JOIN HOTEL H ON T.HotelCode = H.HotelCode
            WHERE T.Visibility = 1
        """

        params = []
        if city:
            base_sql += " AND V.City LIKE %s"
            params.append(f"%{city}%")
        if artist:
            base_sql += " AND E.EventName LIKE %s"
            params.append(f"%{artist}%")

        base_sql += " ORDER BY E.EventDate DESC"

        cursor.execute(base_sql, tuple(params))
        trips = cursor.fetchall()
        cursor.close()

        return jsonify({"trips": trips, "count": len(trips)}), 200
    except Exception as e:
        print(f"Error fetching community trips: {e}")
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


@app.route("/api/trips/<int:trip_id>/copy", methods=["POST"])
def copy_trip_to_user(trip_id):

    data = request.get_json() or {}
    target_user_id = data.get("userId")

    if not target_user_id:
        return jsonify({"message": "Missing userId in request body."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection failed."}), 503

    try:
        cursor = conn.cursor()
        args = [trip_id, target_user_id, 0, 0]
        result_args = cursor.callproc("sp_copy_public_trip_to_user", args)
        conn.commit()
        cursor.close()

        new_trip_id = result_args[2]
        status_code = result_args[3]

        if status_code == 1:
            return (
                jsonify(
                    {"message": f"Public Trip {trip_id} not found or not public."}
                ),
                404,
            )
        elif status_code == 2:
            return (
                jsonify(
                    {
                        "message": "You already have this event in your trips.",
                        "tripId": new_trip_id,
                    }
                ),
                409,
            )
        else:
            return (
                jsonify(
                    {
                        "message": f"Trip {trip_id} copied to user {target_user_id}.",
                        "tripId": new_trip_id,
                    }
                ),
                201,
            )
    except Exception as e:
        conn.rollback()
        print(f"Error copying trip {trip_id}:", e)
        return jsonify({"message": "An internal server error occurred."}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    # debug=False for any deployed/public run — Flask's debug mode ships an
    # interactive debugger that allows arbitrary code execution on an
    # unhandled exception. Production serving is via gunicorn (see
    # Procfile), which imports `app` directly and never hits this block,
    # but this stays safe if anyone runs `python app.py` directly too.
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

