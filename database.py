"""
database.py
-----------
Handles all SQLite database operations for WebScrapeX Pro.

Tables:
    sessions  -> stores metadata about each scraping session
    products  -> stores individual product records linked to a session
"""

import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """Manages all interactions with the SQLite database."""

    def __init__(self, db_path="database/scraper.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._initialize_database()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):
        """Create tables if they do not already exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_name TEXT NOT NULL,
                website_url TEXT NOT NULL,
                scrape_date TEXT NOT NULL,
                total_products INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                product_name TEXT,
                price REAL,
                rating REAL,
                reviews_count INTEGER,
                availability TEXT,
                product_link TEXT,
                category TEXT,
                image_url TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # SESSION OPERATIONS
    # ------------------------------------------------------------------
    def create_session(self, website_name, website_url, total_products):
        """Insert a new scraping session and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (website_name, website_url, scrape_date, total_products)
            VALUES (?, ?, ?, ?)
        """, (
            website_name,
            website_url,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_products
        ))
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id

    def get_all_sessions(self):
        """Return all scraping sessions ordered by most recent."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, website_name, website_url, scrape_date, total_products
            FROM sessions
            ORDER BY scrape_date DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_session(self, session_id):
        """Delete a session and all its associated products."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # PRODUCT OPERATIONS
    # ------------------------------------------------------------------
    def insert_products(self, session_id, products):
        """Bulk insert a list of product dictionaries for a given session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        for p in products:
            cursor.execute("""
                INSERT INTO products (
                    session_id, product_name, price, rating, reviews_count,
                    availability, product_link, category, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                p.get("name"),
                p.get("price"),
                p.get("rating"),
                p.get("reviews_count"),
                p.get("availability"),
                p.get("link"),
                p.get("category"),
                p.get("image_url"),
            ))
        conn.commit()
        conn.close()

    def get_products_by_session(self, session_id):
        """Return all products belonging to a session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT product_name, price, rating, reviews_count, availability,
                   product_link, category, image_url
            FROM products WHERE session_id = ?
        """, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_products(self):
        """Return all products across all sessions (for global analytics)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT product_name, price, rating, reviews_count, availability,
                   product_link, category, image_url
            FROM products
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_summary_stats(self):
        """Return aggregate statistics across all scraped products."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(price), MAX(price), MIN(price), AVG(rating) FROM products WHERE price IS NOT NULL")
        avg_price, max_price, min_price, avg_rating = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]

        conn.close()
        return {
            "total_products": total_products or 0,
            "avg_price": avg_price or 0,
            "max_price": max_price or 0,
            "min_price": min_price or 0,
            "avg_rating": avg_rating or 0,
            "total_sessions": total_sessions or 0,
        }
