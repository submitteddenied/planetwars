'''
Created on 23/03/2011

@author: Michael Jensen
'''
import sys
import pygame
from pygame.locals import *

from Players import *
from PlanetWars import PlanetWars
from PlanetWarsProxy import PlanetWarsProxy
from Players.ScoutPlayer import ScoutPlayer
from Players.VariableAggressionPlayer import VariableAggressionPlayer

GAME_SIZE = (500,500)
SCREEN_SIZE = (3*GAME_SIZE[0], GAME_SIZE[1])
COLOUR = {"0": (200, 200, 200),
          "1": (255, 0, 0),
          "2": (0, 0, 255),
          "3": (0, 255, 0)}
PLANET_MIN_R = 0.85
PLANET_FACTOR = 0.05
MARGIN = 20
DISPLAY = True

def draw(world, screen, background=None, offset=(0,0)):
    display_size = [screen.get_size()[0] - (MARGIN * 2), screen.get_size()[1] - (MARGIN * 2)]
    display_offset = [offset[0] + MARGIN, offset[1] + MARGIN]
    e = world._Extent()
    world_width = e[1] - e[3]
    world_height = e[0] - e[2]
    world_offset = [0, 0]
    if(e[3] < 0):
        world_offset[0] = abs(e[3])
    if(e[2] < 0):
        world_offset[1] = abs(e[2])
    world_r = float(world_width) / float(world_height)
    screen_r = float(display_size[0]) / float(display_size[1])
    if world_r > screen_r:
        display_size[1] = display_size[0] / world_r
        dy = screen.get_size()[1] - (display_size[1] + (MARGIN * 2))
        display_offset[1] += int(dy / 2.0)
    else:
        display_size[0] = display_size[1] * world_r
        dx = screen.get_size()[0] - (display_size[0] + (MARGIN * 2))
        display_offset[0] += int(dx / 2.0)
    
    factor = (float(display_size[0]) / float(world_width))
    surf = pygame.Surface(display_size)
    if(background):
        surf.blit(background, (0,0))
    has_fog = world.PlayerID() != 0
    fog = pygame.Surface(display_size, flags=SRCALPHA)
    fog.fill((128,128,128,0))
    
    for p in world.Planets():
        screen_x = int((float(p.X() + world_offset[0]) / world_width) * display_size[0])
        screen_y = int((float(p.Y() + world_offset[1]) / world_height) * display_size[1])
        radius = int((PLANET_MIN_R * factor) + ((PLANET_FACTOR * factor) * p.GrowthRate()))
        pygame.draw.circle(surf, COLOUR[p.Owner()], (screen_x, screen_y), radius)
        if((p.Owner() == world.PlayerID()) and has_fog):
            pygame.draw.circle(fog, (0,0,0,0), (screen_x, screen_y), int(p.VisionRange() * factor))
        text = pygame.font.Font(None, 20).render(str(p.NumShips()), False, (0,0,0))
        text_pos = (screen_x - (text.get_width() / 2), screen_y - (text.get_height() / 2))
        surf.blit(text, text_pos)
        pid = pygame.font.Font(None, 18).render(str(p.ID()), False, (255,255,255))
        surf.blit(pid, (screen_x - radius, screen_y - radius))
        
    for f in world.Fleets():
        text = pygame.font.Font(None, 16).render(str(f.NumShips()), False, COLOUR[f.Owner()])
        screen_x = int((float(f.X() + world_offset[0]) / world_width) * display_size[0])
        screen_y = int((float(f.Y() + world_offset[1]) / world_height) * display_size[1])
        text_pos = (screen_x - (text.get_width() / 2), screen_y - (text.get_height() / 2))
        surf.blit(text, text_pos)
        if((f.Owner() == world.PlayerID()) and has_fog):
            pygame.draw.circle(fog, (0,0,0,0), (screen_x, screen_y), int(f.VisionRange() * factor))
    
    if(has_fog):
        surf.blit(fog, (0,0), special_flags=BLEND_SUB);
    #output the current tick
    surf.blit(pygame.font.Font(None, 22).render(str(world.CurrentTick()), False, (255,255,255)), (20, 20))
    screen.blit(surf, display_offset)
    pygame.display.update()
    

def do_game(game_id, logger, p1, p2, pw, show_gui=False, max_game_length=500):
    #we want to:
    #  - Load the map
    #  - instantiate two players (objects that respond to player.DoTurn(PlanetWars)
    # (we'll substitute a "real" planetwars object above with a proxy for each
    #  player. This proxy will have an output queue of commands rather than dealing with
    #  stdio)
    #  - instantiate two proxies, which will remember what the player knows,
    #    rather than the actual state of the game.
    
    #then, while not [victory conditions]
    #  - get an array of moves from p1's proxy world
    #  - get an array of moves from p2's proxy world
    #  - apply the moves to the world
    #  - update each proxy with the real world
    #  - render the current state
    #  - pause for framerate?
    
    if show_gui:
        pygame.init()
        screen = pygame.display.set_mode(SCREEN_SIZE, 0 ,32)
        background = pygame.image.load("space.jpg").convert_alpha()
        clock = pygame.time.Clock()
        view = 'all'
        paused = True
    else:
        paused = False
        
    p1Proxy = pw.MakeProxy("1", logger.p1log)
    p2Proxy = pw.MakeProxy("2", logger.p2log)
    fps = 4
    #min_100_ships = lambda p, pw: 100
    #p1 = VariableAggressionPlayer(0.2, min_100_ships)
    #p2 = VariableAggressionPlayer(0.2, min_100_ships)
    
    while pw.IsAlive(p1Proxy.PlayerID()) and \
          pw.IsAlive(p2Proxy.PlayerID()) and \
          pw.CurrentTick() < max_game_length:
        onestep = False
        if show_gui:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                if event.type == KEYDOWN:
                    if event.key == K_p:
                        paused = not paused
                    elif (event.key == K_PLUS) or (event.key == K_EQUALS):
                        fps = fps + 1
                    elif event.key == K_MINUS:
                        fps = fps - 1
                        if fps < 1: fps = 1
                    elif event.key == K_n:
                        onestep = True
                    elif event.key == K_a:
                        if(view != 'all'):
                            screen = pygame.display.set_mode(SCREEN_SIZE, 0 ,32)
                        view = 'all'
                    elif event.key == K_e:
                        if(view != 'world'):
                            screen = pygame.display.set_mode(GAME_SIZE, 0 ,32)
                        view = 'world'
                    elif event.key == K_1:
                        if(view != 'p1'):
                            screen = pygame.display.set_mode(GAME_SIZE, 0 ,32)
                        view = 'p1'
                    elif event.key == K_2:
                        if(view != 'p2'):
                            screen = pygame.display.set_mode(GAME_SIZE, 0 ,32)
                        view = 'p2'
            if(view == 'world'):
                draw(pw, screen, background)
            elif(view == 'p1'):
                draw(p1Proxy, screen, background)
            elif(view == 'p2'):
                draw(p2Proxy, screen, background)
            elif(view == 'all'):
                draw(p1Proxy, screen,background,(-GAME_SIZE[0],0))
                draw(pw, screen, background, (0,0))
                draw(p2Proxy, screen, background, (GAME_SIZE[0], 0))
            time_passed = clock.tick(fps)
        
        if((not paused) or onestep):
            p1.DoTurn(p1Proxy)
            p2.DoTurn(p2Proxy)
            pw.ProcessOrders(p1Proxy.PlayerID(), p1Proxy._GetOrders())
            pw.ProcessOrders(p2Proxy.PlayerID(), p2Proxy._GetOrders())
            
            p1Proxy._ClearOrders()
            p2Proxy._ClearOrders()
            
            pw.Tick()
            
            p1Proxy._Update(pw)
            p2Proxy._Update(pw)
    if p1Proxy.TotalShips() == p2Proxy.TotalShips():
        #tie
        winner = "tie"
    elif p1Proxy.TotalShips() > p2Proxy.TotalShips():
        #p1 wins!
        winner = "%s victory" % p1Proxy.PlayerID()
    else:
        #p2 wins!
        winner = "%s victory" % p2Proxy.PlayerID()
    
    logger.result("Game {0}: {1} at turn {2} - {3}: {4}, {5}: {6}".format(
                    game_id,
                    winner,
                    pw.CurrentTick(),
                    p1Proxy.PlayerID(),
                    p1Proxy.TotalShips(),
                    p2Proxy.PlayerID(),
                    p2Proxy.TotalShips()))
    

from Logger import Logger

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        bot1 = VariableAggressionPlayer(0.3)
        bot2 = VariableAggressionPlayer(0.5)
        log = Logger('./%s.log')
        pw = PlanetWars(open(sys.argv[1]).read(), logger=log.turn)
        do_game(1, log, bot1, bot2, pw, show_gui=True)
        log.flush()
    except KeyboardInterrupt:
        print 'ctrl-c, leaving ...'
