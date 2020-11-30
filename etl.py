import os
import glob
import psycopg2
import pandas as pd
import uuid
from sql_queries import *

# copy from function (adapted from https://naysan.ca/2020/06/21/pandas-to-postgresql-using-psycopg2-copy_from/)
def copy_from_file(conn, cur, df, table):
    """
    Here we are going save the dataframe on disk as 
    a csv file, load the csv file  
    and use copy_from() to copy it to the table
    """
    # Save the dataframe to disk
    tmp_df = "./tmp_dataframe.csv"
    records = len(df.index)
    df.to_csv(tmp_df, header=False, index=False)
    f = open(tmp_df, 'r')
    try:
        cur.copy_from(f, table, sep=",", null='')
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        os.remove(tmp_df)
        print("Error: %s" % error)
        conn.rollback()
        #cursor.close()
        return 1
    print("copy_from_file() done. %s table created in postgres with %s records" % (table, records))
    os.remove(tmp_df)
    
def get_files(filepath):
    """
    Creates a list of all json files under a directory (recursive)
    """
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))
    
    return all_files

def process_song_files(conn, cur, filepath):
    """
    Imports song files under a given directory
    and creates the song and artist dimension tables
    in postgres. Must be run prior to the 
    process_log_files function for data integrity
    """
    # open song file
    song_files = get_files(filepath)
    num_files = len(song_files)
    print('{} files found in {}'.format(num_files, filepath))
    
    # read song files into dataframe 
    dfs =[]
    for file in song_files:
        data = pd.read_json(file, lines=True)
        dfs.append(data)
    df = pd.concat(dfs, ignore_index=True)
    
    # transform, dedup and copy song data into postgres
    song_data = df[['song_id','title','artist_id','year','duration']].sort_values('song_id').drop_duplicates('song_id')
    copy_from_file(conn, cur, song_data, 'songs')
        
    # transform,dedup and copy artist data into postgres
   
    # minor cleansing
    df['artist_location_clean'] = df['artist_location'].str.replace(",",";")
    artist_data = df[['artist_id', 'artist_name', 'artist_location_clean', 'artist_latitude', 'artist_longitude']].sort_values('artist_id').drop_duplicates('artist_id')
    copy_from_file(conn, cur, artist_data, 'artists')

def process_log_files(conn, cur, filepath):
    """
    Imports log files under a given directory
    and creates the user and time dimension tables.
    Must be run prior to the process_log_files function
    for data integrity whilst creating the songplays fact
    table in postgres.
    """
    # open log file
    log_files = get_files(filepath)
    num_files = len(log_files)
    print('{} files found in {}'.format(num_files, filepath))
    
    # create log dataframe
    raw_log_dfs =[]
    for file in log_files:
        data = pd.read_json(file, lines=True)
        raw_log_dfs.append(data)
    log_df = pd.concat(raw_log_dfs, ignore_index=True)
    
    # filter by NextSong action
    log_df = log_df[log_df['page']=="NextSong"]
    
    # transform to create time dataframe
    time_data = pd.to_datetime(log_df['ts'], unit ='ms').to_frame()
    
    time_data['start_time'] = time_data['ts'].dt.time
    time_data['hour'] = time_data['ts'].dt.hour
    time_data['day'] = time_data['ts'].dt.day
    time_data['week'] = time_data['ts'].dt.week
    time_data['month'] = time_data['ts'].dt.month
    time_data['year'] = time_data['ts'].dt.year
    time_data['weekday'] = time_data['ts'].dt.weekday
    
    time_data = time_data.drop('ts',axis='columns')
    
    # copy time data into postgres (no key to dedup here - could create one...)
    copy_from_file(conn, cur, time_data, 'time')

    # transform user table and dedup
    user_data = log_df[['userId','firstName','lastName','gender','level']]

    # copy user data into postgres
    copy_from_file(conn, cur, user_data, 'users')

    # transform songplay records dataframe
    processing_log_list =[]
    for index, row in log_df.iterrows():
        
        # get songid and artistid from song and artist tables
        #print(song_select %(row.song, row.artist, row.length))
        cur.execute(song_select, (row.song, row.artist, round(row.length,3)))
        results = cur.fetchone()
        
        #print(results)
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # create songplay dataframe
        songplay_tuple = (uuid.uuid4().hex, time_data['start_time'][index], row.userId, row.level, \
                                 songid, artistid, row.sessionId, row.location.replace(",",";"), \
                                 row.userAgent.replace(",",";"))
        processing_log_list.append(songplay_tuple)
        #cur.execute(songplay_table_insert, songplay_data)

    songplay_data =  pd.DataFrame(processing_log_list,columns = ['songplay_id', 'start_time', \
                                                                 'user_id', 'level', 'song_id', \
                                                                 'artist_id', 'session_id', \
                                                                 'location', 'user_agent'])
    
    # copy songplay data to postgres (no need to dedup here)
    copy_from_file(conn, cur, songplay_data, 'songplays')


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_song_files(conn, cur, filepath='data/song_data')
    process_log_files(conn, cur, filepath='data/log_data')

    conn.close()


if __name__ == "__main__":
    main()