"""Interactive Tkinter UI for the GPlay Scraper library.

This module exposes a small desktop interface that surfaces the most
common scraping workflows: analysing an app, running a search,
collecting reviews and fetching developer portfolios.  The UI is meant
for experimentation and learning – it keeps the inputs simple, validates
as much as possible and renders JSON responses in a scrollable viewer.
"""

from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Iterable

from gplay_scraper import GPlayScraper
from gplay_scraper.config import Config
from gplay_scraper.exceptions import GPlayScraperError


class GPlayScraperUI:
    """Main Tkinter application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("GPlay Scraper UI")
        self.root.geometry("900x650")

        self.scraper = GPlayScraper()

        self._build_layout()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        self.status_var = tk.StringVar(value="Ready")

        # Result viewer shared across tabs
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.result_text = tk.Text(result_frame, wrap=tk.NONE)
        self.result_text.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")

        x_scroll = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.result_text.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.result_text.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

        app_frame = ttk.Frame(notebook)
        search_frame = ttk.Frame(notebook)
        reviews_frame = ttk.Frame(notebook)
        developer_frame = ttk.Frame(notebook)

        notebook.add(app_frame, text="App")
        notebook.add(search_frame, text="Search")
        notebook.add(reviews_frame, text="Reviews")
        notebook.add(developer_frame, text="Developer")

        self._build_app_tab(app_frame)
        self._build_search_tab(search_frame)
        self._build_reviews_tab(reviews_frame)
        self._build_developer_tab(developer_frame)

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------
    def _build_app_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(1, weight=1)

        app_id_var = tk.StringVar(value="com.whatsapp")
        lang_var = tk.StringVar(value=Config.DEFAULT_LANGUAGE)
        country_var = tk.StringVar(value=Config.DEFAULT_COUNTRY)
        assets_var = tk.StringVar(value="SMALL")
        fields_var = tk.StringVar()

        ttk.Label(frame, text="App ID").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=app_id_var).grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Language").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=lang_var).grid(row=1, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Country").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=country_var).grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Assets Size").grid(row=3, column=0, sticky=tk.W, pady=5)
        assets_combo = ttk.Combobox(
            frame,
            textvariable=assets_var,
            values=["SMALL", "MEDIUM", "LARGE", "ORIGINAL", ""],
            state="readonly",
        )
        assets_combo.grid(row=3, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Fields (comma separated)").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=fields_var).grid(row=4, column=1, sticky=tk.EW, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame,
            text="Analyze App",
            command=lambda: self._run_async(
                self.scraper.app_analyze,
                app_id_var.get(),
                lang_var.get(),
                country_var.get(),
                assets_var.get() or None,
            ),
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Get Fields",
            command=lambda: self._handle_app_fields(
                app_id_var.get(),
                self._split_fields(fields_var.get()),
                lang_var.get(),
                country_var.get(),
                assets_var.get() or None,
            ),
        ).pack(side=tk.LEFT, padx=5)

    def _build_search_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(1, weight=1)

        query_var = tk.StringVar(value="productivity")
        count_var = tk.IntVar(value=Config.DEFAULT_SEARCH_COUNT)
        lang_var = tk.StringVar(value=Config.DEFAULT_LANGUAGE)
        country_var = tk.StringVar(value=Config.DEFAULT_COUNTRY)
        fields_var = tk.StringVar()

        ttk.Label(frame, text="Query").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=query_var).grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Count").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(frame, from_=1, to=200, textvariable=count_var).grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Language").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=lang_var).grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Country").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=country_var).grid(row=3, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Fields (comma separated)").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=fields_var).grid(row=4, column=1, sticky=tk.EW, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame,
            text="Search Apps",
            command=lambda: self._run_async(
                self.scraper.search_analyze,
                query_var.get(),
                count_var.get(),
                lang_var.get(),
                country_var.get(),
            ),
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Get Fields",
            command=lambda: self._handle_search_fields(
                query_var.get(),
                self._split_fields(fields_var.get()),
                count_var.get(),
                lang_var.get(),
                country_var.get(),
            ),
        ).pack(side=tk.LEFT, padx=5)

    def _build_reviews_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(1, weight=1)

        app_id_var = tk.StringVar(value="com.whatsapp")
        count_var = tk.IntVar(value=20)
        lang_var = tk.StringVar(value=Config.DEFAULT_LANGUAGE)
        country_var = tk.StringVar(value=Config.DEFAULT_COUNTRY)
        sort_var = tk.StringVar(value="NEWEST")
        fields_var = tk.StringVar()

        ttk.Label(frame, text="App ID").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=app_id_var).grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Count").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(frame, from_=1, to=200, textvariable=count_var).grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Language").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=lang_var).grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Country").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=country_var).grid(row=3, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Sort Order").grid(row=4, column=0, sticky=tk.W, pady=5)
        sort_combo = ttk.Combobox(frame, textvariable=sort_var, values=["NEWEST", "RELEVANT", "RATING"], state="readonly")
        sort_combo.grid(row=4, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Fields (comma separated)").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=fields_var).grid(row=5, column=1, sticky=tk.EW, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame,
            text="Get Reviews",
            command=lambda: self._run_async(
                self.scraper.reviews_analyze,
                app_id_var.get(),
                count_var.get(),
                lang_var.get(),
                country_var.get(),
                sort_var.get(),
            ),
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Get Fields",
            command=lambda: self._handle_reviews_fields(
                app_id_var.get(),
                self._split_fields(fields_var.get()),
                count_var.get(),
                lang_var.get(),
                country_var.get(),
                sort_var.get(),
            ),
        ).pack(side=tk.LEFT, padx=5)

    def _build_developer_tab(self, frame: ttk.Frame) -> None:
        frame.columnconfigure(1, weight=1)

        dev_id_var = tk.StringVar(value="5700313618786177705")
        count_var = tk.IntVar(value=20)
        lang_var = tk.StringVar(value=Config.DEFAULT_LANGUAGE)
        country_var = tk.StringVar(value=Config.DEFAULT_COUNTRY)
        fields_var = tk.StringVar()

        ttk.Label(frame, text="Developer ID").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=dev_id_var).grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Count").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(frame, from_=1, to=200, textvariable=count_var).grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Language").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=lang_var).grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Country").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=country_var).grid(row=3, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Fields (comma separated)").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=fields_var).grid(row=4, column=1, sticky=tk.EW, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame,
            text="List Apps",
            command=lambda: self._run_async(
                self.scraper.developer_analyze,
                dev_id_var.get(),
                count_var.get(),
                lang_var.get(),
                country_var.get(),
            ),
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Get Fields",
            command=lambda: self._handle_developer_fields(
                dev_id_var.get(),
                self._split_fields(fields_var.get()),
                count_var.get(),
                lang_var.get(),
                country_var.get(),
            ),
        ).pack(side=tk.LEFT, padx=5)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _handle_app_fields(
        self,
        app_id: str,
        fields: Iterable[str],
        lang: str,
        country: str,
        assets: str | None,
    ) -> None:
        if not fields:
            messagebox.showinfo("Fields Required", "Please provide at least one field name.")
            return

        self._run_async(
            self.scraper.app_get_fields,
            app_id,
            list(fields),
            lang,
            country,
            assets,
        )

    def _handle_search_fields(
        self,
        query: str,
        fields: Iterable[str],
        count: int,
        lang: str,
        country: str,
    ) -> None:
        if not fields:
            messagebox.showinfo("Fields Required", "Please provide at least one field name.")
            return

        self._run_async(
            self.scraper.search_get_fields,
            query,
            list(fields),
            count,
            lang,
            country,
        )

    def _handle_reviews_fields(
        self,
        app_id: str,
        fields: Iterable[str],
        count: int,
        lang: str,
        country: str,
        sort: str,
    ) -> None:
        if not fields:
            messagebox.showinfo("Fields Required", "Please provide at least one field name.")
            return

        self._run_async(
            self.scraper.reviews_get_fields,
            app_id,
            list(fields),
            count,
            lang,
            country,
            sort,
        )

    def _handle_developer_fields(
        self,
        dev_id: str,
        fields: Iterable[str],
        count: int,
        lang: str,
        country: str,
    ) -> None:
        if not fields:
            messagebox.showinfo("Fields Required", "Please provide at least one field name.")
            return

        self._run_async(
            self.scraper.developer_get_fields,
            dev_id,
            list(fields),
            count,
            lang,
            country,
        )

    # ------------------------------------------------------------------
    # Async execution helpers
    # ------------------------------------------------------------------
    def _run_async(self, func: Any, *args: Any) -> None:
        self._set_status("Running...")
        self._clear_results()

        def task() -> None:
            try:
                data = func(*args)
            except GPlayScraperError as exc:
                self.root.after(0, lambda: self._handle_error(f"Scraper error: {exc}"))
            except Exception as exc:  # pragma: no cover - unexpected errors
                self.root.after(0, lambda: self._handle_error(f"Unexpected error: {exc}"))
            else:
                self.root.after(0, lambda: self._handle_success(data))

        threading.Thread(target=task, daemon=True).start()

    def _handle_success(self, data: Any) -> None:
        self._display_result(data)
        self._set_status("Finished")

    def _handle_error(self, message: str) -> None:
        self._show_error(message)

    # ------------------------------------------------------------------
    # Result helpers
    # ------------------------------------------------------------------
    def _display_result(self, data: Any) -> None:
        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        self.result_text.insert("1.0", pretty)

    def _clear_results(self) -> None:
        self.result_text.delete("1.0", tk.END)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _show_error(self, message: str) -> None:
        self._set_status("Error")
        messagebox.showerror("GPlay Scraper", message)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    @staticmethod
    def _split_fields(raw: str) -> list[str]:
        return [field.strip() for field in raw.split(",") if field.strip()]


def main() -> None:
    root = tk.Tk()
    GPlayScraperUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
