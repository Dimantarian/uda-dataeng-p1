## Sparkify ETL Data Modelling

### About Sparkify
Sparkify is simply the best streaming service in town, better than all the rest. Access 10's of millions of songs and share the experience with your friends. The social aspects of the service are what really makes the difference.

### Purpose of this database
To make use of sparkify's leading edge platform, we need to get to know our users - or at least we need to understand their behaviour and what they're going to want; ideally before they do! We capture every breath you take, every move you make whilst listening to your favourite songs and carefully catalogue them for our algo's to build that behavioural profile.

### Analytical Goals
Making sense of this data is the aim of the game, and to that end, we need our analysts to be able to write lightning fast queries. We want to know who is listening, how often, and what to. But we also want to know what sort of people listen at different times of day.

### Enough Blurb! How to run!
Follow these steps:
1. Run create_tables.py - this drops, and then recreates the relevant tables and initialises some key queries to be used later
2. Run etl.py - this will perform the steps detailed in *ETL pipeline* below and populate the postgres tables with the transformed data

*NOTE* Given we've used the super fast Copy command, running with repeated data causes errors given the primary key constraints. This will hurt on artists, songs and songplays, but not on users or time as we've not constrained those tables. 

### Design Considerations
This data store is primarily for analytics, we want our analysts to be able to cut lots of different queries (i.e. ask lots of questions) to test theit hypotheses, and be able to create fast aggregations. The star schema design was perfect.

We'll separate data into events within a FACT table, and a number of dimensions representing different aspects of the events. The users, the songs, the artists and when they tuned in.

We're only interested in plays, so a lot of the peripheral event data that isn't a direct listen we can scrap

### ETL pipeline.
We pull our data from two primary sources:

* Our song catalogue
* Activity logs

These are stored in JSON format - probably in a NoSQL database somewhere that's optimised for fast writes and doens't have much need for relational joins.

Using standard open source tools we can pull this data in and begin to split it into our fact and dimensions. 

The song catalogue splits nicely into songs and artists, though some artists have more than one song, so some deduplication is required when building our dimensions.

The log data allows us to split users and time of listen pretty easily. Right now we've assumed that the timestamp is unique enough and didn't create an ID. We should probably look at that in the future, but as we're a startup with only our mates as users, it'll do for now!. Users has some deduping work to do. We hadn't decided on what to do with the record once the decided to upgrade from the free level to the premium, so right now we've kept both (as well as some other general messiness).

We created the fact table, songplays from a combination of the artists, songs and event data. We didn't have great data to match on, so we had to go by the artist names and song titles. In the end this did the trick, but we'll probably wnt to put some effort into data cleansing going forward! This involves a lot of data passing back and forth between client and server, there's probably a smarter / stabler way of doing this, but the code is pretty darn cool so we left it.

Ah! Data cleansing... we did some basic manipulations on some fields that had built in commas, switching them out for semi colons to keep postgres happy. This is something else to look at once we get some of that sweet Series A $$'s!

As we went along, we loaded the data into postgres tables. We thought about using some template insert code from a high school project, but ultimately decided to copy the tables in wholesale to speed up the process. Worked a treat. We're liking the psycopg2 library, but might want to do a little more research to look at the optimal way of moving data, understand what happens client vs. server side to make sure that our code is ready to handle our huge successes on the horizon.

### Examples

#### Query 1
##### What's the most popular song?
```
%load_ext sql
%sql postgresql://student:student@127.0.0.1/sparkifydb
%sql select title, count(*) from songs s join songplays ss on s.song_id = ss.song_id group by title order by count(*) desc
```
#### Query 2
##### Which users spend the most time on our service, is there a difference between the free and paid tiers?
```
%load_ext sql
%sql postgresql://student:student@127.0.0.1/sparkifydb
%sql select u.user_id, u.level, sum(duration) from songs s join songplays ss on s.song_id = ss.song_id join users u on u.user_id = ss.user_id group by u.user_id, u.level order by u.user_id, u.level, sum(duration) desc
```

