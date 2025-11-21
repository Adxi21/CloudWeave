DB_HOST = "13.201.93.107"   # EC2 Public IP
DB_PORT = 5432
DB_NAME = "eventdb"
DB_USER = "adiuser"
DB_PASS = "rajarama"

create_event_table = """
CREATE TABLE IF NOT EXISTS event_registrations (
    bookers_email VARCHAR(255) NOT NULL,
    bookers_phone VARCHAR(20) NOT NULL,
    
    event_name VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    contact VARCHAR(50) NOT NULL,

    attending_dates TEXT[] NOT NULL, 
    travelMode VARCHAR(50),

    departure_from_home VARCHAR(10),
    arrival_at_venue VARCHAR(10),

    accommodation BOOLEAN,
    cot_required BOOLEAN,
    difficultyClimbingStairs BOOLEAN,
    localAssistance BOOLEAN,
    localAssistancePerson VARCHAR(255),

    recordings BOOLEAN,
    recordPrograms TEXT,
    specialRequests TEXT,

    PRIMARY KEY (bookers_email, bookers_phone)
);
"""

create_date_table = """
CREATE TABLE IF NOT EXISTS event_dates (
    email_id varchar(255) not null,
    contact varchar(255) not null,
    name varchar(255) not null,
    date varchar(255) not null,
    morning_tea varchar(255) ,
    morning_coffee varchar(255),
    afternoon_tea varchar(255),
    afternoon_coffee varchar(255),
    breakfast boolean ,
    lunch boolean ,
    dinner boolean ,
    packed_lunch boolean ,
    packed_dinner boolean ,
    departureTime varchar(255)
)

"""


