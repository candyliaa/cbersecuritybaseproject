# Cyber Security Base 2025 Project 1
The current functionality of the app is as follows:
- Users can create a student or a teacher account, which have different functionalities
- Students can view all courses, join them, leave them, view text materials do exercises
- Teachers can create courses, add exercises and text materials, delete exercises and delete courses
- Exercises can be essay exercises or multiple choice exercises: Essay exercises upon submission are always correct, and the example answer is shown, while multiple choice questions can be correct or wrong
- When viewing a course, students can see which exercises they have done and which they haven't, along with if they are correct or incorrect
- Teachers can see which students have done which exercises, and if they are correct or incorrect

# Running the app
**With Docker** <br />
<br />
First, clone the repository:
```
$ git clone https://github.com/candyliaa/tsoha-opetussovellus.git
```
You can run the app with [Docker](https://www.docker.com/). You can install it [here](https://docs.docker.com/get-docker/).
The structure of the Docker containers follows [this](https://docs.docker.com/compose/gettingstarted/) guide.
To run the app yourself, generate a secret key: 
```
$ python3
>>> import secrets
>>> secrets.token_hex(16)
```
and replace `KEY GOES HERE` in `compose.yaml.example` with the key you just generated. Then rename `compose.yaml.example` to just `compose.yaml`.
After that, launch the Docker Desktop application, and run
```
$ docker compose up
```
You can then open the app at [`http://localhost:8000`](http://localhost:8000) . <br />
<br />
**Without Docker**

Alternatively, the app can be ran without Docker.
You will need a [local Postgres installation](https://ubuntu.com/server/docs/databases-postgresql). These instructions assume the user is using Ubuntu or an Ubuntu-based distro. For other distros and operating systems, the process may vary.
Clone the repository:
```
$ git clone https://github.com/candyliaa/tsoha-opetussovellus.git
```
Optionally, you can remove all Docker related files: `Dockerfile` in both the `app` and `db` dictionaries, as well as `compose.yaml.example`.
Then, create a `.env` file in the `app` directory, and add two lines, one for the `SECRET_KEY`, and one for the `DATABASE_URL`. It should look like this:
```
SECRET_KEY = <KEY_GOES_HERE>
DATABASE_URL = <URL_GOES_HERE>
```
Generate a secret key:
```
$ python3
>>> import secrets
>>> secrets.token_hex(16)
```
As for the `DATABASE_URL`, you can input the following: `"postgresql://postgres@localhost/postgres"`. 
Be mindful of the fact that this attempts to connect to a local database named `postgres`, which might already exist.
The URL you have to use depends on your system, so the above may not work properly.

Next, install all required packages with a virtual environment:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./app/requirements.txt
```

*Note:*
You may have to start the `postgresql` service with the following command on Linux:
```
$ service postgresql start
```

Then, build the database using the schema:
```
$ psql < db/schema.sql
```
**If you have PSQL installed locally Linux, you should instead run**
```
$ psql -h localhost -U postgres < db/schema.sql
```
Optionally, you can also add some test data to the database:
```
$ psql < db/test_data.sql
```
**And again, if running locally on Linux, run:**
```
$ psql -h localhost -U postgres < db/test_data.sql
```
instead.

You can now run the app with the command
```
$ flask run
```
Run the command in the `app` directory.
# Current state of the app
The code in `routes.py` has been moved to `data.py` so that the logic in `routes.py` is easier to follow. The code has also been formatted using pylint and Black Formatter.
The app has been styled using Bootstrap and some css.
There should be no security vulnerabilities (at least no SQL injection, XSS or CSRF attack risk). 
