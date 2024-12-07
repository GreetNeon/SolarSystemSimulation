from simulation_helper import *
import pygame

planets = set_planets()
win = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# One planet at a time
starting_y = None
while True:
    clock.tick(60)
    win.fill((0, 0, 0))
    
    for planet in planets:
        pygame.key.set_repeat(1, 1)
        # Mercury Planet points : 87
        #if planet.name == "Mercury":
            #print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
        # Venus Planet points : 226
        #if planet.name == "Venus":
            #print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
        # Earth Planet points : 366
        # if planet.name == "Earth":
        #     print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
        #     if len(planet.orbit_points) == 1:
        #         starting_y = planet.scaled_y
        # Mars Planet points : 684
        # if planet.name == "Mars":
        #     print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
        #     if len(planet.orbit_points) == 1:
        #         starting_y = planet.scaled_y
        # Jupiter Planet points : 
        # if planet.name == "Jupiter":
        #     print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
        #     if len(planet.orbit_points) == 1:
        #         starting_y = planet.scaled_y
        # Saturn Planet points : 
        # if planet.name == "Saturn":
        #     print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
        #     if len(planet.orbit_points) == 1:
        #         starting_y = planet.scaled_y
        # Uranus Planet points : 
        if planet.name == "Uranus":
            print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
            if len(planet.orbit_points) == 1:
                starting_y = planet.scaled_y
        # Neptune Planet points :
        # if planet.name == "Neptune":
        #     print(f'Y: {planet.scaled_y} Length: {len(planet.orbit_points)}')
        #     if len(planet.orbit_points) == 1:
        #         starting_y = planet.scaled_y
        
        if planet.win is None:
            planet.set_window(win)
        planet.update_position(planets)
        planet.draw(win, True)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print(f'Starting Y: {starting_y}')
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_w:
                        Planet.SCALE *= 1.005
                        Planet.orbit_zoom_scale *= 1.005
                    case pygame.K_s:
                        Planet.SCALE /= 1.005
                        Planet.orbit_zoom_scale /= 1.005
    pygame.display.update()