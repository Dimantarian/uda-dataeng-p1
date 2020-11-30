# DROP TABLES

songplay_table_drop = "DROP TABLE IF EXISTS songplays;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES

songplay_table_create = (
    """CREATE TABLE IF NOT EXISTS songplays (songplay_id varchar(50) PRIMARY KEY, start_time time, \
    user_id int, level varchar(10), song_id varchar(50), artist_id varchar(50), session_id int, \
    location varchar(255), user_agent varchar(255));""")

user_table_create = (
    """CREATE TABLE IF NOT EXISTS users (user_id int, first_name varchar(50), \
    last_name varchar(50), gender varchar(1), level varchar(4));""")

song_table_create = (
    """CREATE TABLE IF NOT EXISTS songs (song_id varchar(50) PRIMARY KEY, \
    title varchar(255), artist_id varchar(50), year int, duration real);""")

artist_table_create = (
    """CREATE TABLE IF NOT EXISTS artists (artist_id varchar(50) PRIMARY KEY, \
    name varchar(255), location varchar(255), latitude real, longitude real);""")

time_table_create = (
    """CREATE TABLE IF NOT EXISTS time (start_time time , hour int, \
    day int, week int, month int, year int, weekday int);""")


# FIND SONGS

song_select = (
    """SELECT song_id, a.artist_id FROM songs s INNER JOIN artists a on s.artist_id = a.artist_id \
    WHERE s.title = %s AND a.name = %s AND round(cast(s.duration as numeric),3) = %s;""")

# QUERY LISTS

create_table_queries = [songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
