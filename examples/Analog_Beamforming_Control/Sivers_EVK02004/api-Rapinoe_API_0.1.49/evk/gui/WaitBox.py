import tkinter as tk

class WaitBox(object):

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def show_waitbox(self, fixed_x=None, fixed_y=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_pointerx() + 100
        y = y + cy + self.widget.winfo_pointery() +100
        self.tipwindow = tw = tk.Toplevel(self.widget)
        if fixed_x!=None and fixed_y!=None:
            x = fixed_x
            y = fixed_y
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)
        label.focus()

    def hide_waitbox(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()