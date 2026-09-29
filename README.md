# Code Relay

A Flask + MySQL website for a two-member college Code Relay event.

## Features

- Team login using a team code
- Event rules page
- Round 1 and Round 2 questions
- Coding page with timer
- Participants can write/test code in VS Code and paste the final code
- Submission recording
- Public leaderboard
- Admin dashboard
- Start Round 1 / Round 2
- Finish and reset event
- Add questions
- Secrets stored in environment variables

## Security note

This project DOES NOT execute participant code on the server.

Participants should use VS Code to write and test their program, then paste the final code into the website.

Executing arbitrary participant code requires a proper sandbox/container isolation system and should not be added directly to Flask.

## Requirements

- Python 3.10+
- MySQL 8+
- Git

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd code-relay
```

### 2. Create virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create database

Open MySQL Workbench or MySQL terminal and run:

```sql
SOURCE schema.sql;
```

Or open `schema.sql` in MySQL Workbench and execute it.

### 5. Create `.env`

Copy:

```text
.env.example
```

to:

```text
.env
```

Then change the values.

Example:

```env
SECRET_KEY=some-long-random-secret
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=code_relay

ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-real-admin-password
```

IMPORTANT: `.env` is ignored by Git and must never be committed.

### 6. Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Demo team codes

The database contains:

```text
TEAM001
TEAM002
TEAM003
TEAM004
```

Change these teams in your database before the actual event.

## Admin

Open:

```text
http://127.0.0.1:5000/admin
```

Use the credentials configured in `.env`.

Do NOT use the development defaults for a real event.

## GitHub

After creating your repository:

```bash
git init
git add .
git commit -m "Initial Code Relay project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/code-relay.git
git push -u origin main
```

Verify that `.env` is NOT included:

```bash
git status
```

## Suggested event workflow

1. Admin logs in.
2. Teams receive their team codes.
3. Admin starts Round 1.
4. Teams read the question.
5. Members use VS Code locally.
6. Team pastes final code.
7. Submission time is recorded.
8. Admin monitors the leaderboard.
9. Admin starts Round 2 when appropriate.

## Important improvement before a real competition

The current timer is a browser-side timer. For a high-stakes competition, make timing server-authoritative so participants cannot manipulate the timer through browser tools.

Also consider adding:
- server-side phase countdown
- synchronized round start
- separate timers for discussion/member 1/member 2
- admin ability to lock submissions
- CSV export
- team management UI
- audit logs
- CSRF protection
- HTTPS
- production WSGI server
