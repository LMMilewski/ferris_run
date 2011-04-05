import os, sys;
import pygame;
import cop;

if not pygame.font: print "No font support";
if not pygame.mixer: print "No sound support";

class FerrisRunMain:
    def __init__(self, screen_width = 800, screen_height = 600):
        pygame.init();
        self.width = screen_width;
        self.height = screen_height;
        self.screen = pygame.display.set_mode((self.width, self.height));
        pygame.display.set_caption("FerrisRun");
        
    def LoadCops(self, x):
        self.cops = [];
        for i in range(1, x + 1):
            print "Adding cop " + str(i);
            self.cops.append(cop.Cop(i *100, i * 100, i * 100, i * 100, i * 100, i * 100));
    
    def run_game(self):
        self.LoadCops(3);
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print "Exiting game"; 
                    sys.exit();
            for cop in self.cops:
                cop.cop_sprite.draw(self.screen);
            pygame.display.flip();

if __name__ == "__main__":
    MainWindow = FerrisRunMain();
    MainWindow.run_game();