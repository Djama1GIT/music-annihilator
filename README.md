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

Dashboard:
http://localhost/grafana/ (admin/admin)

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
- Prometheus - An open-source systems monitoring and alerting toolkit that collects and stores metrics as time series data.
- Grafana - A multi-platform open-source analytics and interactive visualization web application for monitoring and observability.
- Loki - A horizontally-scalable, highly-available, multi-tenant log aggregation system inspired by Prometheus.
- Promtail - An agent that ships the contents of local logs to a Loki instance, typically deployed to every machine running applications.
- Nginx - A high-performance web server, reverse proxy, and load balancer used for serving web content and routing traffic.

# Contributors

<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/Djama1GIT">
          <img src="https://avatars.githubusercontent.com/u/89941580?v=4?s=130" height="130px;" alt="Djama1GIT"/>
          <br />
          <sub><b>Djama1GIT</b></sub>
        </a>
      </td>
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/alibekovvl">
          <img src="https://avatars.githubusercontent.com/u/126617833?v=4?s=130" height="130px;" alt="alibekovvl"/>
            <br />
          <sub><b>alibekovvl</b></sub>
        </a>
      </td>
    </tr>
  </tbody>
</table>

# TODO:

- refactoring
- tests
- fix readme