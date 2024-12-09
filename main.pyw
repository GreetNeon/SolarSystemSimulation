#########################################################################################################################
# Description: Main file for the project
# Dependencies: calculations.py, menu_GUI.py, transitions.py, simulation_helper.py, pygame, pickle, pygame_menu
# Author: Teon Green
# Current Bugs: None
#########################################################################################################################

# Importing the necessary modules
import pygame
import pickle as pkl
from transitions import start_menu
from simulation_helper import Planet, set_planets, Button, display_text
import pygame_menu as pm
import time

pygame.init()
# Loading the settings
settings_file = open("data/settings.txt", "rb")
settings = pkl.load(settings_file)
settings_file.close()
resolution = settings["resolution"][0][1]
graphics = settings["graphics"][0][1]
# Defining the graphics settings
graphics_dict = {'low': {'show_orbit_lines': False, 'show_fps': True, 'show_images': False, 'show_time': True, 'show_zoom': True, 'dynamic_orbit_lines': False},
                'medium': {'show_orbit_lines': True, 'show_fps': True, 'show_images': False, 'show_time': True, 'show_zoom': True, 'dynamic_orbit_lines': False},
                'high': {'show_orbit_lines': True, 'show_fps': True, 'show_images': True, 'show_time': True, 'show_zoom': True, 'dynamic_orbit_lines': False},
                'ultra high': {'show_orbit_lines': True, 'show_fps': True, 'show_images': True, 'show_time': True, 'show_zoom': True, 'dynamic_orbit_lines': True}}
show_orbit_lines = graphics_dict[graphics]["show_orbit_lines"]
show_fps = graphics_dict[graphics]["show_fps"]
show_images = graphics_dict[graphics]["show_images"]
show_time = graphics_dict[graphics]["show_time"]
show_zoom = graphics_dict[graphics]["show_zoom"]
dynamic_orbit_lines = graphics_dict[graphics]["dynamic_orbit_lines"]

def create_pause_menu():
    # Creating the pause menu
    pause_menu_image = pm.baseimage.BaseImage(image_path="gfx/pause_background.png", drawing_mode=pm.baseimage.IMAGE_MODE_FILL)
    # Creating the theme for the menus
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
    sim_settings_menu.add.toggle_switch("Show Fps:", show_fps, toggleswitch_id='fps')
    sim_settings_menu.add.toggle_switch("Show Zoom:", show_zoom, toggleswitch_id = "zoom")
    sim_settings_menu.add.toggle_switch("Show Images:", show_images, toggleswitch_id = "images")
    sim_settings_menu.add.toggle_switch("Show Sim Speed:", show_time, toggleswitch_id = "time")
    sim_settings_menu.add.toggle_switch("Show Orbit Lines:", show_orbit_lines, toggleswitch_id = "orbits_lines")
    sim_settings_menu.add.toggle_switch("Dynamic Orbit Lines:", dynamic_orbit_lines, toggleswitch_id = "dynamic_orbit")
    sim_settings_menu.add.color_input('Button Hover Colour: ', color_type=pm.widgets.COLORINPUT_TYPE_RGB, default=(255, 0, 0), color_id='hover_colour')
    # Adding the widgets to the planet settings menu
    planet_settings_menu.add.label('''Disclaimer!: Changing the planet scale will not affect the
orbits of the planets but is likely to make them overlap.''')
    planet_settings_menu.add.range_slider("Relative Planet Scale:", 1, (1, 10), 1, rangeslider_id="planet_scale")
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
    # Defining controls
    controls = ["W - Zoom In", "S - Zoom Out", "A - Decrease Speed", "D - Increase Speed",
                "Space - Pause/Unpause", "Arrow Keys - Pan Screen", "R - Recentre Solar System", "Esc - Pause Menu"]
    # Defining the main variables
    global show_orbit_lines, show_fps, show_images, show_time, show_zoom, dynamic_orbit_lines
    FPS = 90
    clock = pygame.time.Clock()
    running = True
    check_settings = False
    screen_w = resolution[0]
    screen_h = resolution[1]
    show_controls = False
    sim_paused = False
    last_paused = time.time()
    main_font = pygame.font.SysFont("Nevis", 20)
    larger_font = pygame.font.SysFont("Nevis", 40)
    hover_colour = (255, 0, 0)
    planet_focus = None
    Planet.planet_focused = False
    planet_hovered = False
    hovered_planet = None
    update_planet_points = False
    show_planet_focus = False
    planet_focus_buttons_created = False
    # Defining planets
    planets, moons = set_planets()
    # Allows controls to be held down
    pygame.key.set_repeat(1)
    # Creating the window
    window = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Solar System Simulation")
    # Creating the pause menu
    pause_menu, sim_settings_menu, planet_settings_menu = create_pause_menu()
    # Creating in-game buttons
    show_controls_button = Button(screen_w * 0.92, screen_h * 0.01, "Show Controls", main_font)
    show_planet_focus_button = Button(screen_w * 0.065, screen_h * 0.65, "Show Planets To Focus", main_font)
    # Creating main loop
    while running:
        # Defining loop variables
        zoom = round((Planet.SCALE / Planet.DEFAULT_SCALE), 2)
        stats_displayed = 0
        mouse_pos = pygame.mouse.get_pos()
        Planet.Paused = sim_paused
        # Clearing the window
        window.fill((0, 0, 0))
        # Setting the frame rate
        clock.tick(FPS)

        '''Drawing the simulation'''
        # Updating the planets
        for planet in planets:
            # Updating the number of points in a planets orbit
            if update_planet_points:
                planet.update_planet_points()
                if planet.name == "Pluto":
                    update_planet_points = False
            # Setting the window for the planet
            if planet.win is None:
                planet.set_window(window)
            # Updating the position of the planet if the simulation is not paused
            if not sim_paused:
                planet.update_position(planets, dynamic_orbit_lines)
            # Drawing the planet
            planet.draw(show_orbit_lines, dynamic_orbit_lines, show_images)
            # Checking if the mouse is hovering over the planet
            if planet.rect != None:
                if planet.rect.collidepoint(mouse_pos):
                    planet.hovered = True
                    planet_hovered = True
                    # Setting the planet to be focused if it is clicked on
                    if not Planet.planet_focused:
                        planet_focus = planet
                    else:
                        hovered_planet = planet
                else:
                    if planet.hovered:
                        planet_hovered = False
                    planet.hovered = False
            # Drawing the outline of the planet if it is hovered over
            if planet.hovered is True:
                outline_radius = planet.adjusted_radius + screen_w * 0.01
                corrected_x = planet.scaled_x + Planet.correction_x
                corrected_y = planet.scaled_y + Planet.correction_y
                pygame.draw.circle(window, planet.colour, (corrected_x, corrected_y), outline_radius, 2)
                pygame.draw.line(window, planet.colour, (corrected_x + outline_radius - 1, corrected_y), (corrected_x + outline_radius + screen_w * 0.03, corrected_y), 2)
                display_text(window, planet.name, main_font, corrected_x + outline_radius + screen_w * 0.035, corrected_y - screen_h * 0.01, text_colour = planet.colour, scale = False)
        # Updating the moons
        for moon in moons:
            # Setting the window for the moon
            if moon.win is None:
                moon.set_window(window)
            # Updating the position of the moon if the simulation is not paused
            if not sim_paused:
                moon.update_position()
            # Drawing the moon
            moon.draw()            

        '''Event Handling'''
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                    pygame.display.quit()
                    exit()
                    break
                case pygame.KEYDOWN:
                    # Game controls
                    match event.key:
                        case pygame.K_d:
                            Planet.TIMESTEP *= 1.0005
                            update_planet_points = True

                        case pygame.K_a:
                            Planet.TIMESTEP *= 0.9995
                            update_planet_points = True

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
                    # Checking if the mouse is hovering over the show controls button
                    if show_controls_button.hovered(event_pos):
                        show_controls = not show_controls
                        if show_controls:
                            show_controls_button.text = "Hide Controls"
                        else:
                            show_controls_button.text = "Show Controls"
                    # Checking if the mouse is hovering over the focus planet button
                    if show_planet_focus_button.hovered(event_pos):
                        show_planet_focus = not show_planet_focus
                        if show_planet_focus:
                            show_planet_focus_button.text = "Hide Planets To Focus"
                        else:
                            show_planet_focus_button.text = "Show Planets To Focus"
                    if show_planet_focus and planet_focus_buttons_created:
                        for key in planet_focus_buttons:
                            if planet_focus_buttons[key][0].hovered(event_pos):
                                if not planet_focus_buttons[key][1].focused:
                                    if planet_focus is not None:
                                        planet_focus.focused = False
                                    planet_focus = planet_focus_buttons[key][1]
                                    Planet.planet_focused = True
                                    planet_focus.focused = True
                                elif planet_focus_buttons[key][1] != planet_focus:
                                    planet_focus.focused = False
                                    planet_focus = planet_focus_buttons[key][1]
                                else:
                                    planet_focus.focused = False
                                    planet_focus = None
                                
                    # Checking if the user has clicked on a planet
                    if planet_hovered and not Planet.planet_focused:
                        Planet.planet_focused = True
                    # Checking if the user has clicked on the focused planet, unfocusing it
                    elif (planet_focus is not None and Planet.planet_focused and planet_focus.hovered):
                        Planet.planet_focused = False
                        planet_focus.focused = False
                        Planet.displacement_x = 0
                        Planet.displacement_y = 0
                    # Checking if the user has clicked on a different planet
                    elif (hovered_planet != planet_focus) and Planet.planet_focused and hovered_planet is not None:
                        planet_focus.focused = False
                        planet_focus = hovered_planet
                    
        '''Changing the settings'''
        if check_settings:
            check_settings = False
            Planet.update_planet_sizes = True 
            Planet.update_planet_colours = True
            # Getting the settings from the settings menus
            sim_settings = sim_settings_menu.get_input_data()
            planet_settings = planet_settings_menu.get_input_data()
            show_fps = sim_settings["fps"]
            show_orbit_lines = sim_settings["orbits_lines"]
            dynamic_orbit_lines = sim_settings["dynamic_orbit"]
            show_images = sim_settings["images"]
            show_time = sim_settings["time"]
            # Exception handling for the hover colour
            if sim_settings["hover_colour"] != "":
                hover_colour = sim_settings["hover_colour"]
            Planet.planet_size = planet_settings["planet_scale"]
            Planet.colour_mode = planet_settings["planet_colours"][0][1]

        '''Simulation Ui'''
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
            display_text(window, f'Zoom: {zoom}x', main_font, screen_w * 0.005, screen_h * (0.01 + 0.025 * (stats_displayed - 1)), scale = False)
        if sim_paused:
            display_text(window, "Paused", larger_font, screen_w / 2, screen_h * 0.05, text_colour=(255, 0, 0))
        # Drawing buttons
        show_controls_button.draw_text(window)
        show_planet_focus_button.draw_text(window)
        if show_controls:
            for i in range(len(controls)):
                display_text(window, controls[i], main_font, screen_w * 0.92, screen_h * 0.05 + (i * 20))
        if show_planet_focus:
            if not planet_focus_buttons_created:
                planet_focus_buttons_created = True
                planet_focus_buttons = {}
                for i in range(len(planets)):
                    temp_button = Button(screen_w * 0.065, screen_h * 0.6875 + (i * 20), planets[i].name, main_font)
                    planet_focus_buttons[planets[i].name] = [temp_button, planets[i]]
                for key in planet_focus_buttons:
                    planet_focus_buttons[key][0].draw_text(window)
                    if planet_focus_buttons[key][0].hovered(mouse_pos):
                        planet_focus_buttons[key][0].text_colour = hover_colour
                    else:
                        planet_focus_buttons[key][0].text_colour = (255, 255, 255)
            else:
                for i in range(len(planets)):
                    planet_focus_buttons[planets[i].name][0].draw_text(window)
                    if planet_focus_buttons[planets[i].name][0].hovered(mouse_pos):
                        planet_focus_buttons[planets[i].name][0].text_colour = hover_colour
                    else:
                        planet_focus_buttons[planets[i].name][0].text_colour = (255, 255, 255)

        #Checking what the mouse is hovering over
        if show_controls_button.hovered(mouse_pos):
            show_controls_button.text_colour = hover_colour
        else:
            show_controls_button.text_colour = (255, 255, 255)

        if show_planet_focus_button.hovered(mouse_pos):
            show_planet_focus_button.text_colour = hover_colour
        else:
            show_planet_focus_button.text_colour = (255, 255, 255)

        if Planet.planet_focused and (planet_focus is not None):
            planet_focus.focused = True
            temp_x, temp_y = planet_focus.orbit[-1]
            temp_x = temp_x * Planet.SCALE
            temp_y = temp_y * Planet.SCALE
            focus_x, focus_y = planet_focus.orbit_points[-1]
            diff_x = (screen_w/2) - focus_x
            diff_y = (screen_h/2) - focus_y
            Planet.correction_x = diff_x
            Planet.correction_y = diff_y
            Planet.displacement_x = (-temp_x)
            Planet.displacement_y = (-temp_y)
        else:
            Planet.correction_x = 0
            Planet.correction_y = 0

        pygame.display.update()

    return


# Running the main function
if __name__ == "__main__":
    main_sim()