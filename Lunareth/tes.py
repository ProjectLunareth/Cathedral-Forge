import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
glViewport(0, 0, display[0], display[1])

gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glBegin(GL_TRIANGLES)
    glColor3f(1,0,0)
    glVertex3f(-1, -1, 0)
    glColor3f(0,1,0)
    glVertex3f(1, -1, 0)
    glColor3f(0,0,1)
    glVertex3f(0, 1, 0)
    glEnd()

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
