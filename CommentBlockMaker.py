#!/usr/bin/env python

########################################################################
#                                                                      #
#                         COMMENT BLOCK MAKER                          #
#                                                                      #
#                            Version 1.0.0                             #
#                                                                      #
#            Copyright 2015 Karl Dolenc, beholdingeye.com.             #
#                         All rights reserved.                         #
#                                                                      #
#                  Python 2.6 or greater is required.                  #
#                                                                      #
#         Tested with Python 2.7 and 3.4 on Debian GNU/Linux,          #
#     and 2.6 on Mac OS X. MS Windows OS is supported, but has not     #
#                             been tested.                             #
#                                                                      #
# -------------------------------------------------------------------- #
#                                                                      #
#                             INTRODUCTION                             #
#                                                                      #
#  Comment Block Maker is a utility for programmers, converting plain  #
#  text into a fixed width comment block. The interface is quite       #
#  self-explanatory, but Usage Instructions are available in the Help  #
#  menu.                                                               #
#                                                                      #
#                                 GUI                                  #
#                                                                      #
#  This application uses a generic and versatile Tkinter GUI           #
#  template, with a layout of three rows, and three columns in the     #
#  middle row. The left and right columns are further subdivided into  #
#  two rows each. A basic menu bar is also included.                   #
#   ________________________________________________________________   #
#  |                                                                |  #
#  | topRow                                                         |  #
#  |----------------------------------------------------------------|  #
#  | midRow                                                         |  #
#  |    frameLeft         |  frameMiddle   |    frameRight          |  #
#  |                      |                |                        |  #
#  |                      |                |                        |  #
#  |    frameLeftTop      |                |    frameRightTop       |  #
#  |                      |                |                        |  #
#  |----------------------|                |------------------------|  #
#  |                      |                |                        |  #
#  |    frameLeftBottom   |                |    frameRightBottom    |  #
#  |                      |                |                        |  #
#  |----------------------------------------------------------------|  #
#  | bottomRow                                                      |  #
#  |________________________________________________________________|  #
#                                                                      #
#  In the present implementation of the GUI, the top row and the       #
#  bottom rows of the left and right columns are empty and minimized   #
#  in size. This demonstrates the ease of adapting the template.       #
#                                                                      #
#                             KNOWN ISSUES                             #
#                                                                      #
#  * The interface may not look 'right' on some setups. You may like   #
#  to experiment by turning off the ttk interface: change the  gotTtk  #
#  variable in the importing segment to  False .                       #
#  * A monospaced font will be used by the application, but in rare    #
#  cases only a serif or sans may be available, making the comment     #
#  block look broken. This is a presentational issue; pasted into an   #
#  editor with a monospaced font, the block will look as it should.    #
#  * If you copy the comment block to clipboard, then quit the         #
#  application before you have pasted the text elsewhere, the copied   #
#  text on the clipboard may be lost. However, the application will    #
#  print the comment block to the Terminal (if run from there) just    #
#  before quitting.                                                    #
#                                                                      #
#                                TO DO                                 #
#                                                                      #
#  Lack of time prevented the development of the following features    #
#  that would be nice to have.                                         #
#                                                                      #
#  * Interface control for the choice of comment symbol. The code      #
#  already allows for the comment symbol being any one of '#$;:/*\',   #
#  but '#' is presently fixed with a variable (commentChar). More      #
#  refactoring work would be needed to implement a two-character       #
#  solution.                                                           #
#  * Interface control for line length in comment block. Presently     #
#  fixed at 72 characters, the standard. A choice would be nice.       #
#  * Interface control of text font size, presently fixed at 10px.     #
#  * Option of a comment block without trailing spaces and comment     #
#  symbols, featuring only leading ones.                               #
#  * More robust solution for copying text to the clipboard. Not a     #
#  trivial undertaking, it appears.                                    #
#  * Support for right-alignment may be welcome in some cases.         #
#  Implemented in a way similar to the centering of titles, using a    #
#  special markup sequence of characters.                              #
#                                                                      #
#  Volunteers are welcome to submit patches or pull requests           #
#  implementing any of the above, for review and possible inclusion.   #
#                                                                      #
########################################################################

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  


# --------------------- IMPORTS ---------------------

from __future__ import print_function
# Future builtins imports must be at top of script for 2.6, but fail to load in 3
try:
    from future_builtins import map, filter, ascii, hex, oct, zip
except ImportError as e:
    # We're either in 2.5 or earlier - unsupported, or we're 
    # in 3+ and can continue regardless
    pass
import sys, re
import platform as pl
import textwrap as tw
gotTtk = True # Set to False if you prefer not to have ttk interface
print("Comment Block Maker starting up...")
if int(pl.python_version().split(".")[0]) >= 3: # Python version 3 or greater
    import tkinter as tk
    if gotTtk:
        import tkinter.ttk as ttk # Needed for Sizegrip, Scrollbar and themes
        print("Info: Module ttk available and loaded")
    else:
        print("Info: Module ttk not loaded, using Tkinter")
    import tkinter.font as tkfont
    import tkinter.messagebox as msg
    import tkinter.filedialog as fd
    import tkinter.simpledialog as sDialog
elif int(pl.python_version().split(".")[0]) == 2: # Python version 2.x
    import Tkinter as tk
    if gotTtk:
        try:
            import ttk # This will fail if ttk not installed, as can be the case in 2.6
            print("Info: Module ttk available and loaded")
        except ImportError as e:
            print("Info: Module ttk not loaded, using Tkinter")
            gotTtk = False
    else:
        print("Info: Module ttk not loaded, using Tkinter")
    import tkFont as tkfont
    import tkMessageBox as msg
    import tkFileDialog as fd
    import tkSimpleDialog as sDialog
else: # Can't handle versions under 2
    # Exit silently because print keyword would raise SyntaxError in Py 3
    sys.exit()


# --------------------- FUNCTIONS ---------------------

def revert_to_plain(commentBlock, commentChar):
    """Revert comment block to plain text"""
    # Revert empty lines as own paragraphs
    plainText = re.sub(r"(?m)^[#$;:/*\\][ ]+[#$;:/*\\]$\n",r"\n",commentBlock,count=0)
    # Delete lines with comment characters only (must be done here)
    plainText = re.sub(r"(?m)^[#$;:/*\\]+$\n?","",plainText,count=0)
    # Revert centred lines as own paragraphs
    plainText = re.sub(r"(?m)^[#$;:/*\\][ ]{4,}([^ ].+?)[ ]+[#$;:/*\\]$\n",
                        r"\1\n",plainText,count=0)
    # Revert lines with at least c. 1/3 as many trailing spaces as text, to own paragraphs
    testNum = int((len(commentBlock.splitlines()[0])-4)/3) # Minus 4 to account for "^#  " and "#$"
    plainText = re.sub(r"(?m)^[#$;:/*\\][ ]+([^ ].+?)[ ]{"+str(testNum)+r",}[#$;:/*\\]$\n",
                        r"\1\n",plainText,count=0)
    # Join adjacent lines of text that remain
    plainText = re.sub(r"([^ \n]+)[ ]+[#$;:/*\\]\n[#$;:/*\\]?[ ]*([^ \n]+)",r"\1 \2",plainText,count=0)
    # Remove the remaining commenting
    #plainText = plainText.strip(" "+commentChar) # regex is safer
    plainText = re.sub(r"(?m)^[#$;:/*\\][ ]+","",plainText,count=0)
    plainText = re.sub(r"(?m)[ ]+[#$;:/*\\]$","",plainText,count=0)
    if plainText[-1] == "\n": # Remove last line break
        plainText == plainText[:-1]
    return plainText

def convert_to_comment(plainText, alignCenter, centerTitles, padCount, commentChar, numChars):
    """Convert plain text to comment block"""
    blockText = ""
    plainText = plainText.replace("\t", "    ") # Convert tabs to 4 spaces
    if plainText[-1] != "\n":
        plainText == plainText + "\n"
    if padCount:
        plainText = "\n"*padCount + plainText + "\n"*padCount
    # Wrapper only works on single paragraphs
    for line in plainText.splitlines():
        if line == "":
            blockText = blockText + commentChar + " "*(numChars-2) + commentChar + "\n"
        else:
            # Center lines that start with 5+ hyphens, and are less than numChars-5 long in total
            a = ""
            if len(line) <= numChars-6 and line.startswith("-----") and centerTitles:
                line = re.sub(r"^\-+", "", line, count=1)
                a = commentChar + line.center(numChars-2) + commentChar + "\n"
                blockText = blockText + a
            else:
                for x in tw.wrap(line,width=numChars-6,replace_whitespace=False): # List of lines
                    if alignCenter:
                        a = a + commentChar + x.center(numChars-2) + commentChar + "\n"
                    else: # Align left
                        a = a + commentChar + "  " + x.ljust(numChars-4) + commentChar + "\n"
                blockText = blockText + a
    return commentChar*numChars + "\n" + blockText + commentChar*numChars


# --------------------- GUI ---------------------

class TkGui(object):
    """Tkinter GUI constructor class"""
    # Instantiation of this class is not expected
    def __init__(self, window):
        """Initialize the GUI"""
        # ttk styling theme per user operating system
        if gotTtk:
            themeStyle = ttk.Style()
            if pl.system() == "Linux" and "clam" in themeStyle.theme_names():
                themeStyle.theme_use("clam")
            elif pl.system() == "Windows" and "winnative" in themeStyle.theme_names():
                themeStyle.theme_use("winnative")
            elif pl.system() == "Windows" and "vista" in themeStyle.theme_names():
                themeStyle.theme_use("vista")
            elif pl.system() == "Windows" and "xpnative" in themeStyle.theme_names():
                themeStyle.theme_use("xpnative")
            elif "aqua" in themeStyle.theme_names():
                themeStyle.theme_use("aqua")
            elif "alt" in themeStyle.theme_names():
                themeStyle.theme_use("alt")
            else:
                themeStyle.theme_use("default")
            print("Using ttk style theme:",themeStyle.theme_use())
        # Globally set items
        textSelectColor = "#99CCFF"
        #bgColor = "#D1D1CE" # No longer used, kept here for reference
        availFonts = tkfont.families()
        textFont = ""
        for x in ("dejavu sans mono","monaco","console","consolas","monospace","sans mono",
                    "liberation mono","courier","mono","helvetica","arial"):
            try: # Take the first font that at least partly matches x
                textFont = [y for y in availFonts if x in y.lower()][0]
                break
            except: # Fail silently, continue font search
                pass
        print("Using text font:",textFont)
        textFontSize = "10"
        commentChar = "#" # Could be any -single- 1 in [#$;:/*\\]
        numChars = 72
        
        # --------------------- CREATE WIDGETS ---------------------
        
        # --------------------- Top level window
        window.title("Comment Block Maker")
        # Format the window
        winTop = window.winfo_toplevel()
        # Size of widgets within frames decides actual dimensions
        winTop.minsize(width=800, height=480) # Account for menu
        winTop.maxsize(width=4000, height=3000)
        window.minsize(width=800, height=480)
        window.maxsize(width=4000, height=3000)
        winTop.resizable(True, True)
        
        # --------------------- Application top level menu
        # Menu commands must be defined before menus
        def copy_block():
            """Copies text from the Comment Block text box to the system clipboard"""
            # Clipboard may be lost once app quits (but comment block is written to Terminal)
            commentBlock = commentText.get("1.0", "end")
            winTop.clipboard_clear()
            winTop.clipboard_append(commentBlock)
            
        def paste_plain():
            """Pastes text from the system clipboard into the Plain Text box"""
            hasFocus = winTop.focus_get()
            try:
                pasteText = winTop.selection_get(selection = "CLIPBOARD")
                #inputText.delete("1.0", "end")
                inputText.insert("end", pasteText)
            except:
                pass # Fail silently
        
        def load_file():
            """Load a text file into the Plain Text box"""
            filePath = fd.askopenfilename(filetypes=[("All","*"), ("Plain Text","*.txt")])
            if filePath:
                try:        
                    lFile = open(filePath, mode='r')
                    lText = lFile.read()
                    lFile.close()
                    inputText.delete("1.0", "end")
                    inputText.insert("1.0", lText)
                    print("Loaded file: "+filePath)
                except Exception as e:
                    # Negative number for size in pixels not points
                    window.option_add('*Dialog.msg.font', '-weight normal -size -12')
                    msgText = "Error loading file " + filePath + "\n\n" + str(e)
                    msg.showerror("Error", msgText, default=msg.OK)
                    window.option_clear()            
            
        def help_about():
            """About info box"""
            window.option_add('*Dialog.msg.font', '-weight normal -size -12')
            msgText = "          COMMENT BLOCK MAKER\n\n"
            msgText += "Copyright 2015 Karl Dolenc, beholdingeye.com. All rights reserved.\n\n"
            msgText += "Licensed under the GPL License as open source, free software.\n\n"
            msgText += "You may freely use, copy, modify and distribute this software."
            msg.showinfo("About", msgText, default=msg.OK)
            window.option_clear()
        
        def help_instructions():
            """Instructions for use"""
            window.option_add('*Dialog.msg.font', '-weight normal -size -12')
            msgText = "\nConvert a text string to a 72 character wide comment block.\n\n"
            msgText += "Lines 66 characters long or shorter and starting with 5 hyphens or more\n"
            msgText += "can be centered as titles; check the 'Center -----Titles' button.\n\n"
            msgText += "Check the 'Padding Start/End' button to add an empty line at "
            msgText += "the beginning and end of the comment block.\n\n"
            msgText += "Reverting the comment block back to plain text may not reproduce "
            msgText += "the original text. Tabs are converted to spaces, some spaces may be "
            msgText += "removed, and line breaks changed.\n"
            msg.showinfo("Usage Instructions", msgText, default=msg.OK)
            window.option_clear()
        
        def quit_from_menu():
            """Print Comment box contents in Terminal and exit"""
            if len(commentText.get("1.0", "end")) > 1:
                print("Comment block:\n\n" + commentText.get("1.0", "end") + "\nDone.")
            winTop.quit()

        # --------------------- Menu items
        mainMenu = tk.Menu(winTop)
        # File menu
        fileMenu = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="File", menu=fileMenu)
        if pl.mac_ver()[0] != '': # We're in Mac OS
            fileMenu.add_command(label="Load Plain Text File...", command=load_file, 
                                    accelerator="Cmd - O")
            fileMenu.add_command(label="Quit", command=quit_from_menu, accelerator="Cmd - Q")
        else:
            fileMenu.add_command(label="Load Plain Text File...", command=load_file, 
                                    accelerator="Ctrl - O")
            fileMenu.add_command(label="Quit", command=quit_from_menu, accelerator="Ctrl - Q")
        # Edit menu
        editMenu = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Copy Comment Block", command=copy_block)
        editMenu.add_command(label="Paste Plain Text", command=paste_plain)
        # Help menu
        helpMenu = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="Help", menu=helpMenu)
        helpMenu.add_command(label="About", command=help_about)
        helpMenu.add_command(label="Usage Instructions", command=help_instructions)
        winTop.config(menu=mainMenu)
        
        # --------------------- Window frame of 3 rows
        # Top window frame, containing three rows
        if gotTtk: winFrame = ttk.Frame(window) # Needed as top object
        else: winFrame = tk.Frame(window)
        winFrame.columnconfigure(0, minsize=800, pad=0, weight=1) # Need weight for stretching
        winFrame.rowconfigure(0, minsize=5, pad=0, weight=0) # Top and bottom rows are static
        winFrame.rowconfigure(1, minsize=200, pad=0, weight=10)
        winFrame.rowconfigure(2, minsize=20, pad=0, weight=0)
        # Top row frame
        if gotTtk: topRow = ttk.Frame(winFrame, relief="flat")
        else: topRow = tk.Frame(winFrame, relief="flat")
        # Middle row frame, containing three columns
        if gotTtk: midRow = ttk.Frame(winFrame, relief="flat")
        else: midRow = tk.Frame(winFrame, relief="flat")
        midRow.columnconfigure(0, minsize=300, pad=0, weight=1) # Input box to stretch less...
        midRow.columnconfigure(1, minsize=100, pad=0, weight=0)
        midRow.columnconfigure(2, minsize=300, pad=0,  weight=2) # ...than the comment box
        midRow.rowconfigure(0, minsize=400, pad=0,  weight=1) # Account for other rows
        # Bottom row frame
        if gotTtk: bottomRow = ttk.Frame(winFrame, relief="flat")
        else: bottomRow = tk.Frame(winFrame, relief="flat")
        
        # --------------------- Top row contents
        # None
        
        # --------------------- Mid row contents
        # Left vertical frame, containing two rows
        if gotTtk: frameLeft = ttk.Frame(midRow, width=200, height=400)
        else: frameLeft = tk.Frame(midRow, width=200, height=400)
        frameLeft.columnconfigure(0, minsize=200, pad=0,  weight=1)
        frameLeft.rowconfigure(0, minsize=200, pad=0,  weight=10)
        frameLeft.rowconfigure(1, minsize=5, pad=0,  weight=0) # Bottom row is static
        # The two horizontal frames within
        if gotTtk: frameLeftTop = ttk.LabelFrame(frameLeft)
        else: frameLeftTop = tk.LabelFrame(frameLeft)
        frameLeftTop.config(width=200, height=200, text=" Plain Text Input ")
        if gotTtk: frameLeftBottom = ttk.Frame(frameLeft)
        else: frameLeftBottom = tk.Frame(frameLeft)
        frameLeftBottom.config(width=200, height=5)

        # --------------------- Plain Text Input box frame
        inputTextFrame = tk.Frame(frameLeftTop, border=1, relief="flat", 
                                highlightthickness=1, highlightcolor="gray") # No need for ttk
        # Text height / width is in lines and characters, not pixels
        # No Text widget in ttk
        inputText=tk.Text(inputTextFrame, height=1, width=1, borderwidth=0, 
                        font=(textFont, textFontSize), selectbackground=textSelectColor, 
                        selectforeground="black", padx=4, pady=4, relief="flat", 
                        undo=True, wrap="word", highlightthickness=0, name="inputText")
        # Scrollbar for text box
        if gotTtk: inputScroll=ttk.Scrollbar(inputTextFrame, name="inputScroll")
        else: inputScroll=tk.Scrollbar(inputTextFrame, name="inputScroll")
        inputScroll.config(orient="vertical", command=inputText.yview)
        inputText.configure(yscrollcommand=inputScroll.set)
        
        # Middle vertical frame
        if gotTtk: frameMiddle = ttk.Frame(midRow, width=100, height=400)
        else: frameMiddle = tk.Frame(midRow, width=100, height=400)
        # Convert and Revert buttons
        if gotTtk:
            btnConvert = ttk.Button(frameMiddle, name="btnConvert", text="Convert ->")
            btnRevert = ttk.Button(frameMiddle, name="btnRevert", text="<- Revert")
        else:
            btnConvert = tk.Button(frameMiddle, name="btnConvert", text="Convert ->")
            btnRevert = tk.Button(frameMiddle, name="btnRevert", text="<- Revert")
        
        # --------------------- Preferences
        # Alignment options
        if gotTtk: alignFrame = ttk.LabelFrame(frameMiddle)
        else: alignFrame = tk.LabelFrame(frameMiddle)
        alignFrame.config(width=100, height=150, text=" Align Comments ")
        radioAlignCtrl = tk.IntVar()
        if gotTtk: radioAlignLeft = ttk.Radiobutton(alignFrame, name="radioAlignLeft")
        else: radioAlignLeft = tk.Radiobutton(alignFrame, name="radioAlignLeft")
        radioAlignLeft.config(text="Left", value=0, variable=radioAlignCtrl)
        if gotTtk: radioAlignCenter = ttk.Radiobutton(alignFrame, name="radioAlignCenter")
        else: radioAlignCenter = tk.Radiobutton(alignFrame, name="radioAlignCenter")
        radioAlignCenter.config(text="Center", value=1, variable=radioAlignCtrl)
        radioAlignLeft.invoke()
        centerTitlesCtrl = tk.IntVar()
        if gotTtk: checkCenterTitles = ttk.Checkbutton(alignFrame, name="checkCenterTitles")
        else: checkCenterTitles = tk.Checkbutton(alignFrame, name="checkCenterTitles")
        checkCenterTitles.config(text="Center -----Titles", variable=centerTitlesCtrl)
        
        # Option to pad with empty line at start and end of block
        padLinesCtrl = tk.IntVar()
        if gotTtk: checkPadLines = ttk.Checkbutton(frameMiddle, name="checkPadLines")
        else: checkPadLines = tk.Checkbutton(frameMiddle, name="checkPadLines")
        checkPadLines.config(text="Padding Start/End", variable=padLinesCtrl)
        
        # Right vertical frame
        if gotTtk: frameRight= ttk.Frame(midRow, width=400, height=400)
        else: frameRight= tk.Frame(midRow, width=400, height=400)
        frameRight.columnconfigure(0, minsize=300, pad=0,  weight=1)
        frameRight.rowconfigure(0, minsize=200, pad=0,  weight=10)
        frameRight.rowconfigure(1, minsize=5, pad=0,  weight=0)
        # Two horizontal frames within
        if gotTtk: frameRightTop = ttk.LabelFrame(frameRight)
        else: frameRightTop = tk.LabelFrame(frameRight)
        frameRightTop.config(width=400, height=200, text=" Comment Block Output ")
        if gotTtk: frameRightBottom = ttk.Frame(frameRight, width=400, height=5)
        else: frameRightBottom = tk.Frame(frameRight, width=400, height=5)

        # --------------------- Comment Box Text box frame
        commentTextFrame = tk.Frame(frameRightTop, border=1, relief="flat", 
                                highlightthickness=1, highlightcolor="gray")
        commentText=tk.Text(commentTextFrame, height=1, width=1, borderwidth=0, 
                        font=(textFont, textFontSize), selectbackground=textSelectColor, 
                        selectforeground="black", padx=4, pady=4, relief="flat", 
                        undo=True, wrap="none", highlightthickness=0, name="commentText")
        # Scrollbar for text box
        if gotTtk: commentScroll=ttk.Scrollbar(commentTextFrame, name="commentScroll")
        else: commentScroll=tk.Scrollbar(commentTextFrame, name="commentScroll")
        commentScroll.config(orient="vertical", command=commentText.yview)
        commentText.configure(yscrollcommand=commentScroll.set)
        
        # --------------------- Bottom row contents
        # Quit button
        if gotTtk: btnQuit = ttk.Button(bottomRow, name="btnQuit")
        else: btnQuit = tk.Button(bottomRow, name="btnQuit")
        btnQuit.config(text="Quit", command=quit_from_menu)
        # Window resizing corner widget, only in ttk
        if gotTtk: winGrip = ttk.Sizegrip(window)
        
        # --------------------- CALLBACKS & COMMANDS ---------------------
        # These methods need to be in the scope of __init__    
        
        def convert_text():
            """Convert plain text input to comment block"""
            inputString = inputText.get("1.0", "end")
            if len(inputString) > 999999: # Let's stay sane
                print("Text too long. Work with chunks shorter than 1,000,000 characters.")
                return
            commentBlock = convert_to_comment(inputString, radioAlignCtrl.get(), 
                                                centerTitlesCtrl.get(), padLinesCtrl.get(), 
                                                commentChar, numChars)
            commentText.delete("1.0", "end")
            commentText.insert("1.0", commentBlock)
        # Convert button binding
        btnConvert.config(command=convert_text)

        def revert_text():
            """Revert comment block to plain text"""
            commentBlock = commentText.get("1.0", "end")
            revertedString = revert_to_plain(commentBlock, commentChar)
            inputText.delete("1.0", "end")
            inputText.insert("1.0", revertedString)
        # Revert button binding
        btnRevert.config(command=revert_text)

        # --------------------- Event handlers
        
        def mouse_wheel_scroll(event):
            """Mousewheel scrolling of Text box scrollbars"""
            scrollCount = 0
            # Linux v. Windows v. Mac
            if event.num == 5 or event.delta == -120 or event.delta == -1:
                scrollCount = 2
            elif event.num == 4 or event.delta == 120 or event.delta == 1:
                scrollCount = -2
            if str(event.widget).split(".")[-1] == "inputScroll": # Name is last in .path
                inputText.yview_scroll(scrollCount, "units")
            if str(event.widget).split(".")[-1] == "commentScroll":
                commentText.yview_scroll(scrollCount, "units")
        # Mousewheel binding
        inputScroll.bind("<MouseWheel>", mouse_wheel_scroll) # Windows/Mac
        inputScroll.bind("<Button-4>", mouse_wheel_scroll) # Linux (Up)
        inputScroll.bind("<Button-5>", mouse_wheel_scroll) # Linux (Down)
        commentScroll.bind("<MouseWheel>", mouse_wheel_scroll)
        commentScroll.bind("<Button-4>", mouse_wheel_scroll)
        commentScroll.bind("<Button-5>", mouse_wheel_scroll)
        
        def resize_window(event):
            """Resizing window with winGrip widget"""
            x1 = window.winfo_pointerx()
            y1 = window.winfo_pointery()
            x0 = window.winfo_rootx()
            y0 = window.winfo_rooty()
            window.geometry("%sx%s" % (max((x1-x0),800),max((y1-y0),480)))
            return
        # Window resizing call
        if gotTtk:
            winGrip.bind("<B1-Motion>", resize_window)

        def quit_app(event):
            """Quit application"""
            quit_from_menu()
        # Obtain text on close of window
        window.wm_protocol("WM_DELETE_WINDOW", quit_from_menu) # No event passed
        # Quit accelerator binding
        if pl.mac_ver()[0] != '':
            winTop.bind_all("<Command-q>", quit_app)
        else:
            winTop.bind_all("<Control-q>", quit_app)
        
        def open_app(event):
            """Run the Load File command"""
            load_file()
        # Load File accelerator binding
        if pl.mac_ver()[0] != '':
            winTop.bind_all("<Command-o>", open_app)
        else:
            winTop.bind_all("<Control-o>", open_app)

        # --------------------- PLACE WIDGETS ---------------------
        
        # Window of 3 rows
        winFrame.pack(side="top", fil="both", expand=True)
        topRow.grid(column=0, row=0, sticky="wens")
        midRow.grid(column=0, row=1, sticky="wens")
        bottomRow.grid(column=0, row=2, sticky="wens")
        
        # --------------------- Top row contents
        # None
        
        # --------------------- Mid row contents
        # Left column
        frameLeft.grid(column=0, row=0, sticky="wens")
        frameLeftTop.grid(column=0, row=0, padx=10, pady=10, sticky="wens")
        frameLeftBottom.grid(column=0, row=1, sticky="wens")
        # Text box
        inputTextFrame.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        inputText.pack(side="left", fill="both", expand=True)
        inputScroll.pack(side="right", fill="y", expand=False)
        
        # Middle column
        frameMiddle.grid(column=1, row=0, sticky="wens")
        # Comment block alignment buttons
        alignFrame.grid(column=0, row=0, pady=10, ipady=10)
        radioAlignLeft.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        radioAlignCenter.grid(column=1, row=0, padx=10, sticky="w")
        checkCenterTitles.grid(column=0, columnspan=2, row=1, padx=10, sticky="w")
        
        checkPadLines.grid(column=0, row=1, padx=10, pady=10)
        
        btnConvert.grid(column=0, row=2, pady=30)
        btnRevert.grid(column=0, row=3)
        
        # Right column
        frameRight.grid(column=2, row=0, sticky="wens")
        frameRightTop.grid(column=0, row=0, padx=10, pady=10, sticky="wens")
        frameRightBottom.grid(column=0, row=1, sticky="wens")
        # Text box
        commentTextFrame.pack(side="top", fill="both", expand=True, padx=20, pady=20)
        commentText.pack(side="left", fill="both", expand=True)
        commentScroll.pack(side="right", fill="y", expand=False)
        
        # --------------------- Bottom row contents
        btnQuit.pack(side="bottom", padx=20, pady=10, ipadx=10)

        if gotTtk:
            winGrip.place(relx=1.0, rely=1.0, anchor="se")
            winGrip.lift()

if __name__=="__main__":
    window = tk.Tk()
    app = TkGui(window)
    window.mainloop()
