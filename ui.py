"""
ui.py
-----
The View/Controller layer of WebScrapeX Pro, built with CustomTkinter.

Contains:
    - SidebarFrame: navigation sidebar
    - DashboardPage, ScraperPage, AnalyticsPage, ExportPage,
      HistoryPage, SettingsPage
    - App: main application window that wires everything together
"""

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scraper import WebScraper
from database import DatabaseManager
from analytics import AnalyticsEngine
from exporter import DataExporter

# ----------------------------------------------------------------------
# THEME CONSTANTS
# ----------------------------------------------------------------------
DARK_BG = "#13111c"
DARK_SURFACE = "#1e1b2e"
DARK_CARD = "#262138"
PURPLE = "#9d4edd"
PURPLE_HOVER = "#7b2cbf"
BLUE_ACCENT = "#4361ee"
TEXT_LIGHT = "#e0e0e0"
TEXT_MUTED = "#9b9bb5"

LIGHT_BG = "#f4f4f8"
LIGHT_SURFACE = "#ffffff"
LIGHT_CARD = "#ffffff"


class SidebarFrame(ctk.CTkFrame):
    """Left navigation sidebar."""

    def __init__(self, master, on_nav, **kwargs):
        super().__init__(master, width=220, corner_radius=0, **kwargs)
        self.on_nav = on_nav
        self.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(
            self, text="⚡ WebScrapeX Pro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=PURPLE
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5), sticky="w")

        self.subtitle = ctk.CTkLabel(
            self, text="Data Intelligence Platform",
            font=ctk.CTkFont(size=11), text_color=TEXT_MUTED
        )
        self.subtitle.grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Scraper", "scraper"),
            ("Analytics", "analytics"),
            ("Export Center", "export"),
            ("History", "history"),
            ("Settings", "settings"),
        ]

        for i, (label, key) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self, text=f"  {label}", anchor="w",
                fg_color="transparent", hover_color=DARK_CARD,
                font=ctk.CTkFont(size=14),
                command=lambda k=key: self.on_nav(k)
            )
            btn.grid(row=i, column=0, padx=15, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        self.version_label = ctk.CTkLabel(
            self, text="v1.0.0 — PRODIGY_SD_05",
            font=ctk.CTkFont(size=10), text_color=TEXT_MUTED
        )
        self.version_label.grid(row=9, column=0, padx=20, pady=15, sticky="w")

    def set_active(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=PURPLE, hover_color=PURPLE_HOVER, text_color="white")
            else:
                btn.configure(fg_color="transparent", hover_color=DARK_CARD, text_color=TEXT_LIGHT)


class StatCard(ctk.CTkFrame):
    """A small KPI card used on dashboard/analytics pages."""

    def __init__(self, master, title, value, accent=PURPLE, **kwargs):
        super().__init__(master, corner_radius=12, fg_color=DARK_CARD, **kwargs)
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=12),
                                         text_color=TEXT_MUTED)
        self.title_label.pack(anchor="w", padx=18, pady=(15, 0))

        self.value_label = ctk.CTkLabel(self, text=str(value),
                                         font=ctk.CTkFont(size=26, weight="bold"),
                                         text_color=accent)
        self.value_label.pack(anchor="w", padx=18, pady=(0, 15))

    def set_value(self, value):
        self.value_label.configure(text=str(value))


# ----------------------------------------------------------------------
# DASHBOARD PAGE
# ----------------------------------------------------------------------
class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app

        header = ctk.CTkLabel(self, text="Home Dashboard",
                               font=ctk.CTkFont(size=26, weight="bold"))
        header.pack(anchor="w", padx=30, pady=(25, 5))

        sub = ctk.CTkLabel(self, text="Overview of your data extraction activity",
                            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
        sub.pack(anchor="w", padx=30, pady=(0, 20))

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        self.card_total = StatCard(cards_frame, "Total Products Scraped", "0", PURPLE)
        self.card_total.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        self.card_avg_price = StatCard(cards_frame, "Average Price", "$0.00", BLUE_ACCENT)
        self.card_avg_price.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self.card_avg_rating = StatCard(cards_frame, "Average Rating", "0.0 ★", PURPLE)
        self.card_avg_rating.grid(row=0, column=2, padx=8, pady=8, sticky="ew")

        self.card_sessions = StatCard(cards_frame, "Scrape Sessions", "0", BLUE_ACCENT)
        self.card_sessions.grid(row=0, column=3, padx=8, pady=8, sticky="ew")

        # Quick actions
        actions_frame = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        actions_frame.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(actions_frame, text="Quick Actions",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))

        btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(btn_frame, text="🔍 Start New Scrape", fg_color=PURPLE,
                       hover_color=PURPLE_HOVER, height=40,
                       command=lambda: self.app.navigate("scraper")).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_frame, text="📊 View Analytics", fg_color=BLUE_ACCENT,
                       hover_color="#3046c4", height=40,
                       command=lambda: self.app.navigate("analytics")).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="📁 Export Data", fg_color="transparent",
                       border_width=1, border_color=PURPLE, height=40,
                       command=lambda: self.app.navigate("export")).pack(side="left", padx=10)

        # Recent activity
        recent_frame = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        recent_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        ctk.CTkLabel(recent_frame, text="Recent Scrape Sessions",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(15, 10))

        self.recent_list = ctk.CTkScrollableFrame(recent_frame, fg_color="transparent")
        self.recent_list.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def refresh(self):
        stats = self.app.db.get_summary_stats()
        self.card_total.set_value(stats["total_products"])
        self.card_avg_price.set_value(f"${stats['avg_price']:.2f}")
        self.card_avg_rating.set_value(f"{stats['avg_rating']:.1f} ★")
        self.card_sessions.set_value(stats["total_sessions"])

        for widget in self.recent_list.winfo_children():
            widget.destroy()

        sessions = self.app.db.get_all_sessions()[:5]
        if not sessions:
            ctk.CTkLabel(self.recent_list, text="No scraping sessions yet. Start one from the Scraper page.",
                          text_color=TEXT_MUTED).pack(anchor="w", pady=10)
            return

        for sid, name, url, date, total in sessions:
            row = ctk.CTkFrame(self.recent_list, fg_color=DARK_SURFACE, corner_radius=8)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"🌐 {name}", font=ctk.CTkFont(weight="bold")).pack(
                side="left", padx=15, pady=10)
            ctk.CTkLabel(row, text=f"{total} products", text_color=TEXT_MUTED).pack(
                side="left", padx=15)
            ctk.CTkLabel(row, text=date, text_color=TEXT_MUTED).pack(side="right", padx=15)


# ----------------------------------------------------------------------
# SCRAPER PAGE
# ----------------------------------------------------------------------
class ScraperPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.current_results = []

        header = ctk.CTkLabel(self, text="Scraper", font=ctk.CTkFont(size=26, weight="bold"))
        header.pack(anchor="w", padx=30, pady=(25, 5))

        sub = ctk.CTkLabel(self, text="Connect to a website and extract product data",
                            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
        sub.pack(anchor="w", padx=30, pady=(0, 20))

        # --- Input Panel ---
        input_frame = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        input_frame.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkLabel(input_frame, text="Website URL", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(15, 5))

        row = ctk.CTkFrame(input_frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 10))
        row.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(row, placeholder_text="https://example.com/products",
                                       height=40, font=ctk.CTkFont(size=13))
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.url_entry.insert(0, "https://example.com/products")

        self.connect_btn = ctk.CTkButton(row, text="Connect", width=110, height=40,
                                          fg_color=BLUE_ACCENT, hover_color="#3046c4",
                                          command=self.test_connection)
        self.connect_btn.grid(row=0, column=1, padx=(0, 10))

        self.scrape_btn = ctk.CTkButton(row, text="Start Scraping", width=140, height=40,
                                         fg_color=PURPLE, hover_color=PURPLE_HOVER,
                                         command=self.start_scraping)
        self.scrape_btn.grid(row=0, column=2)

        self.status_label = ctk.CTkLabel(input_frame, text="Status: Not connected",
                                          text_color=TEXT_MUTED)
        self.status_label.pack(anchor="w", padx=20, pady=(0, 10))

        # --- Progress ---
        progress_frame = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        progress_frame.pack(fill="x", padx=30, pady=(0, 15))

        self.progress_label = ctk.CTkLabel(progress_frame, text="Idle", text_color=TEXT_MUTED)
        self.progress_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.progress_bar = ctk.CTkProgressBar(progress_frame, progress_color=PURPLE)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 15))
        self.progress_bar.set(0)

        # --- Search/Filter Bar ---
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="🔍 Search products...",
                                          height=36, width=250)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        self.category_filter = ctk.CTkOptionMenu(filter_frame, values=["All Categories"],
                                                   width=180, fg_color=DARK_CARD,
                                                   button_color=PURPLE, command=lambda v: self.refresh_table())
        self.category_filter.pack(side="left", padx=10)

        self.availability_filter = ctk.CTkOptionMenu(
            filter_frame, values=["All Availability", "In Stock", "Out of Stock", "Limited Stock"],
            width=180, fg_color=DARK_CARD, button_color=PURPLE,
            command=lambda v: self.refresh_table())
        self.availability_filter.pack(side="left", padx=10)

        # --- Data Table ---
        table_frame = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=DARK_SURFACE, fieldbackground=DARK_SURFACE,
                        foreground=TEXT_LIGHT, rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background=DARK_CARD, foreground=PURPLE,
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", PURPLE)])

        columns = ("name", "price", "rating", "reviews", "availability", "category")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = {
            "name": "Product Name", "price": "Price ($)", "rating": "Rating",
            "reviews": "Reviews", "availability": "Availability", "category": "Category"
        }
        for col in columns:
            self.tree.heading(col, text=headings[col],
                               command=lambda c=col: self.sort_by_column(c, False))
            self.tree.column(col, width=150 if col == "name" else 100, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=15, pady=15, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", pady=15)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- Pagination ---
        pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        pagination_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.page = 0
        self.page_size = 10
        self.filtered_data = []

        self.prev_btn = ctk.CTkButton(pagination_frame, text="◀ Previous", width=110,
                                       fg_color=DARK_CARD, command=self.prev_page)
        self.prev_btn.pack(side="left")

        self.page_label = ctk.CTkLabel(pagination_frame, text="Page 1 of 1")
        self.page_label.pack(side="left", padx=15)

        self.next_btn = ctk.CTkButton(pagination_frame, text="Next ▶", width=110,
                                       fg_color=DARK_CARD, command=self.next_page)
        self.next_btn.pack(side="left")

        self.sort_reverse = {}

    # ------------------------------------------------------------------
    def test_connection(self):
        url = self.url_entry.get().strip()
        self.status_label.configure(text="Status: Testing connection...", text_color=TEXT_MUTED)

        def task():
            success, msg = self.app.scraper.test_connection(url)
            color = "#4ade80" if success else "#f87171"
            self.status_label.configure(text=f"Status: {msg}", text_color=color)

        threading.Thread(target=task, daemon=True).start()

    def start_scraping(self):
        url = self.url_entry.get().strip()
        if not self.app.scraper.is_valid_url(url):
            messagebox.showerror("Invalid URL", "Please enter a valid URL (must start with http:// or https://)")
            return

        self.scrape_btn.configure(state="disabled", text="Scraping...")
        self.connect_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Initializing scraper...")

        def progress_cb(percent, message):
            self.after(0, lambda: self._update_progress(percent, message))

        def task():
            try:
                products = self.app.scraper.scrape_products(url, max_items=24, progress_callback=progress_cb)
                self.after(0, lambda: self._on_scrape_complete(url, products))
            except Exception as e:
                self.after(0, lambda: self._on_scrape_error(str(e)))

        threading.Thread(target=task, daemon=True).start()

    def _update_progress(self, percent, message):
        self.progress_bar.set(percent / 100)
        self.progress_label.configure(text=f"{message} ({percent}%)")

    def _on_scrape_complete(self, url, products):
        self.current_results = products
        self.scrape_btn.configure(state="normal", text="Start Scraping")
        self.connect_btn.configure(state="normal")
        self.progress_label.configure(text=f"Completed — {len(products)} products extracted")

        # Save to database
        from urllib.parse import urlparse
        domain = urlparse(url).netloc or "Unknown Site"
        session_id = self.app.db.create_session(domain, url, len(products))
        self.app.db.insert_products(session_id, products)

        # Update category filter
        categories = sorted(set(p["category"] for p in products))
        self.category_filter.configure(values=["All Categories"] + categories)

        self.app.set_active_results(products)
        self.refresh_table()
        self.app.refresh_all_pages()
        messagebox.showinfo("Scraping Complete", f"Successfully extracted {len(products)} products from {domain}")

    def _on_scrape_error(self, error_msg):
        self.scrape_btn.configure(state="normal", text="Start Scraping")
        self.connect_btn.configure(state="normal")
        self.progress_label.configure(text="Error during scraping")
        messagebox.showerror("Scraping Error", f"An error occurred: {error_msg}")

    # ------------------------------------------------------------------
    def refresh_table(self):
        data = self.current_results

        search_term = self.search_entry.get().lower().strip()
        category = self.category_filter.get()
        availability = self.availability_filter.get()

        filtered = []
        for p in data:
            if search_term and search_term not in p["name"].lower():
                continue
            if category != "All Categories" and p["category"] != category:
                continue
            if availability != "All Availability" and p["availability"] != availability:
                continue
            filtered.append(p)

        self.filtered_data = filtered
        self.page = 0
        self._render_page()

    def _render_page(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        start = self.page * self.page_size
        end = start + self.page_size
        page_items = self.filtered_data[start:end]

        for p in page_items:
            self.tree.insert("", "end", values=(
                p["name"], f"{p['price']:.2f}", f"{p['rating']:.1f}",
                p["reviews_count"], p["availability"], p["category"]
            ))

        total_pages = max(1, (len(self.filtered_data) + self.page_size - 1) // self.page_size)
        self.page_label.configure(text=f"Page {self.page + 1} of {total_pages}")

    def next_page(self):
        total_pages = max(1, (len(self.filtered_data) + self.page_size - 1) // self.page_size)
        if self.page < total_pages - 1:
            self.page += 1
            self._render_page()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._render_page()

    def sort_by_column(self, col, reverse):
        key_map = {
            "name": lambda p: p["name"].lower(),
            "price": lambda p: p["price"],
            "rating": lambda p: p["rating"],
            "reviews": lambda p: p["reviews_count"],
            "availability": lambda p: p["availability"],
            "category": lambda p: p["category"],
        }
        reverse = self.sort_reverse.get(col, False)
        self.filtered_data.sort(key=key_map[col], reverse=reverse)
        self.sort_reverse[col] = not reverse
        self._render_page()


# ----------------------------------------------------------------------
# ANALYTICS PAGE
# ----------------------------------------------------------------------
class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.chart_canvases = []

        header = ctk.CTkLabel(self, text="Analytics Dashboard",
                               font=ctk.CTkFont(size=26, weight="bold"))
        header.pack(anchor="w", padx=30, pady=(25, 5))

        sub = ctk.CTkLabel(self, text="Insights derived from your scraped product data",
                            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
        sub.pack(anchor="w", padx=30, pady=(0, 20))

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        for i in range(5):
            cards_frame.grid_columnconfigure(i, weight=1)

        self.card_total = StatCard(cards_frame, "Total Products", "0", PURPLE)
        self.card_total.grid(row=0, column=0, padx=6, pady=8, sticky="ew")
        self.card_avg_price = StatCard(cards_frame, "Avg Price", "$0.00", BLUE_ACCENT)
        self.card_avg_price.grid(row=0, column=1, padx=6, pady=8, sticky="ew")
        self.card_max_price = StatCard(cards_frame, "Highest Price", "$0.00", PURPLE)
        self.card_max_price.grid(row=0, column=2, padx=6, pady=8, sticky="ew")
        self.card_min_price = StatCard(cards_frame, "Lowest Price", "$0.00", BLUE_ACCENT)
        self.card_min_price.grid(row=0, column=3, padx=6, pady=8, sticky="ew")
        self.card_avg_rating = StatCard(cards_frame, "Avg Rating", "0.0 ★", PURPLE)
        self.card_avg_rating.grid(row=0, column=4, padx=6, pady=8, sticky="ew")

        # Charts
        self.charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True, padx=30, pady=10)
        self.charts_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.chart_holders = []
        for i in range(3):
            holder = ctk.CTkFrame(self.charts_frame, fg_color=DARK_CARD, corner_radius=12)
            holder.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
            self.chart_holders.append(holder)

        # Keyword extraction (bonus)
        self.keyword_frame = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        self.keyword_frame.pack(fill="x", padx=30, pady=(0, 25))
        ctk.CTkLabel(self.keyword_frame, text="🔑 Top Keywords (SEO Insight)",
                      font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        self.keyword_label = ctk.CTkLabel(self.keyword_frame, text="No data yet.",
                                           text_color=TEXT_MUTED, justify="left", wraplength=900)
        self.keyword_label.pack(anchor="w", padx=20, pady=(0, 15))

    def refresh(self):
        products = self.app.get_active_results()
        engine = self.app.analytics
        engine.theme = self.app.current_theme

        stats = engine.compute_stats(products)
        self.card_total.set_value(stats["total_products"])
        self.card_avg_price.set_value(f"${stats['avg_price']:.2f}")
        self.card_max_price.set_value(f"${stats['max_price']:.2f}")
        self.card_min_price.set_value(f"${stats['min_price']:.2f}")
        self.card_avg_rating.set_value(f"{stats['avg_rating']:.1f} ★")

        # Clear old charts
        for holder in self.chart_holders:
            for widget in holder.winfo_children():
                widget.destroy()

        if not products:
            for holder in self.chart_holders:
                ctk.CTkLabel(holder, text="No data\nRun a scrape first", text_color=TEXT_MUTED).pack(
                    expand=True, pady=40)
            self.keyword_label.configure(text="No data yet. Run a scraping session to see keyword insights.")
            return

        figs = [
            engine.price_distribution_chart(products),
            engine.rating_distribution_chart(products),
            engine.category_distribution_chart(products),
        ]

        for holder, fig in zip(self.chart_holders, figs):
            canvas = FigureCanvasTkAgg(fig, master=holder)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        keywords = engine.extract_keywords(products, top_n=12)
        keyword_text = "   ".join(f"#{w} ({c})" for w, c in keywords)
        self.keyword_label.configure(text=keyword_text or "No keywords found.")


# ----------------------------------------------------------------------
# EXPORT PAGE
# ----------------------------------------------------------------------
class ExportPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app

        header = ctk.CTkLabel(self, text="Export Center", font=ctk.CTkFont(size=26, weight="bold"))
        header.pack(anchor="w", padx=30, pady=(25, 5))

        sub = ctk.CTkLabel(self, text="Export your extracted product data to common formats",
                            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
        sub.pack(anchor="w", padx=30, pady=(0, 20))

        self.info_label = ctk.CTkLabel(self, text="0 products available for export",
                                        text_color=TEXT_MUTED)
        self.info_label.pack(anchor="w", padx=30, pady=(0, 10))

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._export_card(cards_frame, 0, "📄 CSV File", "Comma-separated values, ideal for spreadsheets",
                           "Export to CSV", self.export_csv)
        self._export_card(cards_frame, 1, "📊 Excel Workbook", "Formatted .xlsx with auto-sized columns",
                           "Export to Excel", self.export_excel)
        self._export_card(cards_frame, 2, "🧾 JSON File", "Structured JSON for developers & APIs",
                           "Export to JSON", self.export_json)

        self.result_label = ctk.CTkLabel(self, text="", text_color="#4ade80")
        self.result_label.pack(anchor="w", padx=30, pady=15)

    def _export_card(self, parent, col, title, desc, btn_text, command):
        card = ctk.CTkFrame(parent, fg_color=DARK_CARD, corner_radius=12)
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(card, text=desc, text_color=TEXT_MUTED, wraplength=200, justify="left").pack(
            anchor="w", padx=20, pady=(0, 15))
        ctk.CTkButton(card, text=btn_text, fg_color=PURPLE, hover_color=PURPLE_HOVER,
                       command=command).pack(anchor="w", padx=20, pady=(0, 20))

    def refresh(self):
        count = len(self.app.get_active_results())
        self.info_label.configure(text=f"{count} products available for export")

    def _export(self, fn, label):
        products = self.app.get_active_results()
        if not products:
            messagebox.showwarning("No Data", "No product data available to export. Run a scrape first.")
            return
        path = fn(products)
        self.result_label.configure(text=f"✅ {label} exported successfully to: {path}")
        messagebox.showinfo("Export Complete", f"{label} saved to:\n{path}")

    def export_csv(self):
        self._export(self.app.exporter.export_csv, "CSV")

    def export_excel(self):
        self._export(self.app.exporter.export_excel, "Excel")

    def export_json(self):
        self._export(self.app.exporter.export_json, "JSON")


# ----------------------------------------------------------------------
# HISTORY PAGE
# ----------------------------------------------------------------------
class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app

        header = ctk.CTkLabel(self, text="Scrape History", font=ctk.CTkFont(size=26, weight="bold"))
        header.pack(anchor="w", padx=30, pady=(25, 5))

        sub = ctk.CTkLabel(self, text="View, reopen, or delete previous scraping sessions",
                            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
        sub.pack(anchor="w", padx=30, pady=(0, 20))

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=DARK_CARD, corner_radius=12)
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))

    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        sessions = self.app.db.get_all_sessions()
        if not sessions:
            ctk.CTkLabel(self.list_frame, text="No scraping sessions found.",
                          text_color=TEXT_MUTED).pack(pady=20)
            return

        for sid, name, url, date, total in sessions:
            row = ctk.CTkFrame(self.list_frame, fg_color=DARK_SURFACE, corner_radius=8)
            row.pack(fill="x", pady=5, padx=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            ctk.CTkLabel(info, text=f"🌐 {name}", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"{url}", text_color=TEXT_MUTED, font=ctk.CTkFont(size=11)).pack(anchor="w")
            ctk.CTkLabel(info, text=f"{date}  •  {total} products", text_color=TEXT_MUTED,
                          font=ctk.CTkFont(size=11)).pack(anchor="w")

            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="right", padx=15)

            ctk.CTkButton(btn_frame, text="View Results", width=110, fg_color=PURPLE,
                           hover_color=PURPLE_HOVER,
                           command=lambda s=sid: self.view_session(s)).pack(side="left", padx=5)

            ctk.CTkButton(btn_frame, text="Delete", width=80, fg_color="#e63946",
                           hover_color="#c1121f",
                           command=lambda s=sid: self.delete_session(s)).pack(side="left", padx=5)

    def view_session(self, session_id):
        rows = self.app.db.get_products_by_session(session_id)
        products = []
        for r in rows:
            products.append({
                "name": r[0], "price": r[1], "rating": r[2], "reviews_count": r[3],
                "availability": r[4], "link": r[5], "category": r[6], "image_url": r[7]
            })
        self.app.set_active_results(products)
        self.app.scraper_page.current_results = products
        self.app.scraper_page.refresh_table()
        categories = sorted(set(p["category"] for p in products))
        self.app.scraper_page.category_filter.configure(values=["All Categories"] + categories)
        self.app.navigate("scraper")
        self.app.refresh_all_pages()

    def delete_session(self, session_id):
        if messagebox.askyesno("Delete Session", "Are you sure you want to delete this session and all its data?"):
            self.app.db.delete_session(session_id)
            self.refresh()
            self.app.dashboard_page.refresh()


# ----------------------------------------------------------------------
# SETTINGS PAGE
# ----------------------------------------------------------------------
class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app

        header = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=26, weight="bold"))
        header.pack(anchor="w", padx=30, pady=(25, 5))

        sub = ctk.CTkLabel(self, text="Customize WebScrapeX Pro to your preferences",
                            font=ctk.CTkFont(size=13), text_color=TEXT_MUTED)
        sub.pack(anchor="w", padx=30, pady=(0, 20))

        # Theme settings
        theme_card = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        theme_card.pack(fill="x", padx=30, pady=(0, 15))
        ctk.CTkLabel(theme_card, text="Appearance", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(15, 10))

        theme_row = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_row.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(theme_row, text="Theme Mode:").pack(side="left", padx=(0, 10))
        self.theme_menu = ctk.CTkOptionMenu(theme_row, values=["Dark", "Light"],
                                             fg_color=DARK_SURFACE, button_color=PURPLE,
                                             command=self.change_theme)
        self.theme_menu.set("Dark")
        self.theme_menu.pack(side="left")

        # Export preferences
        export_card = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        export_card.pack(fill="x", padx=30, pady=(0, 15))
        ctk.CTkLabel(export_card, text="Export Preferences", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(15, 10))

        export_row = ctk.CTkFrame(export_card, fg_color="transparent")
        export_row.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(export_row, text="Default export folder:").pack(side="left", padx=(0, 10))
        self.export_path_label = ctk.CTkLabel(export_row, text=self.app.exporter.export_dir,
                                               text_color=TEXT_MUTED)
        self.export_path_label.pack(side="left", padx=(0, 10))
        ctk.CTkButton(export_row, text="Change Folder", fg_color=PURPLE, hover_color=PURPLE_HOVER,
                       command=self.change_export_folder).pack(side="left")

        # Database settings
        db_card = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        db_card.pack(fill="x", padx=30, pady=(0, 15))
        ctk.CTkLabel(db_card, text="Database Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(15, 10))

        db_row = ctk.CTkFrame(db_card, fg_color="transparent")
        db_row.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(db_row, text=f"Database path: {self.app.db.db_path}", text_color=TEXT_MUTED).pack(side="left")

        # Scraper settings
        scraper_card = ctk.CTkFrame(self, fg_color=DARK_CARD, corner_radius=12)
        scraper_card.pack(fill="x", padx=30, pady=(0, 15))
        ctk.CTkLabel(scraper_card, text="Scraper Configuration", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=20, pady=(15, 10))

        scraper_row = ctk.CTkFrame(scraper_card, fg_color="transparent")
        scraper_row.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(scraper_row, text="Max retries:").pack(side="left", padx=(0, 10))
        self.retry_slider = ctk.CTkSlider(scraper_row, from_=1, to=5, number_of_steps=4,
                                           command=self.change_retries, progress_color=PURPLE)
        self.retry_slider.set(self.app.scraper.max_retries)
        self.retry_slider.pack(side="left", padx=(0, 10))
        self.retry_value_label = ctk.CTkLabel(scraper_row, text=str(self.app.scraper.max_retries))
        self.retry_value_label.pack(side="left")

    def change_theme(self, value):
        self.app.set_theme(value.lower())

    def change_export_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.app.exporter.export_dir = folder
            self.export_path_label.configure(text=folder)

    def change_retries(self, value):
        retries = int(value)
        self.app.scraper.max_retries = retries
        self.retry_value_label.configure(text=str(retries))


# ----------------------------------------------------------------------
# MAIN APPLICATION
# ----------------------------------------------------------------------
class App(ctk.CTk):
    """Main application window — wires together all pages and services."""

    def __init__(self):
        super().__init__()

        self.title("WebScrapeX Pro — Data Intelligence Platform")
        self.geometry("1280x780")
        self.minsize(1100, 650)

        self.current_theme = "dark"
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Services (Model layer)
        self.scraper = WebScraper()
        self.db = DatabaseManager()
        self.analytics = AnalyticsEngine(theme="dark")
        self.exporter = DataExporter()
        self._active_results = []

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = SidebarFrame(self, on_nav=self.navigate, fg_color=DARK_SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.main_container = ctk.CTkFrame(self, fg_color=DARK_BG, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Pages
        self.dashboard_page = DashboardPage(self.main_container, self)
        self.scraper_page = ScraperPage(self.main_container, self)
        self.analytics_page = AnalyticsPage(self.main_container, self)
        self.export_page = ExportPage(self.main_container, self)
        self.history_page = HistoryPage(self.main_container, self)
        self.settings_page = SettingsPage(self.main_container, self)

        self.pages = {
            "dashboard": self.dashboard_page,
            "scraper": self.scraper_page,
            "analytics": self.analytics_page,
            "export": self.export_page,
            "history": self.history_page,
            "settings": self.settings_page,
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.navigate("dashboard")

    # ------------------------------------------------------------------
    def navigate(self, key):
        self.pages[key].tkraise()
        self.sidebar.set_active(key)
        if hasattr(self.pages[key], "refresh"):
            self.pages[key].refresh()

    def set_active_results(self, products):
        self._active_results = products

    def get_active_results(self):
        return self._active_results

    def refresh_all_pages(self):
        self.dashboard_page.refresh()
        self.export_page.refresh()
        if self.analytics_page.winfo_ismapped():
            self.analytics_page.refresh()

    def set_theme(self, mode):
        self.current_theme = mode
        ctk.set_appearance_mode(mode)
        self.analytics.theme = mode
        if self.analytics_page.winfo_ismapped():
            self.analytics_page.refresh()
