import os
from apps import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Alter column length if using PostgreSQL or other DB supporting ALTER TYPE
    stmt = text('ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(256)')
    try:
        db.session.execute(stmt)
        db.session.commit()
        print('Password hash column length updated to 256')
    except Exception as e:
        print('Error updating column:', e)
