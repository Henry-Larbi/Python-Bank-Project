import psycopg2
import config


def get_connection():
    """Return a new psycopg2 connection to the Supabase PostgreSQL database."""
    return psycopg2.connect(config.DATABASE_URL)
