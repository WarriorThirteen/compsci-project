# Menu verison 1
import tkinter as tk
import tkfontchooser as tkFont



def __init__():
    

    ##  Variables
    global WINDOW_WIDTH
    global WINDOW_HEIGHT
 
    global WINDOW_BACKGROUND   # Gray chosen in documentation
    global BUTTON_BACKGROUND

    global FONT_FAMILY


    WINDOW_WIDTH = 1280     # These can be changed, but convenient for 720p to be used for
    WINDOW_HEIGHT = 720     # reasons mentioned in design
 
    WINDOW_BACKGROUND = "#FAFAFA"   # Gray chosen in documentation
    BUTTON_BACKGROUND = "white"
 
    FONT_FAMILY = "MV Boli"


    global sound_on
 
    global opened_home
    global opened_sp
    global opened_mp

    sound_on = True
 
    opened_home = False
    opened_sp = False
    opened_mp = False



    ##  Create and display menu

    global root
    root = tk.Tk()
    root.title("Jario")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.configure(bg=WINDOW_BACKGROUND)

    global large_font
    large_font = tkFont.Font(root=root, family=FONT_FAMILY, size=20)


    global unmuted_icon
    global muted_icon
    global cross_icon

    unmuted_icon = tk.PhotoImage(file="resources/images/menu_images/mute_icon.png")
    muted_icon = tk.PhotoImage(file="resources/images/menu_images/mute_icon_muted.png")
    cross_icon = tk.PhotoImage(file="resources/images/menu_images/cross_icon.png")



def not_implemented():
    '''
    Placeholder function to provide for not yet implemented buttons
    This allows quick searching of the document for incomplete functions
    '''
    not_implemented_text = "This function has not been implemented yet"

    alert(not_implemented_text)
    print(not_implemented_text)


def alert(text):
    alert_window = tk.Toplevel(root)
    alert_window.minsize(200, 200)

    alert_window.title("Alert")
    tk.Label(alert_window, text=text).pack()







##  Button Functions

# opening menus
def open_home_menu():
    global opened_home
    if not opened_home:

        ##  Main Menu screen
        global home_menu_frame
        home_menu_frame = tk.Frame(root, bg=WINDOW_BACKGROUND)

        title = tk.Label(home_menu_frame, text="Jario", font=large_font, bg=WINDOW_BACKGROUND)
        title.place(relx=0.5, rely=0.125, anchor="n")


        ##  Singleplayer and multiplayer buttons

        global btn_singleplayer
        btn_singleplayer = tk.Button(home_menu_frame, command=open_singleplayer_menu, text="Single Player", font=large_font)
        btn_singleplayer.place(relx=0.2, rely=0.5, relwidth=0.2, relheight=0.15, anchor="w")

        global btn_multiplayer
        btn_multiplayer = tk.Button(home_menu_frame, command=open_multiplayer_menu, text="Multiplayer", font=large_font)
        btn_multiplayer.place(relx=0.6, rely=0.5, relwidth=0.2, relheight=0.15, anchor="w")



        ##  auxiliary buttons

        global btn_sound_toggle
        btn_sound_toggle = tk.Button(home_menu_frame, command=toggle_sound, image=unmuted_icon)
        btn_sound_toggle.place(relx=0.05, rely=0.1)

        global btn_close_program
        btn_close_program = tk.Button(home_menu_frame, command=close_program, image=cross_icon)
        btn_close_program.place(relx=0.95, rely=0.1, anchor="ne")

        opened_home = True


    home_menu_frame.pack(fill="both", expand=True)


def open_multiplayer_menu():
    not_implemented()


def open_singleplayer_menu():
    not_implemented()


def toggle_sound():
    global sound_on
    if sound_on:
        btn_sound_toggle.config(image=muted_icon)
        sound_on = False

    else:
        btn_sound_toggle.config(image=unmuted_icon)
        sound_on = True

    not_implemented()


def close_program():
    exit()




if __name__ == "__main__":

    __init__()
    
    open_home_menu()

    root.mainloop()
