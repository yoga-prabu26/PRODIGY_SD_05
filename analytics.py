"""
analytics.py
------------
Computes analytical statistics from product data and generates
matplotlib chart figures for the Analytics Dashboard.
"""

import matplotlib
matplotlib.use("Agg")  # Safe backend before embedding in CustomTkinter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from collections import Counter
import pandas as pd


class AnalyticsEngine:
    """Generates statistics and charts from scraped product data."""

    DARK_BG = "#1a1a2e"
    PURPLE = "#9d4edd"
    BLUE = "#4361ee"
    TEXT_COLOR = "#e0e0e0"

    def __init__(self, theme="dark"):
        self.theme = theme

    def _style_axes(self, ax, fig):
        if self.theme == "dark":
            fig.patch.set_facecolor(self.DARK_BG)
            ax.set_facecolor(self.DARK_BG)
            ax.tick_params(colors=self.TEXT_COLOR)
            ax.title.set_color(self.TEXT_COLOR)
            ax.xaxis.label.set_color(self.TEXT_COLOR)
            ax.yaxis.label.set_color(self.TEXT_COLOR)
            for spine in ax.spines.values():
                spine.set_color("#444466")
        else:
            fig.patch.set_facecolor("#ffffff")
            ax.set_facecolor("#f5f5f7")

    # ------------------------------------------------------------------
    # DATAFRAME HELPERS
    # ------------------------------------------------------------------
    @staticmethod
    def to_dataframe(products):
        """Convert raw product tuples/dicts into a pandas DataFrame."""
        columns = ["name", "price", "rating", "reviews_count",
                   "availability", "link", "category", "image_url"]
        if not products:
            return pd.DataFrame(columns=columns)
        if isinstance(products[0], dict):
            return pd.DataFrame(products)
        return pd.DataFrame(products, columns=columns)

    def compute_stats(self, products):
        """Return summary statistics dictionary for a product list."""
        df = self.to_dataframe(products)
        if df.empty:
            return {
                "total_products": 0, "avg_price": 0, "max_price": 0,
                "min_price": 0, "avg_rating": 0
            }
        return {
            "total_products": len(df),
            "avg_price": round(df["price"].mean(), 2),
            "max_price": round(df["price"].max(), 2),
            "min_price": round(df["price"].min(), 2),
            "avg_rating": round(df["rating"].mean(), 2),
        }

    # ------------------------------------------------------------------
    # CHART GENERATORS
    # ------------------------------------------------------------------
    def price_distribution_chart(self, products):
        df = self.to_dataframe(products)
        fig = Figure(figsize=(5, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        if not df.empty:
            ax.hist(df["price"].dropna(), bins=10, color=self.PURPLE, edgecolor="white")
        ax.set_title("Price Distribution")
        ax.set_xlabel("Price")
        ax.set_ylabel("Count")
        self._style_axes(ax, fig)
        fig.tight_layout()
        return fig

    def rating_distribution_chart(self, products):
        df = self.to_dataframe(products)
        fig = Figure(figsize=(5, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        if not df.empty:
            ax.hist(df["rating"].dropna(), bins=8, color=self.BLUE, edgecolor="white")
        ax.set_title("Rating Distribution")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        self._style_axes(ax, fig)
        fig.tight_layout()
        return fig

    def category_distribution_chart(self, products):
        df = self.to_dataframe(products)
        fig = Figure(figsize=(5, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        if not df.empty:
            counts = Counter(df["category"].dropna())
            labels = list(counts.keys())
            values = list(counts.values())
            colors = [self.PURPLE, self.BLUE, "#7209b7", "#3a0ca3",
                      "#4895ef", "#560bad", "#480ca8", "#b5179e"]
            ax.pie(values, labels=labels, autopct="%1.0f%%",
                   colors=colors[:len(labels)],
                   textprops={"color": self.TEXT_COLOR if self.theme == "dark" else "#222"})
        ax.set_title("Category Distribution")
        if self.theme == "dark":
            fig.patch.set_facecolor(self.DARK_BG)
        fig.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # KEYWORD / SEO BONUS FEATURES
    # ------------------------------------------------------------------
    @staticmethod
    def extract_keywords(products, top_n=10):
        """Extract most common keywords from product names."""
        df = AnalyticsEngine.to_dataframe(products)
        if df.empty:
            return []
        words = []
        stopwords = {"the", "a", "an", "for", "with", "and", "of", "to", "in", "-"}
        for name in df["name"].dropna():
            for w in str(name).lower().split():
                w = w.strip(".,()-")
                if len(w) > 2 and w not in stopwords:
                    words.append(w)
        return Counter(words).most_common(top_n)
