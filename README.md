# Videoflix Backend API

Built as part of a full-stack learning journey.

This project is a RESTful backend API for a video streaming platform built with Django and Django REST Framework.

The API provides secure authentication, automated media processing, and adaptive video streaming using HTTP Live Streaming (HLS).

Uploaded videos are processed asynchronously using Redis and Django RQ, where thumbnails and HLS streams are generated before becoming available to authenticated users.

---

# Architecture & Workflow

```text
        Admin uploads video
                │
                ▼
         Django REST API
                │
                ▼
      Save original video
                │
                ▼
         Enqueue RQ Job
                │
                ▼
        Redis + RQ Worker
                │
        ┌───────┴────────┐
        ▼                ▼
 Generate Thumbnail   Create HLS
        │                │
        └───────┬────────┘
                ▼
       Media Directory
                │
                ▼
 Authenticated Users
                │
                ▼
      HLS Streaming API
```

---

# Features

* User registration with email activation
* JWT authentication using HTTP-only cookies
* Secure login, logout and token refresh
* Password reset via email
* Video upload (administrator only)
* Automatic thumbnail generation using FFmpeg
* Automatic HLS conversion (480p, 720p and 1080p)
* Background video processing using Django RQ
* Protected HLS streaming endpoints
* Docker-based development environment

---

# Technologies

* Python 3.x  
* Django  
* Django REST Framework
* PostgreSQL
* Redis
* Django RQ
* FFmpeg  
* SimpleJWT
* Docker 
* Docker Compose

---

# Authentication

Authentication is implemented using JWT stored in HTTP-only cookies.

### Cookies

* `access_token` → short-lived authentication  
* `refresh_token` → used to generate new access tokens  

### Authentication Flow

1. User logs in.
2. Backend creates both JWT cookies.
3. Protected endpoints authenticate users using:
    - Authorization header
    - or HTTP-only access cookie
4. When the access token expires, the frontend requests a new access token using the refresh endpoint.
5. Logout invalidates the refresh token and removes both cookies.

---

# Permissions

### Administrator

Administrators can:
    - Upload videos
    - Manage video content

### Authenticated Users

Authenticated users can:
    - View the video catalogue
    - Request HLS playlists
    - Stream protected video segments

---

# Video Processing Pipeline

Each uploaded video is processed asynchronously.

Processing workflow:

1. Upload original video
2. Create background job
3. Generate thumbnail
4. Generate HLS stream (480p)
5. Generate HLS stream (720p)
6. Generate HLS stream (1080p)
7. Video becomes available for streaming

---

# Streaming

The backend uses HTTP Live Streaming (HLS).

Available endpoints:

```text
GET /api/video/
```

Returns all available videos.

```text
POST /api/video/upload/
```

Uploads a new video (administrator only).

```text
GET /api/video/<movie_id>/<resolution>/index.m3u8
```

Returns the HLS playlist.

```text
GET /api/video/<movie_id>/<resolution>/<segment>
```

Returns a single MPEG-TS segment.

---

# Background Processing

Heavy media processing is executed asynchronously using Redis and Django RQ.

Background tasks include:

* Thumbnail generation
* HLS conversion
* Media processing

---

# Installation (Docker)

Clone the repository:

```
git clone <repository-url>
cd Videoflix
```


Create a local environment file.

```bash
cp .env.template .env
```

(Windows users can simply copy `.env.template` and rename it to `.env`.)

Edit the `.env` file and replace the placeholder values with your own configuration.

Start the application.

```bash
docker compose up --build
```

On the first startup Docker automatically:

- creates the database schema
- creates the administrator account
- starts the Redis worker
- starts the Django application

The backend is now available.

---

# Purpose of this Project

This project was built to practice:

* Django Rest Framework  
* JWT authentication with cookies  
* Secure API design  
* Background processing with Redis
* Django RQ workers
* FFmpeg media processing
* HTTP Live Streaming (HLS)
* Docker-based development
* Scalable backend architecture

---

# License

This project is intended for **educational purposes**.