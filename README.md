# Vincent

Vincent is a system for reporting, assigning, and tracking voter protection incidents.

## Goals
1. Streamline data entry for attorneys.
2. Help lead attorneys triage & admins effectively triage the "hottest" issues amongst their thinly spread field attorney resources.
3. Location reporting, **especially** – make that as dead simple as possible.

## Features
1. Geolocation. Click "Find polling locations near me" and it gives the attorneys a list of places to choose from. Boom.
2. A highly customized Django admin to slice and dice incidents that need tracking.
3. GeoDjango niceness, for filtering (and visualizing) incidents, with help from Leaflet.
4. Stork Jobs to porting data around. More on that in a minute.

## Requirements

- Django (~1.9)
- GeoDjango https://docs.djangoproject.com/en/1.9/ref/contrib/gis/install/#mac-os-x
- Stork / DNC access

## Installation (tragically untested / recalling from memory)

1. `git clone git@github.com/Bernie-2016/vincent.git`
2. `cd vincent`
3. `mkvirtualenv vincent`
4. `pip install -r requirements.txt`
5. Add a `SECRET_KEY` and `DATABASE_URL` entries to a `.env` file (and, for email invite support, `MAILGUN_ACCESS_KEY` and `MAILGUN_SERVER_NAME`)
6. `./manage.py migrate`
7. `./manage.py runserver`

## But how do I even?

It really only needs three things in an ongoing basis:
1. Clear out issues. Marking them Closed or even Deleting them would probably do the trick.
2. Loading attorney users. Create a CSV file with these fields: `'First Name', 'Last Name', 'Email', 'Phone', 'Group'`, and see `./manage.py load_users` for doing that; it will email out invites.
3. Populating polling locations (with precinct rankings) via Stork job.

That last one's going to require some elaboration — somewhere in the bowels of Vertica, there's:

1. A Stork job to pull all the polling place locations within a given set of states (specified by abbreviation). Find that job and sub in the states you need. You'll want to run this close to / the night before Election Day.
2. Run ANOTHER Stork job, on that data, to use SmartTarget's geocoding service to produce lat / lng pairs on each of those points.
3. Run a third Stork job, to pipe ALL that composite data, over to Vincent's Postgres Database.

The jobs all exist, almost surely owned by me (Jon Culver). It's a bit to wrap your head around but most of the pieces are in place. Run them and wait (the state of CA, for example, might take a few hours to geocode entirely) and then you're gold!

## To do
1. Better separate the "front-end" roles. There's field attorneys, who need some of the geolcoation featuers, but there's also "boiler room" attorneys who aren't on the scene and don't care as much (and, probably don't need to review existing events). Talk to Renée to hash these use-cases out better.
2. Workflow _could_ be tighter, I'll say. They're training wheels, at this point.
3. Toward that same end: email notifications of incident assignments would be a big halp.
