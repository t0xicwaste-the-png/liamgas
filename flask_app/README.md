# LiamGas (Flask Edition)

A lightweight chat application ported from Django to Flask.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser at `http://127.0.0.1:5000`

## Configuration

- `SECRET_KEY`: Set this environment variable in production.
- Database: Uses SQLite by default (`site.db`).

## Notes

- This replaces the old Django project (`mysite/liamgas`).
- Static files are in `static/`.
- Templates are in `templates/`.
