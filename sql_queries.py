# DROP TABLES

songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES

songplay_table_create = (
    """CREATE TABLE IF NOT EXISTS songplays (songplay_id varchar(50) PRIMARY KEY, start_time TIME, \
    user_id int, level varchar(10), song_id VARCHAR(50), artist_id VARCHAR(50), session_id INT, \
    location VARCHAR(255), user_agent VARCHAR(255));""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS  users(
    user_id  INT PRIMARY KEY,
    first_name  VARCHAR,
    last_name  VARCHAR,
    gender  CHAR(1),
    level VARCHAR NOT NULL
)""")

song_table_create = (
    """CREATE TABLE IF NOT EXISTS songs (song_id VARCHAR(50) PRIMARY KEY, \
    title VARCHAR(255), artist_id VARCHAR(50), year INT, duration INT);""")

artist_table_create = (
    """CREATE TABLE IF NOT EXISTS artists (artist_id VARCHAR(50) PRIMARY KEY, \
    name VARCHAR(255), location VARCHAR(255), latitude REAL, longitude REAL);""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS  time(
    start_time  TIME PRIMARY KEY,
    hour INT NOT NULL CHECK (hour >= 0),
    day INT NOT NULL CHECK (day >= 0),
    week INT NOT NULL CHECK (week >= 0),
    month INT NOT NULL CHECK (month >= 0),
    year INT NOT NULL CHECK (year >= 0),
    weekday INT NOT NULL
)""")

# INSERT RECORDS

songplay_table_insert = ("""INSERT INTO songplays VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s )
""")


# Updating the user level on conflict
user_table_insert = ("""INSERT INTO users (user_id, first_name, last_name, gender, level) VALUES (%s, %s, %s, %s, %s) 
                        ON CONFLICT (user_id) DO UPDATE SET 
                        level = EXCLUDED.level 
""")

song_table_insert = ("""INSERT INTO songs (song_id, title, artist_id, year, duration) VALUES (%s, %s, %s, %s, %s) 
                        ON CONFLICT (song_id) DO NOTHING                        
""")


# Artist location, latitude and longitude might change and need to be updated.
artist_table_insert = ("""INSERT INTO artists (artist_id, name, location, latitude, longitude) VALUES (%s, %s, %s, %s, %s) 
                          ON CONFLICT (artist_id) DO UPDATE SET
                          location = EXCLUDED.location,
                          latitude = EXCLUDED.latitude,
                          longitude = EXCLUDED.longitude
""")

time_table_insert = ("""INSERT INTO time VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (start_time) DO NOTHING
""")

# FIND SONGS

song_select = (
    """SELECT song_id, a.artist_id FROM songs s INNER JOIN artists a on s.artist_id = a.artist_id \
    WHERE s.title = %s AND a.name = %s AND round(cast(s.duration as numeric),3) = %s;""")

# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
