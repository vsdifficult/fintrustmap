"""
FinTrustMap - Heatmap grouped by Federal Districts (GUI)
Version: 1.2.0
License: MIT
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime
import math

# ---------------------------------------------------------------------
# Маппинг регионов по федеральным округам (включены основные регионы)
# Если в твоём Excel имена регионов отличаются — можно расширить/дополнить список
# ---------------------------------------------------------------------
FEDERAL_DISTRICTS = {
    "Центральный ФО": [
        "Белгородская область","Брянская область","Владимирская область","Воронежская область",
        "Ивановская область","Калужская область","Костромская область","Курская область",
        "Липецкая область","Московская область","Орловская область","Рязанская область",
        "Смоленская область","Тамбовская область","Тверская область","Тульская область",
        "Ярославская область","Москва"
    ],
    "Северо-Западный ФО": [
        "Республика Карелия","Республика Коми","Архангельская область","Вологодская область",
        "Калининградская область","Ленинградская область","Мурманская область",
        "Новгородская область","Псковская область","Санкт-Петербург","Ненецкий АО"
    ],
    "Южный ФО": [
        "Республика Адыгея","Республика Калмыкия","Республика Крым","Краснодарский край",
        "Астраханская область","Волгоградская область","Ростовская область","Севастополь"
    ],
    "Северо-Кавказский ФО": [
        "Республика Дагестан","Ингушетия","Кабардино-Балкарская Республика","Карачаево-Черкесская Республика",
        "Республика Северная Осетия — Алания","Чеченская Республика","Ставропольский край"
    ],
    "Приволжский ФО": [
        "Республика Башкортостан","Республика Марий Эл","Республика Мордовия","Республика Татарстан",
        "Удмуртская Республика","Чувашская Республика","Кировская область","Нижегородская область",
        "Оренбургская область","Пензенская область","Пермский край","Самарская область",
        "Саратовская область","Ульяновская область"
    ],
    "Уральский ФО": [
        "Курганская область","Свердловская область","Тюменская область","Челябинская область",
        "Ханты-Мансийский автономный округ","Ямало-Ненецкий автономный округ"
    ],
    "Сибирский ФО": [
        "Республика Алтай","Республика Бурятия","Республика Тыва","Республика Хакасия",
        "Алтайский край","Забайкальский край","Красноярский край","Иркутская область",
        "Кемеровская область","Новосибирская область","Омская область","Томская область"
    ],
    "Дальневосточный ФО": [
        "Республика Саха (Якутия)","Камчатский край","Приморский край","Хабаровский край",
        "Амурская область","Магаданская область","Сахалинская область","Еврейская автономная область",
        "Чукотский автономный округ"
    ]
}

# Доп. группа для несопоставленных регионов
OTHER_GROUP = "Прочие"

# ---------------------------------------------------------------------
# Приложение
# ---------------------------------------------------------------------
class FinTrustHeatmapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinTrustMap - Heatmap by Federal Districts")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')

        self.df = None
        self.excel_file = None

        self.canvas = None
        self.current_fig = None

        self.setup_style()
        self.create_widgets()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

    def create_widgets(self):
        header = tk.Frame(self.root, bg='#0d7377', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="📊 FinTrustMap — Heatmap по ФО", bg='#0d7377', fg='white',
                 font=('Arial', 18, 'bold')).pack(pady=16)

        main = tk.Frame(self.root, bg='#1e1e1e')
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        left = tk.Frame(main, bg='#2d2d2d', width=360)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        left.pack_propagate(False)

        right = tk.Frame(main, bg='#2d2d2d')
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Контролы
        file_section = tk.LabelFrame(left, text="📁 Данные", bg='#2d2d2d', fg='white')
        file_section.pack(fill=tk.X, padx=8, pady=8)

        self.file_label = tk.Label(file_section, text="Файл не выбран", bg='#2d2d2d', fg='#aaa')
        self.file_label.pack(anchor=tk.W, pady=6)

        tk.Button(file_section, text="Выбрать Excel", command=self.load_excel, bg='#0d7377', fg='white').pack(fill=tk.X, pady=6)

        method_section = tk.LabelFrame(left, text="⚙ Метод расчёта", bg='#2d2d2d', fg='white')
        method_section.pack(fill=tk.X, padx=8, pady=8)

        self.method_var = tk.StringVar(value="min_max_normalized")
        tk.Radiobutton(method_section, text="Min-Max нормализация", variable=self.method_var, value="min_max_normalized", bg='#2d2d2d', fg='white', selectcolor='#0d7377').pack(anchor=tk.W, pady=2)
        tk.Radiobutton(method_section, text="Простое среднее", variable=self.method_var, value="simple_average", bg='#2d2d2d', fg='white', selectcolor='#0d7377').pack(anchor=tk.W, pady=2)
        tk.Radiobutton(method_section, text="PCA", variable=self.method_var, value="pca", bg='#2d2d2d', fg='white', selectcolor='#0d7377').pack(anchor=tk.W, pady=2)
        tk.Radiobutton(
            method_section,
            text="Методика ЦБ РФ",
            variable=self.method_var,
            value="cbr_method",
            bg='#2d2d2d',
            fg='white',
            selectcolor='#0d7377'
        ).pack(anchor=tk.W, pady=2) 

        style_section = tk.LabelFrame(left, text="🎨 Стиль", bg='#2d2d2d', fg='white')
        style_section.pack(fill=tk.X, padx=8, pady=8)
        self.colormap_var = tk.StringVar(value="RdYlGn")
        ttk.Combobox(style_section, textvariable=self.colormap_var, values=["RdYlGn","RdYlGn_r","viridis","plasma","coolwarm","Spectral"], state="readonly").pack(fill=tk.X, pady=6)
        self.show_values_var = tk.BooleanVar(value=True)
        tk.Checkbutton(style_section, text="Показывать названия и значения", variable=self.show_values_var, bg='#2d2d2d', fg='white', selectcolor='#0d7377').pack(anchor=tk.W)

        actions = tk.Frame(left, bg='#2d2d2d')
        actions.pack(fill=tk.X, padx=8, pady=(10,8))
        self.btn_calc = tk.Button(actions, text="📊 Рассчитать индекс", command=self.calculate_index, bg='#14b1ab', fg='white', state=tk.DISABLED)
        self.btn_calc.pack(fill=tk.X, pady=6)
        self.btn_show = tk.Button(actions, text="🔥 Показать Heatmap (по ФО)", command=self.create_heatmap, bg='#ff6b35', fg='white', state=tk.DISABLED)
        self.btn_show.pack(fill=tk.X, pady=6)
        # self.btn_show_rf = tk.Button(actions, text="🇷🇺 Показать Heatmap (карта РФ)", command=self.create_heatmap_by_rf, bg='#35aaff', fg='white', state=tk.DISABLED)
        # self.btn_show_rf.pack(fill=tk.X, pady=6)
        self.btn_export = tk.Button(actions, text="💾 Экспорт", command=self.export_results, bg='#323232', fg='white', state=tk.DISABLED)
        self.btn_export.pack(fill=tk.X, pady=6)

        info = tk.LabelFrame(left, text="ℹ Информация", bg='#2d2d2d', fg='white')
        info.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.log_box = tk.Text(info, height=10, bg='#1e1e1e', fg='#00ff00', font=('Courier',9))
        self.log_box.pack(fill=tk.BOTH, expand=True)
        tk.Scrollbar(info, command=self.log_box.yview).pack(side=tk.RIGHT, fill=tk.Y)
        self.log_box.config(yscrollcommand=lambda *args: None)

        # Preview area
        tk.Label(right, text="📈 Предпросмотр Heatmap (по ФО)", bg='#2d2d2d', fg='white', font=('Arial',12,'bold')).pack(pady=10)
        self.preview_frame = tk.Frame(right, bg='#1e1e1e')
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.log("Приложение готово. Загрузите Excel.")

    def log(self, txt):
        t = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{t}] {txt}\n")
        self.log_box.see(tk.END)

    def load_excel(self):
        path = filedialog.askopenfilename(title="Выберите Excel", filetypes=[("Excel","*.xlsx *.xls"),("All","*.*")])
        if not path:
            return
        try:
            self.df = pd.read_excel(path)
            self.excel_file = path
            if 'Регион' not in self.df.columns:
                raise ValueError("В файле обязательно должна быть колонка 'Регион' с точными названиями регионов.")
            numeric = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric) == 0:
                raise ValueError("В файле нет числовых показателей.")
            self.file_label.config(text=f"✓ {os.path.basename(path)}  | Р:{len(self.df)}  П:{len(numeric)}", fg='#00ff00')
            self.btn_calc.config(state=tk.NORMAL)
            self.log(f"Файл загружен: {os.path.basename(path)} (показателей: {len(numeric)})")
            messagebox.showinfo("Успех", "Файл загружен")
        except Exception as e:
            self.log(f"Ошибка загрузки: {e}")
            messagebox.showerror("Ошибка", str(e))

    def calculate_index(self):
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Загрузите файл")
            return
        try:
            method = self.method_var.get()
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) == 0:
                raise ValueError("Нет числовых показателей для расчёта")

            if method == "simple_average":
                # Простое среднее
                self.df['Индекс'] = self.df[numeric_cols].mean(axis=1)

            elif method == "min_max_normalized":
                # Нормализация Min-Max
                normalized = self.df[numeric_cols].copy()
                for c in numeric_cols:
                    mi, ma = normalized[c].min(), normalized[c].max()
                    if ma > mi:
                        normalized[c] = (normalized[c] - mi) / (ma - mi)
                    else:
                        normalized[c] = 0.0
                self.df['Индекс'] = 100 * normalized.mean(axis=1)

            elif method == "pca":
                # PCA
                from sklearn.preprocessing import StandardScaler
                from sklearn.decomposition import PCA
                scaler = StandardScaler()
                scaled = scaler.fit_transform(self.df[numeric_cols])
                pca = PCA(n_components=1)
                idx_raw = pca.fit_transform(scaled).flatten()
                if idx_raw.max() != idx_raw.min():
                    self.df['Индекс'] = 100 * (idx_raw - idx_raw.min()) / (idx_raw.max() - idx_raw.min())
                else:
                    self.df['Индекс'] = 50.0

            elif method == "cbr_method":
                # ---------------- Методика ЦБ РФ ----------------
                normalized = self.df[numeric_cols].copy()
                for c in numeric_cols:
                    mi, ma = normalized[c].min(), normalized[c].max()
                    if ma > mi:
                        normalized[c] = (normalized[c] - mi) / (ma - mi)
                    else:
                        normalized[c] = 0.5  # если все значения одинаковы

                weights = np.ones(len(numeric_cols)) / len(numeric_cols)  # равные веса
                self.df['Индекс'] = normalized.dot(weights) * 100

            else:
                # По умолчанию простое среднее
                self.df['Индекс'] = self.df[numeric_cols].mean(axis=1)

            self.log("Индекс рассчитан")
            self.log(f"Среднее: {self.df['Индекс'].mean():.2f}, Мин: {self.df['Индекс'].min():.2f}, Макс: {self.df['Индекс'].max():.2f}")
            self.btn_show.config(state=tk.NORMAL)
            self.btn_export.config(state=tk.NORMAL)
            messagebox.showinfo("Готово", "Индекс рассчитан")
        except Exception as e:
            self.log(f"Ошибка расчёта: {e}")
            messagebox.showerror("Ошибка", str(e))
            
    def create_heatmap(self):
        """Создание красивого блочного Heatmap по федеральным округам"""

        if self.df is None or 'Индекс' not in self.df.columns:
            messagebox.showwarning("Предупреждение", "Сначала рассчитайте индекс!")
            return

        self.log("Создание Heatmap по федеральным округам...")

        # ----------- Карта соответствия ФО -----------
        federal_districts = {
            "Центральный ФО": [
                "Москва","Московская область","Белгородская область","Брянская область",
                "Владимирская область","Воронежская область","Ивановская область",
                "Калужская область","Костромская область","Курская область",
                "Липецкая область","Орловская область","Рязанская область",
                "Смоленская область","Тамбовская область","Тверская область",
                "Тульская область","Ярославская область"
            ],
            "Северо-Западный ФО": [
                "Санкт-Петербург","Ленинградская область","Республика Карелия",
                "Республика Коми","Архангельская область","Вологодская область",
                "Калининградская область","Мурманская область","Новгородская область",
                "Псковская область"
            ],
            "Южный ФО": [
                "Краснодарский край","Ростовская область","Волгоградская область",
                "Астраханская область","Республика Адыгея","Республика Калмыкия"
            ],
            "Северо-Кавказский ФО": [
                "Республика Дагестан","Ингушетия","Кабардино-Балкария",
                "Карачаево-Черкессия","Северная Осетия-Алания",
                "Чеченская Республика","Ставропольский край"
            ],
            "Приволжский ФО": [
                "Республика Татарстан","Самарская область","Республика Башкортостан",
                "Пермский край","Ульяновская область","Пензенская область",
                "Нижегородская область","Саратовская область","Оренбургская область",
                "Кировская область","Чувашия","Марий Эл","Мордовия","Удмуртия"
            ],
            "Уральский ФО": [
                "Свердловская область","Челябинская область",
                "Тюменская область","Курганская область",
                "ХМАО","ЯНАО"
            ],
            "Сибирский ФО": [
                "Красноярский край","Новосибирская область","Томская область",
                "Кемеровская область","Алтайский край","Республика Алтай",
                "Республика Тыва","Республика Хакасия","Забайкальский край",
                "Иркутская область"
            ],
            "Дальневосточный ФО": [
                "Республика Саха (Якутия)","Приморский край","Хабаровский край",
                "Амурская область","Сахалинская область","Магаданская область",
                "Камчатский край","Чукотский АО","ЕАО"
            ]
        }

        # ----------- Подготовка данных -----------
        df = self.df.copy().set_index("Регион")

        # Цветовая схема
        cmap = plt.get_cmap(self.colormap_var.get())

        # Нормализация индекса в интервал [0,1]
        values = df["Индекс"]
        norm = (values - values.min()) / (values.max() - values.max())

        # ----------- Настройка Figure -----------
        fig_h = 12
        fig_w = 18

        fig = plt.figure(figsize=(fig_w, fig_h), facecolor="#1e1e1e")
        gs = fig.add_gridspec(4, 2, wspace=0.25, hspace=0.35)

        district_positions = list(federal_districts.keys())
        pos_idx = 0

        # ----------- Рисуем каждый округ -----------
        for r in range(4):
            for c in range(2):
                if pos_idx >= len(district_positions):
                    break

                district = district_positions[pos_idx]
                regions = federal_districts[district]

                # Фильтруем только те регионы, которые реально есть в данных
                real_regions = [r for r in regions if r in df.index]

                ax = fig.add_subplot(gs[r, c])
                ax.set_facecolor("#1e1e1e")
                ax.set_title(
                    district,
                    fontsize=14, color="white", pad=10
                )

                if len(real_regions) == 0:
                    ax.text(0.5, 0.5, "Нет данных", color="gray",
                            ha="center", va="center", fontsize=12)
                    ax.axis("off")
                    pos_idx += 1
                    continue

                # Формируем таблицу NxM
                n = len(real_regions)
                cols = int(np.ceil(np.sqrt(n)))
                rows = int(np.ceil(n / cols))

                grid = np.zeros((rows, cols))
                labels = [["" for _ in range(cols)] for __ in range(rows)]

                for i, region in enumerate(real_regions):
                    r0 = i // cols
                    c0 = i % cols
                    val = df.loc[region, "Индекс"]
                    norm_val = (val - values.min()) / (values.max() - values.min())

                    grid[r0, c0] = norm_val
                    labels[r0][c0] = f"{region}\n{val:.1f}"

                sns.heatmap(
                    grid,
                    cmap=self.colormap_var.get(),
                    ax=ax,
                    cbar=False,
                    annot=labels if self.show_values_var.get() else False,
                    fmt="",
                    linewidths=1.5,
                    linecolor="#1e1e1e",
                    annot_kws={"color": "black", "size": 8}
                )

                ax.set_xticks([])
                ax.set_yticks([])
                pos_idx += 1

        # ----------- Вывод в Tkinter -----------
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.preview_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.log("✓ Красивый Heatmap создан!")


    def export_results(self):
        if self.df is None or 'Индекс' not in self.df.columns:
            messagebox.showwarning("Предупреждение", "Нечего экспортировать")
            return
        try:
            fname = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")])
            if not fname:
                return
            out = self.df.sort_values('Индекс', ascending=False).reset_index(drop=True)
            out.index = out.index + 1
            out.index.name = 'Ранг'
            out.to_excel(fname)
            self.log(f"Экспортировано: {os.path.basename(fname)}")
            messagebox.showinfo("Успех", "Экспорт завершён")
        except Exception as e:
            self.log(f"Ошибка экспорта: {e}")
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FinTrustHeatmapApp(root)
    root.update_idletasks()
    width, height = 1200, 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.mainloop()
