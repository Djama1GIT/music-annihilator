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

## User Interface
Home page:

http://localhost/ 

## Technologies Used

- Python - A programming language used for the project.
- FastAPI - The Python framework used in the project to implement the REST API.
- TypeScript - A programming language used for adding static typing with optional type annotations to JavaScript.
- React - The library used for web and native user interfaces.
- REST - An architectural style for designing networked applications, used in the project for API communication between clients and servers.
- Server-Sent Events - A server push technology enabling real-time updates from the server to the client over HTTP, used for streaming data in the application. 
- S3 - Simple Storage Service (S3), an object storage service used in the project for storing and retrieving files.
- LocalStack - A cloud service emulator that runs in a container, providing a local AWS environment for development and testing.
- Docker - A platform used in the project for creating, deploying, and managing containers, allowing the application to run in an isolated environment.

# TODO:

- refactoring
- tests
- fix readme