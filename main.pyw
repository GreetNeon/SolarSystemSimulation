####################################################################################################
# Description: Main file for the project
# Dependencies: calculations.py, menu_GUI.py, transitions.py
# Author: Teon Green
# Current Bugs: None
####################################################################################################

# Importing the calculations module
import calculations
import pygame
import pickle as pkl
from transitions import start_menu
from simulation_helper import Planet, set_planets, Button, display_text
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
    mytheme = pm.Theme(background_color=pause_menu_image,
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
    # Creating the simulation settings menu
    sim_settings_menu = pm.Menu(title="Settings", width=resolution[0], height=resolution[1], theme=mytheme)
    # Creating the planet settibns menu
    planet_settings_menu = pm.Menu(title="Planet Settings", width=resolution[0], height=resolution[1], theme=mytheme)
    # Adding the widgets to the settings menus
    sim_settings_menu.add.toggle_switch("Show Fps", True, toggleswitch_id='fps')
    sim_settings_menu.add.toggle_switch("Show Zoom:", True, toggleswitch_id = "zoom")
    sim_settings_menu.add.toggle_switch("Show Images:", True, toggleswitch_id = "images")
    sim_settings_menu.add.toggle_switch("Show Sim Speed:", True, toggleswitch_id = "time")
    sim_settings_menu.add.toggle_switch("Show Orbit Lines:", True, toggleswitch_id = "orbits_lines")
    sim_settings_menu.add.toggle_switch("Dynamic Orbit Lines:", True, toggleswitch_id = "dynamic_orbit")

    sim_settings_menu.add.color_input('Button Hover Colour: ', color_type=pm.widgets.COLORINPUT_TYPE_RGB, default=(255, 0, 0), color_id='hover_colour')
    # Adding the widgets to the planet settings menu
    planet_settings_menu.add.range_slider("Relative Planet Scale:", 2, (1, 10), 1, rangeslider_id="planet_scale")
    planet_settings_menu.add.selector("Planet colours: ", [("Default", "default"), ("Greyscale", "greyscale"), ("Inverted", "inverted"), ("Fun", "fun")],selector_id="planet_colours")
    # Adding the widgets to the pause menu
    pause_menu.add.button("Resume", lambda: pause_menu.disable())
    pause_menu.add.button("Simulation Settings", sim_settings_menu)
    pause_menu.add.button("Planet Settings", planet_settings_menu)
    pause_menu.add.button("Exit to menu", lambda: start_menu())
    pause_menu.add.button("Exit to desktop", lambda: quit())

    pause_menu.disable()
    return pause_menu, sim_settings_menu, planet_settings_menu

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
    show_zoom = True
    show_controls = False
    dynamic_orbit_lines = True
    sim_paused = False
    last_paused = time.time()
    main_font = pygame.font.SysFont("Nevis", 20)
    larger_font = pygame.font.SysFont("Nevis", 40)
    hover_colour = (255, 0, 0)
    # Defining planets
    planets = set_planets()
    # Allows controls to be held down
    pygame.key.set_repeat(1)
    # Creating the window
    window = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Solar System Simulation")

    # Defining controls
    controls = ["W - Zoom In", "S - Zoom Out", "A - Decrease Speed", "D - Increase Speed",
                "Space - Pause/Unpause", "Arrow Keys - Pan Screen", "R - Recentre Solar System", "Esc - Pause Menu"]

    # Creating the pause menu
    pause_menu, sim_settings_menu, planet_settings_menu = create_pause_menu()
    # Creating in-game buttons
    show_controls_button = Button(screen_w * 0.92, screen_h * 0.01, "Show Controls", main_font)

    # Creating planet focus
    planet_focus = None
    Planet.planet_focused = False
    planet_hovered = False
    hovered_planet = None

    update_planet_points = False

    # Creating main loop
    while running:
        stats_displayed = 0
        mouse_pos = pygame.mouse.get_pos()
        window.fill((0, 0, 0))
        clock.tick(FPS)
        Planet.Paused = sim_paused
        # Updating the planets
        for planet in planets:
            if update_planet_points:
                planet.update_planet_points()
                if planet.name == "Pluto":
                    update_planet_points = False

            if planet.win is None:
                planet.set_window(window)
            if not sim_paused:
                planet.update_position(planets)
            planet.draw(show_orbit_lines, dynamic_orbit_lines, show_images)
            if planet.rect != None:
                if planet.rect.collidepoint(mouse_pos):
                    planet.hovered = True
                    planet_hovered = True
                    if not Planet.planet_focused:
                        planet_focus = planet
                    else:
                        hovered_planet = planet
                else:
                    if planet.hovered:
                        planet_hovered = False
                    planet.hovered = False
            
            # Outline planet if it being hovered over
            if planet.hovered is True:
                outline_radius = planet.adjusted_radius + screen_w * 0.01
                corrected_x = planet.scaled_x + Planet.correction_x
                corrected_y = planet.scaled_y + Planet.correction_y
                pygame.draw.circle(window, planet.colour, (corrected_x, corrected_y), outline_radius, 2)
                pygame.draw.line(window, planet.colour, (corrected_x + outline_radius - 1, corrected_y), (corrected_x + outline_radius + screen_w * 0.03, corrected_y), 2)
                display_text(window, planet.name, main_font, corrected_x + outline_radius + screen_w * 0.035, corrected_y - screen_h * 0.01, text_colour = planet.colour, scale = False)

        # Checking for events
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                    pygame.display.quit()
                    exit()
                    break
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_d:
                            Planet.TIMESTEP *= 1.0005
                            update_planet_points = True

                        case pygame.K_a:
                            Planet.TIMESTEP *= 0.9995
                            update_planet_points = True
                            print(planets[1].planets_points)

                        case pygame.K_w:
                            Planet.SCALE *= 1.0005
                            Planet.orbit_zoom_scale *= 1.0005

                        case pygame.K_s:
                            Planet.SCALE *= 0.9995
                            Planet.orbit_zoom_scale *= 0.9995

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

                case pygame.MOUSEBUTTONDOWN:
                    event_pos = pygame.mouse.get_pos()
                    if show_controls_button.hovered(event_pos):
                        show_controls = not show_controls
                        if show_controls:
                            show_controls_button.text = "Hide Controls"
                        else:
                            show_controls_button.text = "Show Controls"
                    if planet_hovered and not Planet.planet_focused:
                        Planet.planet_focused = True
                        print(Planet.planet_focused)

                    elif (planet_focus is not None and Planet.planet_focused and planet_focus.hovered):
                        Planet.planet_focused = False
                        Planet.displacement_x = 0
                        Planet.displacement_y = 0
                    elif (hovered_planet != planet_focus) and Planet.planet_focused and hovered_planet is not None:
                        planet_focus = hovered_planet
                    
        if planet_focus != None and hovered_planet != None:
            print(f'planet focused: {planet_focus.name}')
            print(f'planet hovered: {hovered_planet.name}')
        if check_settings:
            check_settings = False
            Planet.update_planet_sizes = True 
            Planet.update_planet_colours = True
            sim_settings = sim_settings_menu.get_input_data()
            planet_settings = planet_settings_menu.get_input_data()
            show_fps = sim_settings["fps"]
            show_orbit_lines = sim_settings["orbits_lines"]
            dynamic_orbit_lines = sim_settings["dynamic_orbit"]
            show_images = sim_settings["images"]
            show_time = sim_settings["time"]
            if sim_settings["hover_colour"] != "":
                hover_colour = sim_settings["hover_colour"]
            Planet.planet_size = planet_settings["planet_scale"]
            Planet.colour_mode = planet_settings["planet_colours"][0][1]

        '''Drawing Ui'''

        if show_fps:
            stats_displayed += 1
            fps = clock.get_fps()
            display_text(window, f"FPS: {round(fps, 2)}", main_font, screen_w * 0.005, screen_h * (0.01 + 0.025 * (stats_displayed - 1)), scale = False)
        if show_time and fps != 0:
            stats_displayed += 1
            display_text(window, f"Speed: {round(((Planet.TIMESTEP/(3600*24)) * fps), 2)} (Days Per Second)",
                            main_font, screen_w * 0.005, screen_h * (0.01 + 0.025 * (stats_displayed - 1)), scale = False)
        if show_zoom:
            stats_displayed += 1
            display_text(window, f'Zoom: {round((Planet.SCALE / Planet.DEFAULT_SCALE), 2)}x', main_font, screen_w * 0.005, screen_h * (0.01 + 0.025 * (stats_displayed - 1)), scale = False)
        if sim_paused:
            display_text(window, "Paused", larger_font, screen_w / 2, screen_h * 0.05, text_colour=(255, 0, 0))
        # Drawing buttons
        show_controls_button.draw_text(window)
        if show_controls:
            for i in range(len(controls)):
                display_text(window, controls[i], main_font, screen_w * 0.92, screen_h * 0.05 + (i * 20))

        #Checking what the mouse is hovering over
        if show_controls_button.hovered(mouse_pos):
            show_controls_button.text_colour = hover_colour
        else:
            show_controls_button.text_colour = (255, 255, 255)

        if Planet.planet_focused and (planet_focus is not None):
            temp_x, temp_y = planet_focus.orbit[-1]
            sun_x, sun_y = planets[0].orbit[-1]
            s_sun_x = sun_x * Planet.SCALE
            s_sun_y = sun_y * Planet.SCALE
            temp_x = temp_x * Planet.SCALE
            temp_y = temp_y * Planet.SCALE
            focus_x, focus_y = planet_focus.orbit_points[-1]
            diff_x = (screen_w/2) - focus_x
            diff_y = (screen_h/2) - focus_y
            Planet.correction_x = diff_x
            Planet.correction_y = diff_y
            Planet.displacement_x = (-temp_x)
            Planet.displacement_y = (-temp_y)
            print(f'focused planet x: {planet_focus.orbit_points[-1][0]}, y: {planet_focus.orbit_points[-1][1]} diff x: {diff_x} diff y: {diff_y}')
        else:
            Planet.correction_x = 0
            Planet.correction_y = 0

        pygame.display.update()

    return

# Running the main function
if __name__ == "__main__":
    main_sim()