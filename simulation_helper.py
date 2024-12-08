from calculations import calculate_force, calculate_distance, calculate_xy
import pygame
import pickle as pkl
import time

class Button:
    def __init__(self, x, y, text, font, width = None, height = None, text_colour = (255, 255, 255)):
        self.x = x
        self.y = y
        self.scaled_x = 0
        self.scaled_y = 0
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.text_colour = text_colour

    # Draw the button
    def draw_text(self, win):
        self.scaled_x, self.scaled_y, self.width, self.height = display_text(win, self.text, self.font, self.x,
                                                                            self.y, self.text_colour, rtrn = True)

    # Check if the mouse is hovering over the button
    def hovered(self, point):
        if self.width != None and self.height != None:
            return pygame.Rect(self.scaled_x, self.scaled_y, self.width, self.height).collidepoint(point)
        else:
            return False

class Planet:
    SYSTEM_CENTER = (0, 0)
    Paused = False
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 210 / AU  # 1AU = 100 pixels
    DEFAULT_SCALE = 210 / AU  # Should remain constant
    SCALE_CHANGE = 1
    DEFAULT_TIMESTEP = 3600*24 # 1 day
    TIMESTEP = 3600*24 # 1 day
    planet_scale = 900000000
    planet_size = 1
    update_planet_sizes = True
    update_planet_colours = True
    colour_mode = "default"
    orbit_zoom_scale = 1
    displacement_x = 0
    displacement_y = 0
    correction_x = 0
    correction_y = 0
    planet_focused  = False
    def __init__(self, x, y, radius, colours, mass: float, name, planets_points):
            self.x = x
            self.y = y
            self.scaled_x = 0
            self.scaled_y = 0
            self.name = name
            self.radius = radius
            self.size = radius
            self.adjusted_radius = 0
            self.colours = colours
            self.colour = None
            self.update_colour()
            self.mass = mass

            self.orbit = []
            self.sun = False
            self.distance_to_sun = 0
            self.distance_to_centre = 0

            self.x_vel = 0
            self.y_vel = 0
            self.win = None

            self.orbit_saved = False
            self.load_orbit = True
            self.loaded_orbit = []
            self.orbit_refresh = False
            self.last_orbit_change = 0
            self.rect = None
            self.hovered = False
            self.focused = False

            # Change so that this is given when creating an object and each planet stores its own value
            self.planets_points = planets_points
            self.default_planets_points = planets_points
            
            self.orbit_points = []
            self.update_size()
            self.image = None

    def set_window(self, win):
        '''Set the window the planet is being drawn on'''
        self.win = win
        self.win_width, self.win_height = self.win.get_size()

    def update_size(self):
        '''Update the size of the planet'''
        if not self.sun:
            self.size = self.radius * self.planet_size

    def update_colour(self):
        '''Update the colour of the planet'''
        self.colour = self.colours[self.colour_mode]

    def update_planet_points(self):
        '''Update the number of points in the orbit'''
        self.planets_points = int(round(self.default_planets_points * (self.DEFAULT_TIMESTEP/self.TIMESTEP)))

    def draw(self, orbit_lines, dynamic_orbit, show_images):
        '''Draw the planet on the window'''
        if self.update_planet_sizes:
            self.update_size()
            if self.name == 'Pluto':
                self.update_planet_sizes = False
        if self.update_planet_colours:
            self.update_colour()

        if len(self.orbit) > self.planets_points:
            orbit = self.orbit[-self.planets_points:]
        else:
            orbit = self.orbit
        # Scale the points in the orbit to fit on the screen
        if dynamic_orbit:
            self.orbit_points = [(point[0] * self.SCALE + (self.win_width / 2) + self.displacement_x,
                            point[1] * self.SCALE + (self.win_height / 2) + self.displacement_y) for point in orbit]
        x, y = self.orbit_points[-1]
        # Set important class atributes
        self.scaled_x = x
        self.scaled_y = y
        self.rect = pygame.Rect(x - self.adjusted_radius - 10, y - self.adjusted_radius - 10, (self.adjusted_radius * 2) + 10, (self.adjusted_radius * 2) + 10)
        # Set the center of the system to the sun
        if self.sun:
            Planet.SYSTEM_CENTER = (x, y)
        # When switching from static to dynamic orbit, only keep the last point in the orbit
        if self.orbit != [] and self.orbit_refresh:
            current_position = self.orbit[-1]
            self.orbit.clear()
            self.orbit.append(current_position)
            self.orbit_refresh = False

        # Draw the orbit of the planet if there is more than 2 points in the orbit and the orbit lines are enabled
        if len(self.orbit_points) > 2 and orbit_lines and dynamic_orbit:
            pygame.draw.lines(self.win, self.colour, False, self.orbit_points, 1)

        # If the orbit is not dynamic, draw the orbit of the planet as a circle
        elif not dynamic_orbit:
            # This will make the orbit refresh when switching to dynamic orbit
            if not self.orbit_refresh:
                self.orbit_refresh = True
            # If the distance to centre is 0 or it hasn't been updated in 5 seconds, update it
            if self.distance_to_centre == 0 or (self.last_orbit_change + 5 < time.time() and not self.Paused and not self.planet_focused):
                self.last_orbit_change = time.time()
                scaled_x = self.x * self.DEFAULT_SCALE + (self.win_width / 2) + self.displacement_x
                scaled_y = self.y * self.DEFAULT_SCALE + (self.win_height / 2) + self.displacement_y
                self.distance_to_centre = calculate_distance((scaled_x, scaled_y), self.SYSTEM_CENTER)[0]
            # Dont draw the orbit of the sun
            if not self.sun:
                pygame.draw.circle(self.win, self.colour, self.SYSTEM_CENTER,
                                    self.distance_to_centre * self.orbit_zoom_scale, 1)

        # Draw the planet
        self.adjusted_radius = self.size * self.SCALE * self.planet_scale
        # Dont draw unless its in the window
        if self.rect.colliderect(self.win.get_rect()):
            if show_images and self.name != 'Earth Moon':
                self.image = pygame.transform.scale(pygame.image.load(f'gfx/{self.name}.png').convert_alpha(), (int(self.adjusted_radius * 2), int(self.adjusted_radius * 2)))
                self.win.blit(self.image, (x - self.adjusted_radius + self.correction_x, y - self.adjusted_radius + self.correction_y))
            else:
                pygame.draw.circle(self.win, self.colour, (x + self.correction_x, y + self.correction_y), self.adjusted_radius)

    def attraction(self, other:object):
        '''Calculate the force of attraction between 2 planets'''
        force_x, force_y, self.distance_to_sun = calculate_force(self, other, self.G)
        return force_x, force_y

    def update_position(self, planets:list, dynamic_orbit):
        '''Update the position of the planet'''
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))
        if not dynamic_orbit:
            scaled_x, scaled_y = self.x * self.SCALE + (self.win_width / 2) + self.displacement_x, self.y * self.SCALE + (self.win_height / 2) + self.displacement_y
            self.orbit_points.append((scaled_x, scaled_y))

class Moon(Planet):
    def __init__(self, dist_from_parent, radius, parent, colours, mass, name, orbit_period, win = None):
        self.parent = parent
        self.orbit_points = []
        self.orbit = []
        self.displacement_x = 0
        self.displacement_y = 0
        self.distance_to_parent = ((parent.radius * self.planet_scale) + (dist_from_parent * 10)) * self.DEFAULT_SCALE
        self.orbit_period = orbit_period * 24 * 3600
        self.theta = 0
        super().__init__(parent.x + self.distance_to_parent, parent.y, radius, colours, mass, name, 100)
        

    def update_position(self):
        #idea: Let earth be the sun for the moon, and calculate the force of attraction between the moon and the earth, based on
        #the scaled positions of the moon and the earth
        # Easier idea: make the moon do a circle around its parent planet
        x, y = calculate_xy(self.distance_to_parent, self.theta)
        p_x, p_y = self.parent.orbit_points[-1]
        self.x = p_x + (x * (self.SCALE / self.DEFAULT_SCALE))
        self.y = p_y + (y * (self.SCALE / self.DEFAULT_SCALE))
        self.orbit_points.append((self.x, self.y))
        self.theta += self.TIMESTEP/self.orbit_period

    def draw(self):
        if self.update_planet_colours:
            self.update_colour()
            if self.name == 'Titania':
                self.update_planet_colours = False
        temp_x, temp_y = self.parent.orbit_points[-1]
        diff_x = (self.win_width/2) - temp_x
        diff_y = (self.win_height/2) - temp_y
        
        if self.parent.focused and not self.Paused:
            self.scaled_x = self.x + diff_x
            self.scaled_y = self.y + diff_y
            print(f'scaled x: {self.scaled_x} scaled y: {self.scaled_y}')
            print(f'diff x: {diff_x} diff y: {diff_y}')
            pygame.draw.circle(self.win, self.colour, (self.scaled_x, self.scaled_y), self.radius * self.SCALE * self.planet_scale * self.planet_size)
        else:
            pygame.draw.circle(self.win, self.colour, (self.x, self.y), self.radius * self.SCALE * self.planet_scale * self.planet_size)

        
def set_planets():
    '''Create all the planet objects'''
# A function to create all planet objects
    p_points = {"Sun": 10, "Mercury": 87, "Venus": 226, "Earth": 366, "Mars": 684, "Jupiter": 4350,
                "Saturn": 11000, "Uranus": 34000, "Neptune": 51000, "Pluto": 120000}
    all_colours = {
        "Sun": {"default": "#ffff00", "greyscale": "#BEBEBE", "inverted": "#0000FF", "fun": "#FF4500"},
        "Mercury": {"default": "#DCDBDB", "greyscale": "#A9A9A9", "inverted": "#2324E4", "fun": "#FF69B4"},
        "Venus": {"default": "#F5E16F", "greyscale": "#D3D3D3", "inverted": "#0A1E90", "fun": "#FFD700"},
        "Earth": {"default": "#79DDF2", "greyscale": "#808080", "inverted": "#86220D", "fun": "#00FF00"},
        "Mars": {"default": "#DD4C22", "greyscale": "#696969", "inverted": "#22B3DD", "fun": "#FF6347"},
        "Jupiter": {"default": "#F5CF7C", "greyscale": "#A9A9A9", "inverted": "#0A3083", "fun": "#FF8C00"},
        "Saturn": {"default": "#ab604a", "greyscale": "#D3D3D3", "inverted": "#549FB5", "fun": "#FF00FF"},
        "Uranus": {"default": "#7BBEF5", "greyscale": "#808080", "inverted": "#84410A", "fun": "#00FFFF"},
        "Neptune": {"default": "#4b70dd", "greyscale": "#696969", "inverted": "#B48F22", "fun": "#1E90FF"},
        "Pluto": {"default": "#9ca6b7", "greyscale": "#BEBEBE", "inverted": "#635948", "fun": "#FF1493"},
        'Moon': {"default": "#808080", "greyscale": "#818181", "inverted": "#FFFFFF", "fun": "#F3A8C2"}
    }
    
    sun = Planet(0, 0, 15, all_colours["Sun"], 1.98892 * 10 ** 30, "Sun", p_points["Sun"])
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 6.38, all_colours["Earth"], 5.9722 * 10 ** 24, "Earth", p_points["Earth"])
    earth.y_vel = 29.783 * 1000

    mars = Planet(-1.524 * Planet.AU, 0, 3.39, all_colours["Mars"], 6.39 * 10 ** 23, "Mars", p_points["Mars"])
    mars.y_vel = 24.077 * 1000

    mercury = Planet(0.387 * Planet.AU, 0, 2.44, all_colours["Mercury"], 3.30 * 10 ** 23, "Mercury", p_points["Mercury"])
    mercury.y_vel = -47.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 6.05, all_colours["Venus"], 4.8685 * 10 ** 24, "Venus", p_points["Venus"])
    venus.y_vel = -35.02 * 1000

    jupiter = Planet(5.2 * Planet.AU, 0, 69.91, all_colours["Jupiter"], 1.898 * 10 ** 27, "Jupiter", p_points["Jupiter"])
    jupiter.y_vel = -13.06 * 1000

    saturn = Planet(9.5 * Planet.AU, 0, 58.23, all_colours["Saturn"], 5.683 * 10 ** 26, "Saturn", p_points["Saturn"])
    saturn.y_vel = -9.68 * 1000

    uranus = Planet(-19.8 * Planet.AU, 0, 25.36, all_colours["Uranus"], 8.681 * 10 ** 25, "Uranus", p_points["Uranus"])
    uranus.y_vel = 6.80 * 1000

    neptune = Planet(30 * Planet.AU, 0, 24.6, all_colours["Neptune"], 102.409 * 10 ** 24, "Neptune", p_points["Neptune"])
    neptune.y_vel = -5.43 * 1000

    pluto = Planet(-39 * Planet.AU, 0, 1.18, all_colours["Pluto"], 0.01303 * 10 ** 24, "Pluto", p_points["Pluto"])
    pluto.y_vel = 4.67 * 1000

    earth_moon = Moon(0.00257 * Planet.AU, 1.74, earth, all_colours["Moon"], 7.342 * 10 ** 22, "Moon", 27.3)
    
    jupiter_ganymede = Moon(0.00715 * Planet.AU, 2.63, jupiter, all_colours["Moon"], 1.4819 * 10 ** 23, "Ganymede", 7.2)

    saturn_titan = Moon(0.00817 * Planet.AU, 2.58, saturn, all_colours["Moon"], 1.3452 * 10 ** 23, "Titan", 15.95)

    jupiter_callisto = Moon(0.01257 * Planet.AU, 2.41, jupiter, all_colours["Moon"], 1.075938 * 10 ** 23, "Callisto", 16.7)

    jupiter_io = Moon(0.00282 * Planet.AU, 1.82, jupiter, all_colours["Moon"], 8.931938 * 10 ** 22, "Io", 1.8)

    jupiter_europa = Moon(0.00448 * Planet.AU, 1.56, jupiter, all_colours["Moon"], 4.799844 * 10 ** 22, "Europa", 3.5)

    neptune_triton = Moon(0.00237 * Planet.AU, 1.35, neptune, all_colours["Moon"], 2.14 * 10 ** 22, "Triton", 5.9)

    uranus_titania = Moon(0.00289 * Planet.AU, 0.79, uranus, all_colours["Moon"], 3.527 * 10 ** 21, "Titania", 8.7)

    planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, pluto]
    moons = [earth_moon, jupiter_ganymede, saturn_titan, jupiter_callisto, jupiter_io, jupiter_europa, neptune_triton, uranus_titania]
    return planets, moons

def display_text(win, text, font, x, y, text_colour = (255, 255, 255), rtrn = False, scale = True):
    '''Display text on the window'''
    render = font.render(text, True, text_colour)
    width, height = render.get_size()
    scaled_x = x - width / 2
    scaled_y = y - height / 2
    if scale:
        win.blit(render, (scaled_x, scaled_y))
    else:
        win.blit(render, (x, y))
    if rtrn:
        return scaled_x, scaled_y, width, height