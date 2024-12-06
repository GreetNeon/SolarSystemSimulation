####################################################################################################
# Description: Main file for the project
# Dependencies: calculations.py, menu_GUI.py, transitions.py
# Author: Teon Green
# Current Bugs: 
####################################################################################################

# Importing the calculations module
import calculations
import pygame
import pickle as pkl
from transitions import start_menu
from simulation_classes import Planet, set_planets, Button
import pygame_menu as pm
import sys
import pandas as pd
import time

pygame.init()
# Loading the settings
settings_file = open("data/settings.txt", "rb")
settings = pkl.load(settings_file)
settings_file.close()
resolution = settings["resolution"][0][1]
graphics = settings["graphics"][0][1]

def create_pause_menu():
    pause_menu_image = pm.baseimage.BaseImage(image_path="gfx/pause_background.png", drawing_mode=pm.baseimage.IMAGE_MODE_FILL)
    mytheme = pm.Theme(background_color=pause_menu_image, # transparent background
                title_background_color=(4, 47, 126),
                title_font_shadow=True,
                title_font = pm.font.FONT_NEVIS,
                title_font_size = 70,
                widget_font = pm.font.FONT_NEVIS,
                widget_padding = 25,
                widget_font_color = (255, 255, 255),
                widget_selection_effect = pm.widgets.HighlightSelection(),
                widget_border_color = (0, 0, 255))
    pause_menu = pm.Menu(title="Pause Menu", width=resolution[0], height=resolution[1], theme=mytheme)
    # Creating the settings menu
    settings_menu = pm.Menu(title="Settings", width=resolution[0], height=resolution[1], theme=mytheme)
    settings_menu.add.toggle_switch("Show Fps", True, toggleswitch_id='fps')
    settings_menu.add.toggle_switch("Show Orbit Lines:", True, toggleswitch_id = "orbits_lines")
    settings_menu.add.toggle_switch("Dynamic Orbit Lines:", True, toggleswitch_id = "dynamic_orbit")
    settings_menu.add.toggle_switch("Show Images:", True, toggleswitch_id = "images")
    settings_menu.add.toggle_switch("Show Sim Speed:", True, toggleswitch_id = "time")
    settings_menu.add.color_input('Button Hover Colour: ', color_type=pm.widgets.COLORINPUT_TYPE_RGB, default=(255, 0, 0), color_id='hover_colour')

    pause_menu.add.button("Resume", lambda: pause_menu.disable())
    pause_menu.add.button("Settings", settings_menu)
    pause_menu.add.button("Exit to menu", lambda: start_menu())
    pause_menu.add.button("Exit to desktop", lambda: quit())

    pause_menu.disable()
    return pause_menu, settings_menu



def main_sim():
    planets = set_planets()
    FPS = 90
    clock = pygame.time.Clock()
    # Defining the main variables
    running = True
    check_settings = False
    screen_w = resolution[0]
    screen_h = resolution[1]
    show_orbit_lines = True
    show_fps = True
    show_images = True
    show_time = True
    dynamic_orbit_lines = False
    sim_paused = False
    last_paused = time.time()
    main_font = pygame.font.SysFont("Nevis", 20)
    hover_colour = (255, 0, 0)
    # Defining planets
    planets = set_planets()
    # Allows controls to be held down
    pygame.key.set_repeat(1)
    # Creating the window
    window = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Solar System Simulation")

    # Creating the pause menu
    pause_menu, settings_menu = create_pause_menu()
    # Creating in-game buttons
    show_controls = Button(screen_w * 0.95, screen_h * 0.01, "Show Controls", main_font)

    #Creating main loop
    while running:
        
        window.fill((0, 0, 0))
        clock.tick(FPS)
        # Updating the planets
        for planet in planets:
            if planet.win is None:
                planet.set_window(window)
            if not sim_paused:
                planet.update_position(planets)
            planet.draw(show_orbit_lines, dynamic_orbit_lines)

        # Checking for events
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                    pygame.display.quit()
                    start_menu()
                    break
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_d:
                            Planet.TIMESTEP *= 1.0005
                        case pygame.K_a:
                            Planet.TIMESTEP *= 0.9995
                            print(Planet.TIMESTEP)
                        case pygame.K_w:
                            Planet.SCALE *= 1.0005
                            Planet.orbit_zoom_scale *= 1.0005
                            #for planet in planets:
                                #planet.scale_orbit(1.0005, dynamic_orbit_lines, sim_paused)
                            # for planet in planets:
                            #     for i in range(len(planet.orbit_points)):
                            #         planet.orbit_points[i] = (planet.orbit_points[i][0] / 1.0005, planet.orbit_points[i][1] / 1.0005)
                            # print(Planet.SCALE)
                        case pygame.K_s:
                            Planet.SCALE *= 0.9995
                            Planet.orbit_zoom_scale *= 0.9995
                            #for planet in planets:
                                    #planet.scale_orbit(0.9995, dynamic_orbit_lines, sim_paused)
                            
                            # for planet in planets:
                            #     for i in range(len(planet.orbit_points)):
                            #         planet.orbit_points[i] = (planet.orbit_points[i][0] / 1.0005, planet.orbit_points[i][1] / 1.0005)
                        case pygame.K_ESCAPE:
                            pause_menu.enable()
                            check_settings = True
                            pause_menu.mainloop(window)

                        # Controls to pan the screen
                        case pygame.K_DOWN:
                            Planet.displacement_y -= 1
                        case pygame.K_UP:
                            Planet.displacement_y += 1
                        case pygame.K_LEFT:
                            Planet.displacement_x += 1
                        case pygame.K_RIGHT:
                            Planet.displacement_x -= 1

                        case pygame.K_SPACE:
                            if last_paused + 0.3 < time.time():
                                last_paused = time.time()
                                sim_paused = not sim_paused

                        # Recentreing the solar system
                        case pygame.K_r:
                            Planet.displacement_x = 0
                            Planet.displacement_y = 0

        if check_settings:
            check_settings = False
            sim_settings = settings_menu.get_input_data() 
            show_fps = sim_settings["fps"]
            show_orbit_lines = sim_settings["orbits_lines"]
            dynamic_orbit_lines = sim_settings["dynamic_orbit"]
            show_images = sim_settings["images"]
            show_time = sim_settings["time"]
            if sim_settings["hover_colour"] != "":
                hover_colour = sim_settings["hover_colour"]

        '''Drawing Ui'''
        if show_fps:
            fps = clock.get_fps()
            fps_text = f"FPS: {round(fps, 2)}"
            fps_render = main_font.render(fps_text, True, (255, 255, 255))
            window.blit(fps_render, (10, 10))
        if show_time and fps != 0:
                time_text = f"Speed: {round(((Planet.TIMESTEP/(3600*24)) * fps), 2)} days per second"
                time_render = main_font.render(time_text, True, (255, 255, 255))
                window.blit(time_render, (10, 30))
        # Drawing buttons
        show_controls.draw_text(window)

        #Checking what the mouse is hovering over
        mouse_pos = pygame.mouse.get_pos()
        if show_controls.hovered(mouse_pos):
            show_controls.text_colour = hover_colour
        else:
            show_controls.text_colour = (255, 255, 255)

        pygame.display.update()

    return

# Running the main function
if __name__ == "__main__":
    main_sim()