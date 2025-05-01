# Music Annihilator

Music Annihilator is a simple project that is used to remove music from audio

## Installation and Setup <sup><sub>(tested on Linux)</sub></sup>

1. Install Docker and Docker Compose if they are not already installed on your system.

2. Clone the project repository:

```bash
git clone https://github.com/Djama1GIT/music-annihilator.git
cd music-annihilator
```
3. Start the project:

```bash
docker-compose up --build
```

or<sup>* (it is assumed that you also have npm and Python installed)</sup>

```bash
make install
```
```bash
make frontend-run
```
```bash
make backend-run
```

## User Interface
Home page:

http://localhost/ 

## Technologies Used

- Python - The programming language used for the project.
- FastAPI - The Python framework used in the project to implement the REST API.
- TypeScript - The programming language used for adding static typing with optional type annotations to JavaScript.
- React - The library used for web and native user interfaces.
- Docker - A platform used in the project for creating, deploying, and managing containers, allowing the application to run in an isolated environment.

# TODO:

- backend
- docker
- makefile
- fix readme