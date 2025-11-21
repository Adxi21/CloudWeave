from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import psycopg2
from database_commands import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, create_event_table, create_date_table, create_admin_table , view_date_table , view_event_table , create_admin_table , insert_admin

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegistrationData(BaseModel):
    event: str
    contactEmail: str
    contactNumber: str
    totalParticipants: int
    participants: List[Dict[str, Any]]

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def setup_database():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(create_event_table)
        cur.execute(create_date_table)
        cur.execute(create_admin_table)
        # Insert default admin if not exists
        cur.execute("INSERT INTO admins (email, name, control_type) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING", 
                   ('aditya2732021@gmail.com', 'Aditya Paranjape', 'Q'))
        conn.commit()
        cur.close()
        conn.close()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database setup error: {e}")

# Setup database on startup
setup_database()

def insertDatePreferences(datePreference, email, contact, name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        for date in datePreference:
            cur.execute("""
                INSERT INTO event_dates (
                    email_id, contact, name, date, morning_tea, morning_coffee,
                    afternoon_tea, afternoon_coffee, breakfast, lunch, dinner,
                    packed_lunch, packed_dinner, departureTime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                email, contact, name,
                date.get("date", ""),
                date.get("morningTea", ""),
                date.get("morningCoffee", ""),
                date.get("afternoonTea", ""),
                date.get("afternoonCoffee", ""),
                date.get("breakfast", False),
                date.get("lunch", False),
                date.get("dinner", False),
                date.get("packedLunch", False),
                date.get("packedDinner", False),
                date.get("departureTime", "")
            ))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Date preferences insert error: {e}")
        return False


def insertParticipantDetails(participant, data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Extract data
        event_name = data.event
        bookers_email = data.contactEmail
        bookers_phone = data.contactNumber
        
        name = participant.get("name", "")
        age = participant.get("age", 0) or 0
        gender = participant.get("gender", "")
        origin = participant.get("origin", "")
        contact = participant.get("contactNumber", "")
        
        dates = participant.get("attendingDates", [])
        travelMode = participant.get("travelMode", "")
        travelDetails = participant.get("travelDetails", {})

        departure_from_home = travelDetails.get("departureFromHome", "")
        arrival_at_venue = travelDetails.get("arrivalAtVenue", "")

        accommodation = participant.get("accommodation", False)
        cot_required = participant.get("cot", False)
        difficultyClimbingStairs = participant.get("difficultyClimbingStairs", False)
        localAssistance = participant.get("localAssistance", False)
        localAssistancePerson = participant.get("localAssistancePerson", "")
        recordings = participant.get("recordings", False)
        recordPrograms = participant.get("recordingPrograms", "")
        specialRequests = participant.get("specialRequests", "")
        datePreferences = participant.get("datePreferences", [])

        # Insert participant data
        cur.execute("""
            INSERT INTO event_registrations (
                bookers_email, bookers_phone, event_name, name, age, gender, origin, contact,
                attending_dates, travelMode, departure_from_home, arrival_at_venue,
                accommodation, cot_required, difficultyClimbingStairs, localAssistance,
                localAssistancePerson, recordings, recordPrograms, specialRequests
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            bookers_email, bookers_phone, event_name, name, age, gender, origin, contact,
            dates, travelMode, departure_from_home, arrival_at_venue,
            accommodation, cot_required, difficultyClimbingStairs, localAssistance,
            localAssistancePerson, recordings, recordPrograms, specialRequests
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Insert date preferences
        insertDatePreferences(datePreferences, bookers_email, contact, name)
        return True
        
    except Exception as e:
        print(f"Participant insert error: {e}")
        return False






@app.get("/api/registrations/{email}")
async def get_registrations(email: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get registrations
        cur.execute("""
            SELECT * FROM event_registrations WHERE bookers_email = %s
        """, (email,))
        
        registrations = cur.fetchall()
        reg_columns = [desc[0] for desc in cur.description]
        
        # Get date preferences
        cur.execute("""
            SELECT * FROM event_dates WHERE email_id = %s
        """, (email,))
        
        dates = cur.fetchall()
        date_columns = [desc[0] for desc in cur.description]
        
        result = []
        for reg in registrations:
            reg_dict = dict(zip(reg_columns, reg))
            
            # Get dates for this person
            person_dates = []
            for date_row in dates:
                date_dict = dict(zip(date_columns, date_row))
                if date_dict['name'] == reg_dict['name'] and date_dict['contact'] == reg_dict['contact']:
                    person_dates.append(date_dict)
            
            reg_dict['datePreferences'] = person_dates
            result.append(reg_dict)
        
        cur.close()
        conn.close()
        
        return {"status": "success", "registrations": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.put("/api/update-registration")
async def update_registration(data: Dict[str, Any]):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update registration data
        cur.execute("""
            UPDATE event_registrations SET
                age = %s, gender = %s, origin = %s, travelmode = %s,
                departure_from_home = %s, arrival_at_venue = %s,
                accommodation = %s, cot_required = %s, difficultyclimbingstairs = %s,
                recordings = %s, recordprograms = %s, specialrequests = %s
            WHERE bookers_email = %s AND bookers_phone = %s AND name = %s
        """, (
            data.get('age'), data.get('gender'), data.get('origin'), data.get('travelmode'),
            data.get('departure_from_home'), data.get('arrival_at_venue'),
            data.get('accommodation'), data.get('cot_required'), data.get('difficultyclimbingstairs'),
            data.get('recordings'), data.get('recordprograms'), data.get('specialrequests'),
            data.get('bookers_email'), data.get('bookers_phone'), data.get('name')
        ))
        
        # Update date preferences if provided
        if 'datePreferences' in data:
            for date_pref in data['datePreferences']:
                cur.execute("""
                    UPDATE event_dates SET
                        morning_tea = %s, morning_coffee = %s, afternoon_tea = %s, afternoon_coffee = %s,
                        breakfast = %s, lunch = %s, dinner = %s, packed_lunch = %s, packed_dinner = %s, departuretime = %s
                    WHERE email_id = %s AND contact = %s AND name = %s AND date = %s
                """, (
                    date_pref.get('morning_tea'), date_pref.get('morning_coffee'),
                    date_pref.get('afternoon_tea'), date_pref.get('afternoon_coffee'),
                    date_pref.get('breakfast'), date_pref.get('lunch'), date_pref.get('dinner'),
                    date_pref.get('packed_lunch'), date_pref.get('packed_dinner'), date_pref.get('departuretime'),
                    date_pref.get('email_id'), date_pref.get('contact'), date_pref.get('name'), date_pref.get('date')
                ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": "success", "message": "Registration updated successfully"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/delete-registration")
async def delete_registration(data: Dict[str, Any]):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        bookers_email = data.get('bookers_email')
        bookers_phone = data.get('bookers_phone')
        name = data.get('name')
        
        # Delete from event_dates first (foreign key constraint)
        cur.execute("""
            DELETE FROM event_dates WHERE email_id = %s AND name = %s
        """, (bookers_email, name))
        
        # Delete from event_registrations
        cur.execute("""
            DELETE FROM event_registrations WHERE bookers_email = %s AND bookers_phone = %s AND name = %s
        """, (bookers_email, bookers_phone, name))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": "success", "message": "Registration deleted successfully"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/registration")
async def receive_registration(data: RegistrationData):
    try:
        success_count = 0
        total_participants = len(data.participants)
        
        for participant in data.participants:
            if insertParticipantDetails(participant, data):
                success_count += 1
        
        if success_count == total_participants:
            return {
                "status": "success", 
                "message": f"Registration data successfully saved to database! {success_count} participants registered for {data.event}"
            }
        else:
            return {
                "status": "partial_success", 
                "message": f"Saved {success_count} out of {total_participants} participants to database"
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Database error: {str(e)}"
        }



@app.get("/api/check-admin/{email}")
async def check_admin(email: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT control_type FROM admins WHERE email = %s", (email,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return {"status": "success", "is_admin": True, "control_type": result[0]}
        else:
            return {"status": "success", "is_admin": False, "control_type": None}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/admin/all-registrations")
async def get_all_registrations():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all registrations
        cur.execute("SELECT * FROM event_registrations")
        registrations = cur.fetchall()
        reg_columns = [desc[0] for desc in cur.description]
        
        # Get all date preferences
        cur.execute("SELECT * FROM event_dates")
        dates = cur.fetchall()
        date_columns = [desc[0] for desc in cur.description]
        
        result = []
        for reg in registrations:
            reg_dict = dict(zip(reg_columns, reg))
            
            # Get dates for this person
            person_dates = []
            for date_row in dates:
                date_dict = dict(zip(date_columns, date_row))
                if date_dict['name'] == reg_dict['name'] and date_dict['email_id'] == reg_dict['bookers_email']:
                    person_dates.append(date_dict)
            
            reg_dict['datePreferences'] = person_dates
            result.append(reg_dict)
        
        cur.close()
        conn.close()
        
        return {"status": "success", "registrations": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/admin/analytics")
async def get_analytics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get analytics data
        cur.execute("""
            SELECT date, 
                   COUNT(CASE WHEN morning_tea = 'with' THEN 1 END) as morning_tea_with,
                   COUNT(CASE WHEN morning_tea = 'without' THEN 1 END) as morning_tea_without,
                   COUNT(CASE WHEN morning_coffee = 'with' THEN 1 END) as morning_coffee_with,
                   COUNT(CASE WHEN morning_coffee = 'without' THEN 1 END) as morning_coffee_without,
                   COUNT(CASE WHEN afternoon_tea = 'with' THEN 1 END) as afternoon_tea_with,
                   COUNT(CASE WHEN afternoon_tea = 'without' THEN 1 END) as afternoon_tea_without,
                   COUNT(CASE WHEN afternoon_coffee = 'with' THEN 1 END) as afternoon_coffee_with,
                   COUNT(CASE WHEN afternoon_coffee = 'without' THEN 1 END) as afternoon_coffee_without,
                   COUNT(CASE WHEN breakfast = true THEN 1 END) as breakfast_count,
                   COUNT(CASE WHEN lunch = true THEN 1 END) as lunch_count,
                   COUNT(CASE WHEN dinner = true THEN 1 END) as dinner_count
            FROM event_dates 
            GROUP BY date 
            ORDER BY date
        """)
        
        analytics = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        result = [dict(zip(columns, row)) for row in analytics]
        
        cur.close()
        conn.close()
        
        return {"status": "success", "analytics": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/admin/detailed-analytics")
async def get_detailed_analytics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Accommodation by date and gender
        cur.execute("""
            SELECT r.name, r.age, r.gender, r.origin, r.bookers_email, r.contact,
                   UNNEST(r.attending_dates) as date
            FROM event_registrations r 
            WHERE r.accommodation = true
            ORDER BY date, r.gender, r.name
        """)
        accommodations = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        
        # Cots required
        cur.execute("""
            SELECT name, age, gender, origin, bookers_email, contact
            FROM event_registrations 
            WHERE cot_required = true
            ORDER BY gender, name
        """)
        cots = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        
        # Recordings requested
        cur.execute("""
            SELECT name, bookers_email, contact, recordprograms
            FROM event_registrations 
            WHERE recordings = true AND recordprograms IS NOT NULL AND recordprograms != ''
            ORDER BY name
        """)
        recordings = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        
        # Special requests
        cur.execute("""
            SELECT name, bookers_email, contact, specialrequests
            FROM event_registrations 
            WHERE specialrequests IS NOT NULL AND specialrequests != ''
            ORDER BY name
        """)
        special_requests = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        
        # Packed meals by date
        cur.execute("""
            SELECT d.date, d.name, r.bookers_email, r.contact, r.age, r.origin,
                   d.packed_lunch, d.packed_dinner
            FROM event_dates d
            JOIN event_registrations r ON d.email_id = r.bookers_email AND d.name = r.name
            WHERE d.packed_lunch = true OR d.packed_dinner = true
            ORDER BY d.date, d.name
        """)
        packed_meals = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        return {
            "status": "success", 
            "accommodations": accommodations,
            "cots": cots,
            "recordings": recordings,
            "special_requests": special_requests,
            "packed_meals": packed_meals
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)