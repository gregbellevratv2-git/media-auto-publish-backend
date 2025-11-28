# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LinkedIn Auto Publish is a desktop GUI application for scheduling and publishing LinkedIn posts. It uses a webhook-based approach (via Make.com) to publish content, supports image uploads via FTP, and provides a calendar/list view for managing scheduled posts.

## Architecture

### Core Components

- **main_app.pyw**: Main application with CustomTkinter GUI. Entry point that initializes the database and scheduler, then launches the app window. The app can minimize to system tray.
  - `App`: Main window class (inherits from `ctk.CTk` and `TkinterDnD.DnDWrapper`)
  - `ImageEntry`: Widget for managing individual images with move/delete controls

- **database.py**: SQLite database layer managing posts
  - Table: `posts` with columns: id, title, text_content, image_path, scheduled_at, status, created_at, error_message
  - Status values: 'scheduled', 'published', 'failed'

- **scheduler_service.py**: APScheduler-based background job management
  - Uses SQLAlchemyJobStore backed by the same SQLite database
  - Job IDs follow pattern: `post_{post_id}`
  - `publish_post_task()` is the callback executed at scheduled time

- **linkedin_api.py**: Webhook client for posting to LinkedIn via Make.com
  - `WebhookLinkedInAPI.post_update()` sends JSON payload: {title, text, image_url}
  - Combines title and text into a single field for the webhook

- **image_utils.py**: Image processing and FTP upload
  - Combines up to 3 images vertically with spacing
  - Resizes combined image to height of 1980px (maintains aspect ratio)
  - Uploads to FTP server and returns public URL

- **config.py**: Configuration loader reading from config.ini
  - Sections: [LINKEDIN] (WEBHOOK_URL), [FTP] (HOST, USER, PASS, PATH, BASE_URL)

### Data Flow

1. **Creating a Post**: User enters content, drops images → Images combined/resized → Upload to FTP → Store post in DB with image URL → Schedule job in APScheduler
2. **Editing a Post**: Load post data into form → User modifies → Update DB and reschedule job (or create if doesn't exist)
3. **Publishing**: APScheduler triggers `publish_post_task()` → Call webhook API → Update post status in DB
4. **Manual Send**: User clicks "Envoyer" → Immediately call webhook API → Update status → Remove scheduled job if exists

### UI Structure

- Left panel: Post creation/editing form with drag-and-drop image zone (up to 3 images)
- Right panel: Tabbed view
  - **Liste tab**: Scrollable list of all posts with status indicators, delete/edit/send buttons
  - **Calendrier tab**: Calendar view with event markers + details textbox showing posts for selected date

## Common Development Tasks

### Running the Application

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Run the application
python main_app.pyw
# or launch via
launch.bat
```

### Installing Dependencies

```bash
pip install -r requirements.txt
```

Note: The application requires `tkinterdnd2` which may need manual installation on some systems.

### Database Operations

The database is automatically initialized on first run. File: `linkedin_scheduler.db`

To inspect the database:
```bash
python debug_db.py
```

### Configuration

Edit `config.ini` to set:
- Make.com webhook URL for LinkedIn posting
- FTP credentials for image hosting
- Image base URL for public access

**IMPORTANT**: The config.ini file contains credentials. Ensure it is never committed to version control.

## Key Implementation Details

### Image Handling

- Drag-and-drop zone accepts .png, .jpg, .jpeg, .webp files
- Images are stored in-memory during editing (via `ImageEntry` widgets)
- On schedule/save: Images are combined vertically with 50px spacing between them
- Final image is resized to 1980px height and uploaded to FTP
- Image URL is stored in database, not the local file path

### Edit Mode

- When editing, `App.editing_post_id` is set to the post ID
- Cancel button becomes visible
- Schedule button text changes to "Enregistrer" and command switches to `save_edited_post()`
- `image_marked_for_deletion` flag tracks whether user clicked "Vider Images"
- Image handling logic:
  - New images dropped → Process and upload
  - "Vider Images" clicked → Set flag, remove on save
  - Neither → Keep existing image URL

### Scheduler Persistence

APScheduler uses SQLAlchemyJobStore, so scheduled jobs persist across application restarts automatically. Jobs are stored in the same SQLite database as posts.

### System Tray Behavior

- Closing window minimizes to tray (doesn't exit)
- Tray icon menu: "Afficher" (restore), "Quitter" (exit)
- Scheduler continues running when minimized

## Debugging

Logs are written to `app.log` with level DEBUG. Check this file for detailed execution traces.
