# LCSRC

A way to get pricing info for your BoM and (eventually) find replacement components.

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
