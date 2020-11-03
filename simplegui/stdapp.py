import os
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, simpledialog, messagebox, scrolledtext #Frame, Variable, Scrollbar, Text, 
from tkinter.ttk import *
from tkinter.constants import VERTICAL, RIGHT, LEFT, BOTH, END, Y, SUNKEN, RAISED, GROOVE, FLAT, RIDGE, N, S, E, W
import logging

class MonitoredText(Frame):
    """Extends Frame.  Intended as a container for a Text field.  Better related data handling
    and has Y scrollbar."""


    def __init__(self, master, textvariable=None, *args, **kwargs):

        super(MonitoredText, self).__init__(master)
        # Init GUI

        self._y_scrollbar = Scrollbar(self, orient=VERTICAL)

        self._text_widget = Text(self, yscrollcommand=self._y_scrollbar.set, *args, **kwargs)
        self._text_widget.pack(side=LEFT, fill=BOTH, expand=1)

        self._y_scrollbar.config(command=self._text_widget.yview)
        self._y_scrollbar.pack(side=RIGHT, fill=Y)

        if textvariable is not None:
            if not (isinstance(textvariable, Variable)):
                raise TypeError("tkinter.Variable type expected, " + str(type(textvariable)) + " given.".format(type(textvariable)))
            self._text_variable = textvariable
            self.var_modified()
            self._text_trace = self._text_widget.bind('<<Modified>>', self.text_modified)
            self._var_trace = textvariable.trace("w", self.var_modified)

    def text_modified(self, *args):
            if self._text_variable is not None:
                self._text_variable.trace_vdelete("w", self._var_trace)
                self._text_variable.set(self._text_widget.get(1.0, END))
                self._var_trace = self._text_variable.trace("w", self.var_modified)
                self._text_widget.edit_modified(False)
    def var_modified(self, *args):
        self.set_text(self._text_variable.get())
        self._text_widget.edit_modified(False)

    def unhook(self):
        if self._text_variable is not None:
            self._text_variable.trace_vdelete("w", self._var_trace)

    def clear(self):
        self._text_widget.delete(1.0, END)

    def set_text(self, _value):
        self.clear()
        if (_value is not None):
            self._text_widget.insert(END, _value)

class ProgressWindow(simpledialog.Dialog):
    def __init__(self, parent, name, abortComputation):
        ''' Init progress window '''
        Toplevel.__init__(self, master=parent)
        self.abortComputation = abortComputation # function to call when user hit Cancel
        self.title(name)
        self.length = 400
        self.focus_set()  # set focus on the ProgressWindow
        self.grab_set()  # make a modal window, so all events go to the ProgressWindow
        self.transient(self.master)  # show only one window in the task bar
        #
 
        self.resizable(False, False)  # window is not resizable
        # self.abort gets fired when the window is destroyed
        self.protocol(u'WM_DELETE_WINDOW', self.abort)
        # Set proper position over the parent window
        dx = (self.master.winfo_width() >> 1) - (self.length >> 1)
        dy = (self.master.winfo_height() >> 1) - 50
        self.geometry(u'+{x}+{y}'.format(x = self.master.winfo_rootx() + dx,
                                         y = self.master.winfo_rooty() + dy))
        #self.bind(u'<Escape>', self.abort)  # cancel progress when <Escape> key is pressed
        

    def initialize(self, size):
        ''' Widgets for progress window are created here '''
        self.var1 = StringVar()
        self.var2 = StringVar()
        self.num = IntVar()
        # pady=(0,5) means margin 5 pixels to bottom and 0 to top
        Label(self, textvariable=self.var1).pack(anchor='w', padx=2)
        self.progress = Progressbar(self, maximum=size, orient='horizontal',
                                        length=self.length, variable=self.num, mode='determinate')
        self.progress.pack(padx=2, pady=2)
        Label(self, textvariable=self.var2).pack(side=LEFT, padx=2)
        Button(self, text='Cancel', command=self.abort).pack(anchor='e', padx=1, pady=(0, 1))
        self.aborted = False
        self.update()

    def step(self, step=1):
        ''' Make the progress bar progress by one or more step(s), return false if the computation should stop '''
        if self.aborted:
            return False
        n = self.num.get()
        n += step
        self.num.set(n)
        self.update()
        return True

    def terminate(self):
        ''' Close progress window '''
        self.master.focus_set()  # put focus back to the parent window
        self.destroy()  # destroy progress window

    def message(self, txt):
        logging.info(txt)
        self.var2.set(txt)
        self.update()

    def abort(self, event=None):
        ''' abort computation and close window '''
        self.aborted = True
        self.abortComputation()
        self.terminate()


class ListVar(Variable):
    def __init__(self, master=None, name=None, **kwargs):
        Tkinter.Variable.__init__(self, master, kwargs.get('values'), name)

    def set(self, values):
        self._tk.call('set', self._name, values)

    def set_index(self, index, value):
        self._tk.call('lset', self._name, index, value)

    def get_index(self, index):
        return self._tk.eval('lindex $%s %d' % (self._name, index))

    def get(self, start=None, end=None):
        if start is None and end is None:
            res = self._tk.eval('lrange $%s 0 end' % self._name)
        elif end is None:
            res = self._tk.eval('lrange $%s %d end' % (self._name, start))
        else:
            res = self._tk.eval('lrange $%s %d %d' % (self._name, start, end))
        return self._tk.splitlist(res)

    def swap(self, a, b):
        if a != b:
            tmp = self.get_index(a)
            self.set_index(a, self.get_index(b))
            self.set_index(b, tmp)

    def append(self, value):
        self._tk.eval('lappend %s {%s}' % (self._name, value))



class StdApp:
    def __init__(self, title):
        self.rootwindow = Tk()
        self.rootwindow.title(title)
        menubar = Menu(self.rootwindow)
        self.configFileMenu(menubar)
        self.configEditMenu(menubar)
        self.configOtherMenus(menubar)
        self.configHelpMenu(menubar)
        self.rootwindow.config(menu=menubar)
        self.rootwindow.protocol(u'WM_DELETE_WINDOW', self.close)

    def mainloop(self):
        '''Lancement de la boucle événementielle'''
        self.rootwindow.mainloop()

    def configFileMenu(self,menubar):
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='New', command=self.fnew)
        filemenu.add_command(label='Open', command=self.fopendialog)
        filemenu.add_command(label='Save', command=self.fsave)
        filemenu.add_command(label='Save as...', command=self.fsavedialog)
        filemenu.add_separator()  
        filemenu.add_command(label='Quit', command=self.close) # quitte le programme

    def fnew(self):
        if not self.model.isDirty() or messagebox.askokcancel("Confirm","Data has been modified. Proceed anyway?"):
            self.model.reset()

    def close(self):
        if not self.model.isDirty() or messagebox.askokcancel("Confirm","Data has been modified. Quit anyway?"):
            self.rootwindow.quit()

    def fsave(self):
        if self.model.isNew():
            self.fsavedialog()
        else:
            self.model.resave() # because model.filename not None
 
    def fsavedialog(self):
        if self.model.filename is None:
            currentPath = os.getcwd()
        else:
            currentPath = os.path.dirname(Path(self.model.filename))
        f = filedialog.asksaveasfile\
                 (
                     title='Save query as...',
                     mode='w',
                     defaultextension=self.model.fileExtension, 
                     initialdir=currentPath
                 )
        if f is not None:
            self.model.saveTo(f)
        
    def fopendialog(self):
        if self.model.filename is None:
            currentPath = os.getcwd()
        else:
            currentPath = os.path.dirname(Path(self.model.filename))
        f = filedialog.askopenfile\
                 (
                     mode='r', 
                     defaultextension=self.model.fileExtension, 
                     initialdir=currentPath
                 )
        if f is not None:
            self.model.loadFrom(f) 

    def chooseDir(self, msg: str, startDir: str) -> str:
        if startDir is None:
            if self.model.filename is None:
                startDir = os.getcwd()
            else:
                startDir = os.path.dirname(Path(self.model.filename))
        d = filedialog.askdirectory\
                 (
                    title=msg,
                    initialdir=startDir
                 )
        return d


    def configEditMenu(self,menubar):
        self.editmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Edit', menu=self.editmenu)

    def configOtherMenus(self,menubar):
        '''To be redefined as needed in subclass'''
        pass

    def configHelpMenu(self,menubar):
        self.helpmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=self.helpmenu)
        self.helpmenu.add_command(label='About', command=self.aboutdialog)  

    def aboutdialog(self):
        messagebox.showinfo("About",self.about())

    def warning(self,message):
        messagebox.showwarning("Warning", message)
        
    def createLabelledSpinbox(self,container,intvar,label,lowerbound,upperbound,cmd):
        lf = LabelFrame(container, text=label)
        w = Spinbox(lf, from_=lowerbound, to=upperbound, textvariable=intvar, command=cmd)
        w.pack()
        return lf

    def createRadiobuttons(self,container,textvar,label,values,cmd):
        lf = LabelFrame(container, text=label)
        for v in values:
            b = Radiobutton(lf, text=v, value=v, variable=textvar, command=cmd)
            b.pack(anchor='w')
        return lf
      

    def createEntry(self,container,textvar,label,_width,cmd):
        f = LabelFrame(container, text=label)
        # l = Label(f, text=label)
        # l.pack(side=LEFT)
        entry = Entry(f,textvariable=textvar, width=_width)
        entry.pack(side=LEFT)
        entry.bind('<KeyRelease>',cmd)
        return f

    def createTextBox(self,container,textvar,label,lines,cols,cmd):
        lf = LabelFrame(container, text=label)
        lf.pack()
        text = MonitoredText(lf, textvar, height=lines, width=cols)
        text.pack()
        text.bind('<KeyRelease>',cmd)
        return lf

    def createNotebook(self, container):
        nb = Notebook(container)
        nb.enable_traversal()
        nb.pack(side=TOP,expand=1, fill="both")
        return nb

    def createTab(self,notebook,label,sheetType):
        sheet = Frame(notebook) if sheetType=='table' else scrolledtext.ScrolledText(notebook)
        notebook.add(sheet, text=label)
        return sheet
    
#    style = Style()
#    style.configure("Plain", foreground="black", background="white")
    def createCell(self,sheet,row,col,value,title=False):
        ''' create a cell in the current tab of a Notebook'''
        relief = FLAT  if title or col==0 else SUNKEN #GROOVE RIDGE
        sticky = W if col==0 else E
        cell = Label(sheet,text=str(value),relief=relief)#,width=-6
        cell.grid(row=row,column=col,ipadx=2,ipady=4,sticky=sticky)
        return cell
    
    def insertText(self,sheet,text,position=END):
        ''' Insert text at position in sheet'''
        sheet.config(state=NORMAL)
        sheet.insert(position,text)
        sheet.config(state=DISABLED)
    
    # def createListbox(self,container,cmd,initValue):
    #     result = Variable(value=initValue)
    #     lb = Listbox(master=container, listvariable=result)
    #     lb.pack(fill=BOTH, expand=True)
    #     lb.bind('<Key-Return>',cmd)
    #     return result




