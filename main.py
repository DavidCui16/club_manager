import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from database import init_db
from ui.member_ui import MemberUI
from ui.event_ui import EventUI
from ui.finance_ui import FinanceUI


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("社团管理系统")
        self.geometry("1000x650")

        notebook = ttk.Notebook(self, bootstyle=PRIMARY)

        self.member_ui = MemberUI(notebook)
        self.event_ui = EventUI(notebook)
        self.finance_ui = FinanceUI(notebook)

        notebook.add(self.member_ui, text="  成员管理  ")
        notebook.add(self.event_ui, text="  活动管理  ")
        notebook.add(self.finance_ui, text="  财务管理  ")

        notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)


if __name__ == "__main__":
    from sys import platform
    init_db()
    app = App()
    app.mainloop()
