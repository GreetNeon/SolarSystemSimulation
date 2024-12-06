####################################################################################################
# Description: This file contains the code for the main menu GUI. The main menu GUI is the first
# thing that the user sees when they run the program. The main menu GUI contains buttons that the
# user can click on to navigate to different parts of the program.
####################################################################################################

# Importing the necessary modules
import pygame
import sys
from transitions import start_sim
import pygame_menu as pm
import pickle as pkl
import os

pygame.init()

# Defining the main menu class
class MainMenu:
    # Defining the constructor
    def __init__(self):
        # Defining the important variables
        self.win = pygame.display.set_mode((800, 600))
        self.running = True
        self.buttons = {}
        self.font = pygame.font.SysFont("Arial", 36)
        self.button_text = ["Start Simulation", "Settings", "Exit"]
        self.settings_button_text = []
        self.menu_theme = pm.themes.THEME_DARK.copy()
        self.settings_theme = pm.themes.THEME_BLUE.copy(); self.menu_theme.title_font = pm.font.FONT_NEVIS; self.menu_theme.widget_font = pm.font.FONT_NEVIS
        self.settings_theme.widget_alignment = pm.locals.ALIGN_LEFT ; self.settings_theme.widget_font = pm.font.FONT_NEVIS; self.settings_theme.title_font = pm.font.FONT_NEVIS
        self.menu = pm.Menu(title="Solar System Simulation", 
                        width=800, 
                        height=600, 
                        theme=self.menu_theme)
        self.settings_menu = pm.Menu(title="Settings", 
                        width=800, 
                        height=600, 
                        theme=self.settings_theme) 
    
    # Defining the load_buttons method
    def load_menu_buttons(self):
        # Creating the buttons
        # Create a dictionary of button text and their corresponding functions
        try:
            button_functions = {
                "Start Simulation": lambda: self.play(self.settings_menu),
                "Settings": self.settings_menu,
                "Exit": sys.exit}
            
            for i in range(len(self.button_text)):
                button = self.menu.add.button(self.button_text[i], button_functions[self.button_text[i]])
                self.buttons[self.button_text[i]] = button
        except(pygame.error):
            print("Error loading menu buttons")
    
    def load_settings_buttons(self):
        try:
            graphics = [("Low", "low"), 
                        ("Medium", "medium"), 
                        ("High", "high"), 
                        ("Ultra High", "ultra high")]
            self.settings_menu.add.dropselect(title="Graphics Level", items=graphics, 
                                dropselect_id="graphics", default=0)
            resolutions = [("1200x650", (1200, 650)), ("800x600", (800, 600)),
                            ("400x300", (400, 300))]
            self.settings_menu.add.dropselect(title="Resolution", items=resolutions, 
                                dropselect_id="resolution", default=0)
        except(pygame.error):
            print("Error loading settings buttons")

    def play(self, settings_menu):
        pygame.display.quit()
        self.save_data(settings_menu)
        start_sim()

    def save_data(self, menu):
        data = menu.get_input_data()
        with open("data/settings.txt", "wb") as f:
            pkl.dump(data, f)

    # Defining the main loop
    def main_loop(self):
        # Creating the window
        pygame.display.set_caption("Solar System Simulation")
        # Loading Menu Buttons
        self.load_menu_buttons()
        # Loading Settings Buttons
        self.load_settings_buttons()
        self.menu.mainloop(self.win)

    def returning_menu(self):
        self.main_loop()
# Defining the main loopd
def main():
    # Creating the main menu
    main_menu = MainMenu()
    # Running the main loop
    main_menu.main_loop()


if __name__ == "__main__":
    # Running the main function
    main()