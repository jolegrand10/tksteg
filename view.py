import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image
from PIL.Image import Resampling
from PIL.ImageTk import PhotoImage
import logging
import time
import threading


class Worker:
    def __init__(self, model, win, msg):
        self.model = model
        self.win = win
        self.message = tk.Label(text=f"{msg}... please wait !")
        self.message.pack()
        self.message.place(x=self.win.winfo_width() // 2, y=self.win.winfo_height() // 2 - 30, anchor="center")
        self.pb = ttk.Progressbar(self.win,
                                  orient='horizontal',
                                  mode='indeterminate',
                                  length=300)
        self.pb.pack()
        self.pb.place(x=self.win.winfo_width() // 2, y=self.win.winfo_height() // 2, anchor="center")
        self.pb.start()
        self.finished = False

    def run(self):
        raise NotImplementedError

    def start(self):
        self.th = threading.Thread(target=self.run)
        self.th.start()

    def finish(self):
        self.finished = True
        self.pb.stop()
        self.pb.destroy()
        self.message.destroy()


class DecodingWorker(Worker):
    def __init__(self, model, win):
        super().__init__(model, win, "Decoding")

    def run(self):
        try:
            self.model.decode()
        except UnicodeError:
            raise UnicodeError
        finally:
            self.finish()


class EncodingWorker(Worker):
    def __init__(self, model, win):
        super().__init__(model, win, "Encoding")

    def run(self):
        self.model.encode()
        self.finish()


class ReadImageWorker(Worker):
    def __init__(self, model, win, view):
        self.view = view
        super().__init__(model, win, "Reading image")

    def run(self):
        def fit_size(pic):
            w, h = pic.width, pic.height
            ratiow = w / View.WIDTH
            ratioh = h / View.HEIGHT
            ratio = max(ratiow, ratioh)
            return int(w / ratio), int(h / ratio)

        #
        # read it for the view - requires a TkImage
        #
        self.view.img = Image.open(self.view.picpath)
        resized_image = self.view.img.resize(fit_size(self.view.img), Resampling.LANCZOS)
        self.view.pic = PhotoImage(resized_image)
        self.view.canvas.create_image(0, 0, anchor=tk.NW, image=self.view.pic)
        #
        # update the model (model needs a cv2 image)
        #
        self.model.read_image(self.view.picpath)
        self.finish()


class View:
    WIDTH = 800
    HEIGHT = 600
    INPICFILES = (('image files', '.jpg .png .bmp'),)
    OUTPICFILES = (('image files', '.jpg .png .bmp'),)
    TXTFILES = (('text files', '*.txt'),)

    def __init__(self, controller, model):
        self.controller = controller
        self.model = model
        self.root = tk.Tk()
        self.root.geometry(f"{View.WIDTH}x{View.HEIGHT}")
        self.make_widgets()
        self.showpic = True
        self.txtpath = None
        self.picpath = None
        self.pic = None

    def make_menus(self):
        # menu bar
        self.menu_bar = tk.Menu(self.root, tearoff=0)
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        # Open command
        self.file_menu.add_command(label="Open", command=self.cmd_open, accelerator="Ctrl+O")
        # Save command
        self.file_menu.add_command(label="Save", command=self.cmd_save, accelerator="Ctrl+S")
        # Save as command
        self.file_menu.add_command(label="Save as...", command=self.cmd_saveas)
        # Close command
        self.file_menu.add_command(label="Close", command=self.cmd_close, accelerator="Ctrl+W")
        # Quit command
        self.file_menu.add_command(label="Quit", command=self.cmd_quit, accelerator="Ctrl+Q")
        #
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        #
        # steganography
        self.steg_menu = tk.Menu(self.menu_bar, tearoff=0)
        # encode command
        self.steg_menu.add_command(label="Encode", command=self.cmd_encode, accelerator="Ctrl+E")
        # decode command
        self.steg_menu.add_command(label="Decode", command=self.cmd_decode, accelerator="Ctrl+D")
        #
        self.menu_bar.add_cascade(label='Steganography', menu=self.steg_menu)
        #
        self.root.config(menu=self.menu_bar)
        self.root.bind_all("<Control-q>", self.cmd_quit)
        self.root.bind_all("<Control-s>", self.cmd_save)
        self.root.bind_all("<Control-w>", self.cmd_close)
        self.root.bind_all("<Control-o>", self.cmd_open)
        self.root.bind_all("<Control-t>", self.cmd_toggle_tab)
        self.root.bind_all("<Control-d>", self.cmd_decode)
        self.root.bind_all("<Control-e>", self.cmd_encode)

    def make_widgets(self):
        def tab_changed(*args):
            self.showpic = self.notebook.index(self.notebook.select()) == 0
            # print("tab_changed")
            # print(self.notebook.select())
            # print(self.notebook.index(self.notebook.select()))#0:Pic 1:Txt

        self.make_menus()
        #
        #  Notebook
        #
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True)
        #
        # Frames
        #
        self.framePic = ttk.Frame(self.notebook, width=View.WIDTH, height=View.HEIGHT)
        self.frameTxt = ttk.Frame(self.notebook, width=View.WIDTH, height=View.HEIGHT)
        self.framePic.pack(fill='both', expand=True)
        self.frameTxt.pack(fill='both', expand=True)
        self.notebook.add(self.framePic, text='Picture')
        self.notebook.add(self.frameTxt, text='Text')
        self.notebook.bind('<<NotebookTabChanged>>', tab_changed)
        self.notebook.select(0)
        print(self.notebook.index(self.notebook.select()))
        # canvas
        self.canvas = tk.Canvas(self.framePic, width=View.WIDTH, height=View.HEIGHT)
        self.canvas.pack()
        self.showpic = True
        # editable text window
        self.text = tk.Text(self.frameTxt, width=View.WIDTH, height=View.HEIGHT)
        self.text.pack()

    def cmd_toggle_tab(self, event=None):
        if self.notebook.index(self.notebook.select()) == 0:
            self.showpic = False
            self.notebook.select(1)
        else:
            self.showpic = True
            self.notebook.select(0)

    def cmd_open(self, event=None):
        if self.showpic:
            self.cmd_openpic()
        else:
            self.cmd_opentxt()

    def cmd_openpic(self):

        title = "Open an image file"
        self.picpath = fd.askopenfilename(title=title,
                                          filetypes=View.INPICFILES)
        if self.picpath and self.picpath.strip():
            w = ReadImageWorker(self.model, self.root, self)
            w.start()
            while not w.finished:
                time.sleep(0.1)
                self.root.update()
        else:
            title = "Open failed"
            message = "No image was specified"
            tk.messagebox.showinfo(title, message)
            logging.warning(f"{title}. {message}")

    def cmd_opentxt(self):
        title = "Open an text file"
        self.txtpath = fd.askopenfilename(title=title,
                                          filetypes=View.TXTFILES)
        if self.txtpath and self.txtpath.strip():
            self.model.read_data(self.txtpath)
            self.text.insert(tk.END, str(self.model.data, encoding='utf-8'))
        else:
            title = "Open failed"
            message = "No text file was specified"
            tk.messagebox.showinfo(title, message)
            logging.warning(f"{title}. {message}")

    def cmd_save(self, event=None):
        if self.showpic:
            self.cmd_savepic()
        else:
            self.cmd_savetxt()

    def cmd_savepic(self):
        do_it = True
        if self.picpath[-3:].lower() == 'jpg':
            logging.warning("Cannot save to jpg. Proposing png instead.")
            #
            # replace JPG by PNG in output image
            #
            self.picpath = self.picpath[:-3] + 'png'
            message = f"JPG hardly supports steganography. \nSave to '{self.picpath}' instead ?"
            do_it = tk.messagebox.askokcancel(
                title='Save image to PNG',
                message=message)
        if do_it:
            self.model.write_image(self.picpath)

    def cmd_savetxt(self):
        self.model.data = bytearray(self.text.get("1.0", tk.END), encoding='utf-8')
        if self.txtpath:
            self.model.write_data(self.txtpath)
        else:
            self.cmd_savetxtas()

    def cmd_saveas(self):
        if self.showpic:
            self.cmd_savepicas()
        else:
            self.cmd_savetxtas()

    def cmd_savepicas(self):
        title = "Save picture file as"
        self.picpath = fd.asksaveasfilename(title=title,
                                            filetypes=View.OUTPICFILES,
                                            defaultextension=View.OUTPICFILES)
        self.cmd_savepic()

    def cmd_savetxtas(self):
        title = "Save text file as"
        self.txtpath = fd.asksaveasfilename(title=title,
                                            filetypes=View.TXTFILES,
                                            defaultextension=View.TXTFILES)
        if self.txtpath:
            self.cmd_savetxt()

    def cmd_close(self, event=None):
        if self.showpic:
            self.cmd_closepic()
        else:
            self.cmd_closetxt()

    def cmd_closepic(self):
        self.canvas.delete("all")

    def cmd_closetxt(self):
        self.text.delete('1.0', tk.END)

    def cmd_quit(self, event=None):
        self.root.destroy()

    def cmd_encode(self, event=None):
        s = self.text.get("1.0", tk.END)
        self.model.data = bytes(s, 'utf-8')
        if len(self.model.data) and s != '\n':
            w = EncodingWorker(self.model, self.root)
            w.start()
            while not w.finished:
                time.sleep(0.1)
                self.root.update()
            if not self.showpic:
                self.cmd_toggle_tab()
        else:
            title = "Encoding failed"
            message = "Cannot find any text to encode"
            tk.messagebox.showinfo(title, message)
            logging.warning(f"{title}. {message}")

    def cmd_decode(self, event=None):
        w = DecodingWorker(self.model, self.root)
        try:
            w.start()
            while not w.finished:
                time.sleep(0.1)
                self.root.update()
            if self.showpic:
                self.cmd_toggle_tab()
            self.text.insert(tk.END, self.model.data.decode('utf-8'))
        except UnicodeDecodeError:
            title = "Decoding failed"
            message = "Cannot find any text message in the present picture"
            tk.messagebox.showinfo(title, message)
            logging.warning(f"{title}. {message}")

    def run(self):
        self.root.mainloop()


def main():
    v = View(controller=None, model=None)
    v.root.mainloop()


if __name__ == '__main__':
    main()
