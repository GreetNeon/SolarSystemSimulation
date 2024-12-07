from calculations import calculate_force, calculate_distance
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
    TIMESTEP = 3600*24 # 1 day
    planet_scale = 900000000
    planet_size = 2
    update_planet_size = True
    orbit_zoom_scale = 1
    displacement_x = 0
    displacement_y = 0
    MERCURY_COLOR = "#DCDBDB"
    VENUS_COLOR = "#F5E16F"
    EARTH_COLOR = "#79DDF2"
    MARS_COLOR = "#DD4C22"
    JUPITER_COLOR = "#F5CF7C"
    SATURN_COLOR = "#ab604a"
    URANUS_COLOR = "#7BBEF5"
    NEPTUNE_COLOR = "#4b70dd"
    PLUTO_COLOR = "#9ca6b7"
    YELLOW = "#ffff00"
    def __init__(self, x, y, radius, color, mass: float, name, planets_points):
            self.x = x
            self.y = y
            self.scaled_x = 0
            self.scaled_y = 0
            self.name = name
            self.radius = radius
            self.size = radius
            self.adjusted_radius = 0
            self.color = color
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

            # Change so that this is given when creating an object and each planet stores its own value
            self.planets_points = planets_points
            
            self.orbit_points = []
            self.update_size()

    def set_window(self, win):
        '''Set the window the planet is being drawn on'''
        self.win = win
        self.win_width, self.win_height = self.win.get_size()

    def update_size(self):
        '''Update the size of the planet'''
        if not self.sun:
            self.size = self.radius * self.planet_size

    '''This to scale the orbit of a planet when zooming, however, it is not used in the final version of the code'''
    # def scale_orbit(self, value, dynamic_orbit, paused):
    #     '''When zooming in or out, scale the orbit of the planet'''
    #     self.scaled_x = (value * self.scaled_x) - ((self.win_width / 2) * (value - 1))
    #     self.scaled_y = (value * self.scaled_y) - ((self.win_height / 2) * (value - 1))
    #     if dynamic_orbit:
    #         self.orbit_points = [(value * point[0] - ((self.win_width / 2) * (value - 1)) , value * point[1] - ((self.win_height / 2) * (value - 1))) for point in self.orbit_points]
    #     else:
    #         self.loaded_orbit = [(value * point[0] - ((self.win_width / 2) * (value - 1)) , value * point[1] - ((self.win_height / 2) * (value - 1))) for point in self.loaded_orbit]
    def draw(self, orbit_lines, dynamic_orbit):
        '''Draw the planet on the window'''
        if self.update_planet_size:
            self.update_size()
            if self.name == 'Pluto':
                self.update_planet_size = False
        if len(self.orbit) > self.planets_points:
            orbit = self.orbit[-self.planets_points:]
        else:
            orbit = self.orbit
        # Scale the points in the orbit to fit on the screen
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
        '''This code was used to save the orbit points of the planets to a file'''
        # if not self.orbit_saved:
        #     try:
        #         pkl.dump(orbit_points, open(f"data/OrbitPoints/{self.name}OrbitPoints.txt", "wb"))
        #     except FileNotFoundError:
        #         print("OrbitPoints file not found")
        #     self.orbit_saved = True
        #     print(f"Orbit points saved for {self.name}")
        # When switching from static to dynamic orbit, only keep the last point in the orbit
        if self.orbit != [] and self.orbit_refresh:
            current_position = self.orbit[-1]
            self.orbit.clear()
            self.orbit.append(current_position)
            self.orbit_refresh = False

        # Draw the orbit of the planet if there is more than 2 points in the orbit and the orbit lines are enabled
        if len(self.orbit_points) > 2 and orbit_lines and dynamic_orbit:
            pygame.draw.lines(self.win, self.color, False, self.orbit_points, 1)

        # If the orbit is not dynamic, draw the orbit of the planet as a circle
        elif not dynamic_orbit:
            # This will make the orbit refresh when switching to dynamic orbit
            if not self.orbit_refresh:
                self.orbit_refresh = True
            '''This code was used to load the orbit points of the planets from a file'''
            # if self.load_orbit:
            #     try:
            #         self.loaded_orbit = pkl.load(open(f"data/OrbitPoints/{self.name}OrbitPoints.txt", "rb"))
            #         self.load_orbit = False
            #     except FileNotFoundError:
            #         print("File not found")
            #         pass
            # if len(self.loaded_orbit) > 2:
            #     pygame.draw.lines(self.win, self.color, False, self.loaded_orbit, 1)
            # If the distance to centre is 0 or it hasn't been updated in 5 seconds, update it
            if self.distance_to_centre == 0 or (self.last_orbit_change + 5 < time.time() and not self.Paused):
                self.last_orbit_change = time.time()
                scaled_x = self.x * self.DEFAULT_SCALE + (self.win_width / 2) + self.displacement_x
                scaled_y = self.y * self.DEFAULT_SCALE + (self.win_height / 2) + self.displacement_y
                self.distance_to_centre = calculate_distance((scaled_x, scaled_y), self.SYSTEM_CENTER)[0]
            # Dont draw the orbit of the sun
            if not self.sun:
                pygame.draw.circle(self.win, self.color, self.SYSTEM_CENTER,
                                    self.distance_to_centre * self.orbit_zoom_scale, 1)

        # Draw the planet
        self.adjusted_radius = self.size * self.SCALE * self.planet_scale
        pygame.draw.circle(self.win, self.color, (x, y), self.adjusted_radius)

    def attraction(self, other:object):
        '''Calculate the force of attraction between 2 planets'''
        force_x, force_y, self.distance_to_sun = calculate_force(self, other, self.G)
        return force_x, force_y

    def update_position(self, planets:list):
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

        
def set_planets():
    '''Create all the planet objects'''
# A function to create all planet objects
    p_points = {"Sun": 10, "Mercury": 87, "Venus": 226, "Earth": 366, "Mars": 684, "Jupiter": 4350,
                "Saturn": 11000, "Uranus": 34000, "Neptune": 51000, "Pluto": 120000}
    sun = Planet(0, 0, 15, Planet.YELLOW, 1.98892 * 10 ** 30, "Sun", p_points["Sun"])
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 3.96, Planet.EARTH_COLOR, 5.9722 * 10 ** 24, "Earth", p_points["Earth"])
    earth.y_vel = 29.783 * 1000

    mars = Planet(-1.524 * Planet.AU, 0, 2.46, Planet.MARS_COLOR, 6.39 * 10 ** 23, "Mars", p_points["Mars"])
    mars.y_vel = 24.077 * 1000

    mercury = Planet(0.387 * Planet.AU, 0, 1.52, Planet.MERCURY_COLOR, 3.30 * 10 ** 23, "Mercury", p_points["Mercury"])
    mercury.y_vel = -47.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 3.76, Planet.VENUS_COLOR, 4.8685 * 10 ** 24, "Venus", p_points["Venus"])
    venus.y_vel = -35.02 * 1000

    # jupiter = Planet(5.2 * Planet.AU, 0, 20, Planet.JUPITER_COLOR, 1.898 * 10 ** 27, "Jupiter")
    jupiter = Planet(5.2 * Planet.AU, 0, 43.44, Planet.JUPITER_COLOR, 1.898 * 10 ** 27, "Jupiter", p_points["Jupiter"])
    jupiter.y_vel = -13.06 * 1000

    # saturn = Planet(9.5 * Planet.AU, 0, 16, Planet.SATURN_COLOR, 5.683 * 10 ** 26, "Saturn")
    saturn = Planet(9.5 * Planet.AU, 0, 36.18, Planet.SATURN_COLOR, 5.683 * 10 ** 26, "Saturn", p_points["Saturn"])
    saturn.y_vel = -9.68 * 1000

    # uranus = Planet(-19.8 * Planet.AU, 0, 12, Planet.URANUS_COLOR, 8.681 * 10 ** 25, "Uranus")
    uranus = Planet(-19.8 * Planet.AU, 0, 15.76, Planet.URANUS_COLOR, 8.681 * 10 ** 25, "Uranus", p_points["Uranus"])
    uranus.y_vel = 6.80 * 1000

    # neptune = Planet(30 * Planet.AU, 0, 12, Planet.NEPTUNE_COLOR, 102.409 * 10 ** 24, "Neptune")
    neptune = Planet(30 * Planet.AU, 0, 15.3, Planet.NEPTUNE_COLOR, 102.409 * 10 ** 24, "Neptune", p_points["Neptune"])
    neptune.y_vel = -5.43 * 1000

    # pluto = Planet(-39 * Planet.AU, 0, 2, Planet.PLUTO_COLOR, 0.01303 * 10 ** 24, "Pluto")
    pluto = Planet(-39 * Planet.AU, 0, 1.48, Planet.PLUTO_COLOR, 0.01303 * 10 ** 24, "Pluto", p_points["Pluto"])
    pluto.y_vel = 4.67 * 1000

    planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, pluto]
    return planets

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