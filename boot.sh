#!/bin/bash
# this script is used to boot a Docker container

# 1. Initialize migrations if folder is missing
if [ ! -d "migrations" ]; then
    echo "Initializing migrations folder..."
    flask db init
fi

# 2. Create the migration script (handles schema changes)
echo "Creating migrations..."
flask db migrate -m "startup migration" || echo "No changes detected in models"

# 3. Apply changes to the database
echo "Upgrading database..."
flask db upgrade

# 2. If migrations failed, exit
if [ $? -eq 0 ]; then
    echo "Migrations successful."
else
    echo "Migrations failed."
    exit 1
fi

# 3. Run the app (exec replaces the shell process with python)
exec gunicorn -b :5000 --access-logfile - --error-logfile - moj:app
