# LCSRC

![A screenshot showing LCSRC with the BoM input field and the results table](https://cdn.hackclub.com/01a17aca-c3f9-7dc5-a183-83ee1d78fa7e/Screenshot%202026-10-27%20at%2001-34-58%20LCSRC.png)

A way to get pricing info for your BoM and (eventually) find replacement components+search by electrical parameters. I made it because JLCPCB/LCSC have a bad search interface which often doesn't offer range search or expose some important parameters (even though they're provided by the manufacturer!), JLCsearch limits search to only a couple of fields it considers important, and JLCparts downloads 10GB into your browser's IndexedDB. None of these solutions are ideal, especially when you have someone breathing down your neck about "quickly bringing the total BoM cost down" while JLCPCB just finds some standard PCBA parts that have been out of production for 3 years.

## Usage

Go to [the website](https://lcsrc.berry.hackclub.app) and input a list of LCSC part nums (prefixed with C). You can also use quantities (leaving them out implicitly means the component is a 1-of), for example:
```50,C7512
C28646273
4,C7562
```

After pressing 'Search', the site outputs a table of the components with the per-unit and total price.

## Hosting

- Clone the repository
- Install the necessary packages such as FastAPI, SQLite3 and requests
- In the root directory, run `python app/db.py` to create the database
- Run `python jlc_import.py` to get fresh data and populate the database
- Run `uvicorn app.main:app` to start the server
