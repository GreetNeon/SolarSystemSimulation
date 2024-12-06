#########################################################################################################################
# Description: This file contains the functions to enable transitioning between screens in the program.
#########################################################################################################################

# Importing the necessary modules
import os

def start_sim(): 
    os.startfile("main.pyw")
    exit()

def start_menu():

    import menu_gui
    menu_gui.main()

