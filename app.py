import customtkinter as ctk
import datetime
from tkinter import messagebox
from tkcalendar import Calendar
import colorsys
from database import init_db, add_task, get_all_tasks, get_tasks_by_date_range, update_task_status, delete_task, add_session, get_sessions_by_date_range, delete_session, add_class, get_all_classes, delete_class

# Initialize CustomTkinter settings for a modern flat UI
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Theme settings
BG_COLOR = "#0F172A"      # Slate 900
SURFACE_COLOR = "#1E293B" # Slate 800
SURFACE_LIGHT = "#334155" # Slate 700
ACCENT_GREEN = "#10B981"  # Emerald 500
ACCENT_RED = "#EF4444"    # Red 500
ACCENT_ORANGE = "#F59E0B" # Amber 500
ACCENT_BLUE = "#3B82F6"   # Blue 500
TEXT_MAIN = "#F8FAFC"     # Slate 50
TEXT_MUTED = "#94A3B8"    # Slate 400

def get_color_from_id(task_id):
    # Generates a pseudo-random beautiful color based on the task_id
    golden_ratio_conjugate = 0.618033988749895
    h = (task_id * golden_ratio_conjugate) % 1.0
    s = 0.65
    v = 0.55 if ctk.get_appearance_mode() == "Dark" else 0.8
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

class CalendarModal(ctk.CTkToplevel):
    def __init__(self, parent, entry_widget):
        super().__init__(parent)
        self.title("Seleccionar Fecha")
        self.geometry("300x320")
        self.entry_widget = entry_widget
        self.configure(fg_color=BG_COLOR)
        
        self.cal = Calendar(self, selectmode='day', date_pattern='y-mm-dd',
                            background=SURFACE_COLOR, foreground=TEXT_MAIN,
                            headersbackground=BG_COLOR, headersforeground=TEXT_MUTED)
        self.cal.pack(pady=15, padx=15, fill="both", expand=True)
        
        self.btn = ctk.CTkButton(self, text="Aceptar", command=self.set_date, 
                                 fg_color=ACCENT_GREEN, hover_color="#059669")
        self.btn.pack(pady=10)
        
        self.transient(parent)
        self.grab_set()
        
    def set_date(self):
        self.entry_widget.configure(state="normal")
        self.entry_widget.delete(0, "end")
        self.entry_widget.insert(0, self.cal.get_date())
        self.entry_widget.configure(state="readonly")
        self.destroy()

class AddTaskWindow(ctk.CTkToplevel):
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.title("Añadir Nueva Tarea")
        self.geometry("450x420")
        self.configure(fg_color=BG_COLOR)
        self.refresh_callback = refresh_callback
        
        self.transient(parent)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Crear Nueva Tarea", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_MAIN)
        self.label.pack(pady=(25, 15))

        self.title_entry = ctk.CTkEntry(self, placeholder_text="Título de la tarea...", width=340, height=40, font=ctk.CTkFont(size=14))
        self.title_entry.pack(pady=10)

        self.desc_entry = ctk.CTkTextbox(self, width=340, height=100, font=ctk.CTkFont(size=13))
        self.desc_entry.insert("0.0", "Añade una descripción aquí (opcional)")
        self.desc_entry.pack(pady=10)

        # Date Frame
        self.date_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.date_frame.pack(pady=15)
        
        self.date_entry = ctk.CTkEntry(self.date_frame, placeholder_text="Seleccione Fecha Límite", width=280, height=40, state="readonly", font=ctk.CTkFont(size=14))
        self.date_entry.grid(row=0, column=0, padx=(0,10))
        
        self.cal_btn = ctk.CTkButton(self.date_frame, text="📅", width=50, height=40, command=self.open_calendar, fg_color=SURFACE_COLOR, hover_color=SURFACE_LIGHT)
        self.cal_btn.grid(row=0, column=1)

        self.save_btn = ctk.CTkButton(self, text="Guardar Tarea", height=45, width=200, command=self.save_task, 
                                      fg_color=ACCENT_GREEN, hover_color="#059669", font=ctk.CTkFont(size=16, weight="bold"))
        self.save_btn.pack(pady=25)

    def open_calendar(self):
        CalendarModal(self, self.date_entry)

    def save_task(self):
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get("0.0", "end").strip()
        if desc == "Añade una descripción aquí (opcional)":
            desc = ""
        due_date = self.date_entry.get().strip()
        
        if not title or not due_date:
            messagebox.showerror("Campos Incompletos", "Por favor, ingresa el título y selecciona una fecha límite.")
            return

        add_task(title, desc, due_date)
        self.refresh_callback()
        self.destroy()

class AddSessionWindow(ctk.CTkToplevel):
    def __init__(self, parent, target_date_str, refresh_callback):
        super().__init__(parent)
        self.title(f"Agendar Bloque de Tiempo - {target_date_str}")
        self.geometry("450x380")
        self.configure(fg_color=BG_COLOR)
        self.refresh_callback = refresh_callback
        self.target_date_str = target_date_str
        
        self.transient(parent)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Agendar en " + target_date_str, font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_MAIN)
        self.label.pack(pady=(20, 15))

        # Fetch Tasks
        self.tasks = get_all_tasks()
        self.pending_tasks = [t for t in self.tasks if t['status'] == 'pending']
        
        if not self.pending_tasks:
            lbl = ctk.CTkLabel(self, text="No hay tareas pendientes para agendar.", text_color=ACCENT_RED)
            lbl.pack(pady=20)
            return

        self.task_choices = {f"{t['id']} - {t['title']} (Vence: {t['due_date']})": t['id'] for t in self.pending_tasks}
        
        self.task_combo = ctk.CTkComboBox(self, values=list(self.task_choices.keys()), width=340, height=40, font=ctk.CTkFont(size=14))
        self.task_combo.pack(pady=10)

        # Time Selection
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(pady=15)

        hours = [f"{h:02d}:00" for h in range(6, 24)] + [f"{h:02d}:30" for h in range(6, 23)]
        hours.sort()

        ctk.CTkLabel(time_frame, text="Inicio:").grid(row=0, column=0, padx=5)
        self.start_combo = ctk.CTkComboBox(time_frame, values=hours, width=100)
        self.start_combo.set("08:00")
        self.start_combo.grid(row=0, column=1, padx=(0, 20))

        ctk.CTkLabel(time_frame, text="Fin:").grid(row=0, column=2, padx=5)
        self.end_combo = ctk.CTkComboBox(time_frame, values=hours, width=100)
        self.end_combo.set("09:00")
        self.end_combo.grid(row=0, column=3)

        self.save_btn = ctk.CTkButton(self, text="Guardar Bloque", height=45, command=self.save_session, 
                                      fg_color=ACCENT_BLUE, hover_color="#2563EB", font=ctk.CTkFont(size=16, weight="bold"))
        self.save_btn.pack(pady=30)

    def save_session(self):
        task_str = self.task_combo.get()
        start = self.start_combo.get()
        end = self.end_combo.get()

        if task_str not in self.task_choices:
            messagebox.showerror("Error", "Selecciona una tarea válida.")
            return
        
        if start >= end:
            messagebox.showerror("Error", "La hora de fin debe ser mayor a la hora de inicio.")
            return

        # OVERLAP CHECKING
        existing = get_sessions_by_date_range(self.target_date_str, self.target_date_str)
        t_start = datetime.datetime.strptime(start, "%H:%M")
        t_end = datetime.datetime.strptime(end, "%H:%M")

        for sess in existing:
            s_start = datetime.datetime.strptime(sess['start_time'], "%H:%M")
            s_end = datetime.datetime.strptime(sess['end_time'], "%H:%M")
            # Overlap condition: (New Start < Existing End) AND (New End > Existing Start)
            if t_start < s_end and t_end > s_start:
                messagebox.showerror("Solapamiento de Horario", f"Este bloque choca con la tarea:\n\n'{sess['title']}'\n({sess['start_time']} - {sess['end_time']})")
                return

        # Check overlapping with classes
        target_weekday = datetime.datetime.strptime(self.target_date_str, "%Y-%m-%d").weekday()
        all_classes = get_all_classes()
        day_classes = [c for c in all_classes if c['day_of_week'] == target_weekday]
        
        for c in day_classes:
            c_start = datetime.datetime.strptime(c['start_time'], "%H:%M")
            c_end = datetime.datetime.strptime(c['end_time'], "%H:%M")
            if t_start < c_end and t_end > c_start:
                messagebox.showerror("Solapamiento de Horario", f"Este bloque de estudio choca con tu clase:\n\n'{c['name']}'\n({c['start_time']} - {c['end_time']})")
                return

        task_id = self.task_choices[task_str]
        add_session(task_id, self.target_date_str, start, end)
        self.refresh_callback()
        self.destroy()

class AddClassWindow(ctk.CTkToplevel):
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.title("Añadir Horario de Clase")
        self.geometry("450x420")
        self.configure(fg_color=BG_COLOR)
        self.refresh_callback = refresh_callback
        
        self.transient(parent)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Nueva Clase Universitaria", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_MAIN)
        self.label.pack(pady=(20, 15))

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Nombre de la asignatura...", width=340, height=40, font=ctk.CTkFont(size=14))
        self.name_entry.pack(pady=10)

        self.days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        self.days_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.days_frame.pack(pady=5)
        
        self.day_vars = []
        for i, day in enumerate(self.days):
            var = ctk.BooleanVar(value=False)
            self.day_vars.append((day, var))
            cb = ctk.CTkCheckBox(self.days_frame, text=day[:3], variable=var, width=50)
            cb.grid(row=0, column=i, padx=2)

        # Time Selection
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(pady=15)

        hours = [f"{h:02d}:00" for h in range(6, 24)] + [f"{h:02d}:30" for h in range(6, 23)]
        hours.sort()

        ctk.CTkLabel(time_frame, text="Inicio:").grid(row=0, column=0, padx=5)
        self.start_combo = ctk.CTkComboBox(time_frame, values=hours, width=100)
        self.start_combo.set("08:00")
        self.start_combo.grid(row=0, column=1, padx=(0, 20))

        ctk.CTkLabel(time_frame, text="Fin:").grid(row=0, column=2, padx=5)
        self.end_combo = ctk.CTkComboBox(time_frame, values=hours, width=100)
        self.end_combo.set("10:00")
        self.end_combo.grid(row=0, column=3)

        self.save_btn = ctk.CTkButton(self, text="Guardar Clase", height=45, command=self.save_class, 
                                      fg_color="#8B5CF6", hover_color="#7C3AED", font=ctk.CTkFont(size=16, weight="bold")) # Purple color
        self.save_btn.pack(pady=30)

    def save_class(self):
        name = self.name_entry.get().strip()
        start = self.start_combo.get()
        end = self.end_combo.get()

        selected_days = [day for day, var in self.day_vars if var.get()]

        if not name:
            messagebox.showerror("Error", "El nombre de la asignatura es obligatorio.")
            return
            
        if not selected_days:
            messagebox.showerror("Error", "Debes seleccionar al menos un día para la clase.")
            return

        if start >= end:
            messagebox.showerror("Error", "La hora de fin debe ser mayor a la hora de inicio.")
            return

        all_existing_classes = get_all_classes()
        t_start = datetime.datetime.strptime(start, "%H:%M")
        t_end = datetime.datetime.strptime(end, "%H:%M")

        # Validate for all selected days before saving any
        for day_str in selected_days:
            day_idx = self.days.index(day_str)
            existing_for_day = [c for c in all_existing_classes if c['day_of_week'] == day_idx]
            
            for c in existing_for_day:
                s_start = datetime.datetime.strptime(c['start_time'], "%H:%M")
                s_end = datetime.datetime.strptime(c['end_time'], "%H:%M")
                if t_start < s_end and t_end > s_start:
                    messagebox.showerror("Solapamiento de Horario", f"En el {day_str}, este horario cruza con otra clase:\n\n'{c['name']}'\n({c['start_time']} - {c['end_time']})")
                    return

        # Save a class record for each selected day
        for day_str in selected_days:
            day_idx = self.days.index(day_str)
            add_class(name, day_idx, start, end)
            
        self.refresh_callback()
        self.destroy()

class TaskItemFrame(ctk.CTkFrame):
    def __init__(self, master, task, refresh_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.task = task
        self.refresh_callback = refresh_callback
        
        self.configure(fg_color=SURFACE_COLOR, corner_radius=12)

        today = datetime.date.today()
        task_date = datetime.datetime.strptime(task['due_date'], "%Y-%m-%d").date()
        diff_days = (task_date - today).days

        if task['status'] == 'completed':
            priority = "Completada"
            p_color = TEXT_MUTED
            border_col = SURFACE_COLOR
        elif diff_days < 0:
            priority = "Atrasada!"
            p_color = ACCENT_RED
            border_col = ACCENT_RED
        elif diff_days <= 3:
            priority = "¡Urgente! Alta Prioridad"
            p_color = ACCENT_RED
            border_col = ACCENT_RED
        elif diff_days <= 7:
            priority = "Media Prioridad"
            p_color = ACCENT_ORANGE
            border_col = ACCENT_ORANGE
        else:
            priority = "Baja Prioridad"
            p_color = ACCENT_GREEN
            border_col = ACCENT_GREEN

        if task['status'] == 'pending':
            self.configure(border_width=2, border_color=border_col)

        self.grid_columnconfigure(0, weight=1)

        title_font = ctk.CTkFont(size=16, weight="bold")
        status_icon = "✔️" if task['status'] == 'completed' else "⏳"
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        title_str = f"{status_icon} {task['title']}"
        self.title_label = ctk.CTkLabel(self.header_frame, text=title_str, font=title_font, text_color=TEXT_MAIN if task['status'] == 'pending' else TEXT_MUTED)
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.prio_label = ctk.CTkLabel(self.header_frame, text=priority, font=ctk.CTkFont(size=12, weight="bold"), text_color=p_color)
        self.prio_label.grid(row=0, column=1, sticky="e")

        date_str = f"📅 Fecha Límite: {task['due_date']} ({diff_days} días)" if task['status'] == 'pending' else f"📅 Fecha: {task['due_date']}"
        self.date_label = ctk.CTkLabel(self, text=date_str, font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.date_label.grid(row=1, column=0, padx=15, pady=(0, 5), sticky="w")
        
        if task['description']:
            self.desc_label = ctk.CTkLabel(self, text=task['description'], anchor="w", text_color=TEXT_MUTED, font=ctk.CTkFont(size=13), justify="left")
            self.desc_label.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=0, column=1, rowspan=3, padx=15, pady=15, sticky="e")

        if task['status'] == 'pending':
            self.complete_btn = ctk.CTkButton(self.btn_frame, text="Finalizar", width=80, height=30, fg_color=ACCENT_GREEN, hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=self.mark_completed)
            self.complete_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.delete_btn = ctk.CTkButton(self.btn_frame, text="Borrar", width=80, height=30, fg_color=ACCENT_RED, hover_color="#B91C1C", font=ctk.CTkFont(weight="bold"), command=self.delete_this_task)
        self.delete_btn.grid(row=0, column=1)

    def mark_completed(self):
        update_task_status(self.task['id'], 'completed')
        self.refresh_callback()

    def delete_this_task(self):
        if messagebox.askyesno("Confirmar Acción", "¿Estás seguro de que deseas eliminar permanentemente esta tarea?"):
            delete_task(self.task['id'])
            self.refresh_callback()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MyUniTasks - Organizador")
        self.geometry("1100x750")
        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        init_db()

        self.create_sidebar()
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        self.view_title = ctk.CTkLabel(self.main_container, text="", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_MAIN)
        self.view_title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        self.current_view = "all"
        
        # Cache frames for quick switching instead of recreating the whole structure
        self.cached_views = {}
        
        self.switch_view("all")

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SURFACE_COLOR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="📌 MyUniTasks", font=ctk.CTkFont(size=26, weight="bold"), text_color=TEXT_MAIN)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        btn_font = ctk.CTkFont(size=14, weight="bold")
        btn_kwargs = {"fg_color": "transparent", "text_color": TEXT_MUTED, "hover_color": SURFACE_LIGHT, "anchor": "w", "font": btn_font, "height": 40}

        self.all_tasks_btn = ctk.CTkButton(self.sidebar_frame, text="📋 Tablero de Tareas", command=lambda: self.switch_view("all"), **btn_kwargs)
        self.all_tasks_btn.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.calendar_btn = ctk.CTkButton(self.sidebar_frame, text="🗓️ Calendario (7 Días)", command=lambda: self.switch_view("calendar"), **btn_kwargs)
        self.calendar_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.add_task_btn = ctk.CTkButton(self.sidebar_frame, text="+ Nueva Tarea", command=self.open_add_task_window, 
                                          fg_color=ACCENT_GREEN, hover_color="#059669", font=ctk.CTkFont(size=15, weight="bold"), height=45)
        self.add_task_btn.grid(row=4, column=0, padx=20, pady=(40, 5), sticky="ew")
        
        self.add_class_btn = ctk.CTkButton(self.sidebar_frame, text="+ Añadir Clase", command=self.open_add_class_window, 
                                          fg_color="#8B5CF6", hover_color="#7C3AED", font=ctk.CTkFont(size=15, weight="bold"), height=45)
        self.add_class_btn.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"],
                                                                       command=self.change_appearance_mode_event,
                                                                       fg_color=BG_COLOR, button_color=BG_COLOR)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="s")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def switch_view(self, view_name):
        self.current_view = view_name
        self.all_tasks_btn.configure(text_color=TEXT_MUTED)
        self.calendar_btn.configure(text_color=TEXT_MUTED)

        # Hide all cached views first without destroying them
        for frame in self.cached_views.values():
            frame.grid_remove()

        if view_name == "all":
            self.view_title.configure(text="Tablero General")
            self.all_tasks_btn.configure(text_color=TEXT_MAIN)
            self.load_list_view()
        elif view_name == "calendar":
            self.view_title.configure(text="Mi Agenda para la Semana")
            self.calendar_btn.configure(text_color=TEXT_MAIN)
            self.load_calendar_view()

    def refresh_current_view(self):
        # Force redraw of data only
        if self.current_view in self.cached_views:
            for widget in self.cached_views[self.current_view].winfo_children():
                widget.destroy()
        self.switch_view(self.current_view)

    def sort_tasks_by_custom_priority(self, tasks):
        def sorting_key(task):
            is_completed = 1 if task['status'] == 'completed' else 0
            task_date = datetime.datetime.strptime(task['due_date'], "%Y-%m-%d").date()
            return (is_completed, task_date)
            
        return sorted(tasks, key=sorting_key)

    def load_list_view(self):
        if "all" not in self.cached_views:
            self.cached_views["all"] = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        
        view_content = self.cached_views["all"]
        view_content.grid(row=1, column=0, sticky="nsew")
        
        # Clear previous items so they don't duplicate on re-visit
        for widget in view_content.winfo_children():
            widget.destroy()
        
        tasks = self.sort_tasks_by_custom_priority(get_all_tasks())

        if not tasks:
            ctk.CTkLabel(view_content, text="No hay tareas programadas.", text_color=TEXT_MUTED, font=ctk.CTkFont(size=16, slant="italic")).pack(pady=60)
            return

        for task in tasks:
            task_frame = TaskItemFrame(view_content, task, self.refresh_current_view)
            task_frame.pack(fill="x", pady=10, padx=5)

    def load_calendar_view(self):
        # Master View Frame Cached
        if "calendar" not in self.cached_views:
            self.cached_views["calendar"] = ctk.CTkFrame(self.main_container, fg_color="transparent")
            
        view_content = self.cached_views["calendar"]
        view_content.grid(row=1, column=0, sticky="nsew")
        
        # Clear previous calendar headers and grid so they don't duplicate
        for widget in view_content.winfo_children():
            widget.destroy()

        today = datetime.date.today()
        end_date = today + datetime.timedelta(days=6)
        sessions = get_sessions_by_date_range(today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        all_classes = get_all_classes()

        # 1. TOP STICKY HEADER
        # This will hold the day labels and "add" buttons
        header_frame = ctk.CTkFrame(view_content, fg_color="transparent")
        # Added right padding of 20 to account for the CustomTkinter scrollbar in the list below.
        # This prevents the headers from shifting right relative to the body content.
        header_frame.pack(fill="x", pady=(0, 10), padx=(0, 20))
        
        # Spacer on the left for the timeline text (Width 45 + 5 left padx = 50px total)
        ctk.CTkFrame(header_frame, width=45, height=0, fg_color="transparent").pack(side="left", padx=(5, 0))

        # 2. BODY SCROLLABLE FRAME
        # A single vertical scrolling canvas for perfect sync
        scroll_body = ctk.CTkScrollableFrame(view_content, fg_color="transparent", orientation="vertical")
        scroll_body.pack(fill="both", expand=True)

        grid_frame = ctk.CTkFrame(scroll_body, fg_color="transparent")
        grid_frame.pack(fill="x", expand=True)

        PIXELS = 85
        START = 6
        TOTAL = 18
        
        # Timeline Sidebar (Inside the single body)
        timeline_bar = ctk.CTkFrame(grid_frame, fg_color="transparent", width=45, height=TOTAL*PIXELS)
        timeline_bar.pack(side="left", fill="y", pady=0, padx=(5, 0))
        timeline_bar.pack_propagate(False)

        for hour in range(TOTAL + 1):
            y_pos = hour * PIXELS
            real_h = START + hour
            if real_h <= 23:
                lbl = ctk.CTkLabel(timeline_bar, text=f"{real_h:02d}:00", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED)
                lbl.place(x=0, y=y_pos - 10)

        week_day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        # Background Master Canvas for Everything (Grid, Classes, Sessions)
        # This brings a colossal performance improvement by avoiding thousands of widget instantiations
        self.bg_canvas = ctk.CTkCanvas(grid_frame, bg=SURFACE_COLOR, highlightthickness=0)
        self.bg_canvas.pack(side="left", fill="both", expand=True, padx=5)
        
        # Bind the configure event to redraw lines when resized
        def redraw_grid(event):
            self.bg_canvas.delete("grid_line")
            width = event.width
            height = self.bg_canvas.winfo_height()
            
            # Horizontal lines
            for hour in range(TOTAL + 1):
                y_pos = hour * PIXELS
                self.bg_canvas.create_line(0, y_pos, width, y_pos, fill=SURFACE_LIGHT, tags="grid_line")
                
            # Vertical lines (7 columns means 6 inner lines)
            col_width = width / 7
            for day in range(1, 7):
                x_pos = day * col_width
                self.bg_canvas.create_line(x_pos, 0, x_pos, height, fill=SURFACE_LIGHT, tags="grid_line")
                
        # We need to compute total items and their placement natively
        def draw_calendar_native(event=None):
            self.bg_canvas.delete("block_shape") # Delete all blocks and texts
            width = self.bg_canvas.winfo_width()
            # If width is too small, geometry isn't ready. Abort drawing.
            if width < 50: return
            
            col_width = width / 7
            
            # Dictionary linking rectangle IDs to their data for deletion events
            self.canvas_item_data = {}
            
            def on_canvas_click(e):
                item_id = self.bg_canvas.find_withtag("current")
                if item_id:
                    data = self.canvas_item_data.get(item_id[0])
                    if data:
                        # Direct check if they clicked the 'close' element
                        if data.get('is_close', False):
                            if data['type'] == 'class':
                                if messagebox.askyesno("Confirmar", "¿Deseas eliminar esta clase de tu horario universitario?"):
                                    delete_class(data['id'])
                                    self.refresh_current_view()
                            elif data['type'] == 'session':
                                delete_session(data['id'])
                                self.refresh_current_view()
            
            self.bg_canvas.bind("<Button-1>", on_canvas_click)

            # Click on empty space to add a session
            def on_empty_click(e):
                item_id = self.bg_canvas.find_withtag("current")
                # Only trigger if there's nothing under the cursor
                if not item_id or item_id[0] not in self.canvas_item_data:
                    current_col_width = self.bg_canvas.winfo_width() / 7
                    col_idx = int(e.x / current_col_width)
                    col_idx = max(0, min(6, col_idx))
                    clicked_day = today + datetime.timedelta(days=col_idx)
                    date_str = clicked_day.strftime("%Y-%m-%d")
                    # Compute approximate time from y position
                    hour_float = START + (e.y / PIXELS)
                    hour = int(hour_float)
                    minute = 30 if (hour_float - hour) >= 0.5 else 0
                    hour = max(START, min(23, hour))
                    AddSessionWindow(self.winfo_toplevel(), date_str, self.refresh_current_view)
            
            self.bg_canvas.bind("<Button-1>", on_empty_click, add="+")

            # Helper to draw a block natively
            def draw_block(col_idx, y_start, y_end, title, bg_color, fg_color, item_type, db_id):
                x_start = (col_idx * col_width)
                x_end = ((col_idx + 1) * col_width)
                
                if y_end - y_start < 30: y_end = y_start + 30
                
                # Draw rounded rectangle effect via native polygon (simplified to rectangle for speed)
                # Keep blocks exactly 4px away from grid borders for visual separation
                rect_id = self.bg_canvas.create_rectangle(x_start+4, y_start+2, x_end-4, y_end-2, fill=bg_color, outline="", tags="block_shape")
                
                self.canvas_item_data[rect_id] = {'type': item_type, 'id': db_id}
                
                # Title - max width ensures it doesn't spill over or crush
                max_txt_w = max(10, x_end - x_start - 24)
                text_id = self.bg_canvas.create_text(x_start + 8, y_start + 6, text=title, anchor="nw", fill=fg_color, font=("Arial", 9, "bold"), width=max_txt_w, tags="block_shape")
                # Pass clicks on text down to the rectangle logic
                self.canvas_item_data[text_id] = {'type': item_type, 'id': db_id}
                
                # Close "X" button proxy
                close_id = self.bg_canvas.create_text(x_end - 8, y_start + 6, text="✖", anchor="ne", fill=fg_color, font=("Arial", 10, "bold"), tags="block_shape")
                self.canvas_item_data[close_id] = {'type': item_type, 'id': db_id, 'is_close': True}
                
            # 2. Draw all blocks column by column
            for i in range(7):
                current_day = today + datetime.timedelta(days=i)
                date_str = current_day.strftime("%Y-%m-%d")
                
                # Classes
                day_classes = [c for c in all_classes if c['day_of_week'] == current_day.weekday()]
                for c in day_classes:
                    s_h, s_m = map(int, c['start_time'].split(':'))
                    e_h, e_m = map(int, c['end_time'].split(':'))
                    y1 = max(0, ((s_h - START) + (s_m/60.0)) * PIXELS)
                    y2 = ((e_h - START) + (e_m/60.0)) * PIXELS
                    t = f"{c['start_time']} - {c['end_time']}\n🎓 {c['name']}"
                    draw_block(i, y1, y2, t, "#8B5CF6", TEXT_MAIN, 'class', c['id'])
                    
                # Sessions
                day_sessions = [s for s in sessions if s['session_date'] == date_str]
                for s in day_sessions:
                    s_h, s_m = map(int, s['start_time'].split(':'))
                    e_h, e_m = map(int, s['end_time'].split(':'))
                    y1 = max(0, ((s_h - START) + (s_m/60.0)) * PIXELS)
                    y2 = ((e_h - START) + (e_m/60.0)) * PIXELS
                    t = f"{s['start_time']} - {s['end_time']}\n{s['title']}"
                    bg = SURFACE_LIGHT if s['status'] == 'completed' else get_color_from_id(s['task_id'])
                    fg = TEXT_MAIN if s['status'] == 'pending' else TEXT_MUTED
                    draw_block(i, y1, y2, t, bg, fg, 'session', s['session_id'])
                    
        # Draw layout initially with a small delay to ensure window geometry is populated
        self.bg_canvas.after(50, draw_calendar_native)
        self.bg_canvas.bind("<Configure>", redraw_grid)
        self.bg_canvas.bind("<Configure>", draw_calendar_native, add="+")
        
        # 3. Generating Header for each Day (Columns are now drawn natively by the canvas)
        for i in range(7):
            current_day = today + datetime.timedelta(days=i)
            date_str = current_day.strftime("%Y-%m-%d")
            
            # --- HEADER COMPONENT ---
            hdr_col = ctk.CTkFrame(header_frame, fg_color=SURFACE_COLOR, corner_radius=8, width=50, height=85)
            hdr_col.pack_propagate(False)
            hdr_col.pack(side="left", fill="both", expand=True, padx=5)
            
            is_today = current_day == datetime.date.today()
            h_color = ACCENT_BLUE if is_today else TEXT_MAIN
            
            header_text = f"{week_day_names[current_day.weekday()]} {current_day.day}"
            ctk.CTkLabel(hdr_col, text=header_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=h_color).pack(pady=(8, 0))
            ctk.CTkLabel(hdr_col, text=date_str, text_color=TEXT_MUTED, font=ctk.CTkFont(size=11)).pack(pady=(0, 2))
            
            def create_callback(d):
                return lambda: AddSessionWindow(self.winfo_toplevel(), d, self.refresh_current_view)
                
            btn = ctk.CTkButton(hdr_col, text="+ Agendar", width=90, height=24, fg_color=SURFACE_LIGHT, command=create_callback(date_str))
            btn.pack(pady=4)

        # Add total height for scroll bar
        self.bg_canvas.configure(height=TOTAL*PIXELS)

    def open_add_task_window(self):
        AddTaskWindow(self, self.refresh_current_view)
        
    def open_add_class_window(self):
        AddClassWindow(self, self.refresh_current_view)

if __name__ == "__main__":
    app = App()
    app.mainloop()
