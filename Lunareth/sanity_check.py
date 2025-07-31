import pygame, sys, time, math

pygame.init()
W, H = 800, 800
screen = pygame.display.set_mode((W, H))
clock  = pygame.time.Clock()

# Load the sacred image
image = pygame.image.load("6B764B7F-D074-4D39-971F-EA2641A3591B.jpeg").convert()
image = pygame.transform.scale(image, (W, H))  # resize to fit window

t0 = time.time()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (
            e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            pygame.quit(); sys.exit()

    t = time.time() - t0
    screen.blit(image, (0, 0))  # draw image as background

    # Pulsing central circle
    r = 120 + 40 * (1 + math.sin(t * 2))
    pygame.draw.circle(screen, (255, 255, 255), (W//2, H//2), int(r), 3)

    pygame.display.flip()
    clock.tick(60)
