import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import numpy as np
import math
import ctypes
import os
import glm

from tabuleiro import *

# ==============================================================================
# VARIÁVEIS GLOBAIS DA ESTRUTURA
# ==============================================================================
resolution = [1000, 700]  # resolução inicial da janela
tabuleiro = None          # objeto do tabuleiro
shaderId = 0              # identificador do shader program
locations = {}            # dicionário com as locations das variáveis uniforms         

# Estado da Câmera
angle = math.radians(45)
elev = math.radians(35)
target_angle = angle 
target_elev = elev

def init():
    global tabuleiro, shaderId, locations

    # Definindo e habilitando funcionalidades do OpenGL
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.10, 0.14, 1.0) # Cor de fundo original
    
    # Criando objetos da cena
    tabuleiro = Tabuleiro()

    # Carregando e criando shaders
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here,'vertex_shader.glsl')) as file:
        vsSource = file.read()
    with open(os.path.join(here,'fragment_shader.glsl')) as file:
        fsSource = file.read()
        
    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

    # IMPORTANTE: Se o seu vertex_shader atual só tem 'uniform mat4 uMVP;', mantenha isso.
    # Caso ele tenha sido atualizado para receber projMatrix, viewMatrix e modelMatrix isolados:
    locations['projMatrix']  = glGetUniformLocation(shaderId, 'projMatrix')
    locations['viewMatrix']  = glGetUniformLocation(shaderId, 'viewMatrix')
    locations['modelMatrix'] = glGetUniformLocation(shaderId, 'modelMatrix')
    
    # Backup para shader antigo:
    locations['uMVP'] = glGetUniformLocation(shaderId, 'uMVP')


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUseProgram(shaderId)

    aspect = resolution[0] / resolution[1]

    # Matriz de projeção: Mantivemos ORTOGRÁFICA (glm.ortho) para preservar o visual do "Into the Breach"
    projMatrix = glm.ortho(-6 * aspect, 6 * aspect, -6, 6, -0.1, 100.0)
    
    # Matriz de câmera: convertida de cam.py para glm.lookAt
    dist = 12.0
    eye_x = dist * math.cos(elev) * math.sin(angle)
    eye_y = dist * math.sin(elev)
    eye_z = dist * math.cos(elev) * math.cos(angle)
    
    viewMatrix = glm.lookAt(glm.vec3(eye_x, eye_y, eye_z), # posição da câmera
                            glm.vec3(0, 0, 0),             # alvo
                            glm.vec3(0, 1, 0))             # direção 'up'

    # Matriz de modelo (tabuleiro estático na origem)
    modelMatrix = glm.mat4(1.0)

    # Enviando matrizes para o shader (Padrão Novo)
    if locations.get('projMatrix') != -1:
        glUniformMatrix4fv(locations['projMatrix'], 1, GL_FALSE, glm.value_ptr(projMatrix))
        glUniformMatrix4fv(locations['viewMatrix'], 1, GL_FALSE, glm.value_ptr(viewMatrix))
        glUniformMatrix4fv(locations['modelMatrix'], 1, GL_FALSE, glm.value_ptr(modelMatrix))
    
    # Fallback caso seu shader ainda utilize a matriz 'uMVP' unificada do arquivo original
    if locations.get('uMVP') != -1:
        mvp = projMatrix * viewMatrix * modelMatrix
        glUniformMatrix4fv(locations['uMVP'], 1, GL_FALSE, glm.value_ptr(mvp))

    # Desenhando
    tabuleiro.render()

    glUseProgram(0)

def update(window):
    global elev, angle, target_angle, target_elev
    angle += (target_angle - angle) * 0.05
    elev += (target_elev - elev) * 0.05

def updateFrameBuffer(window, width, height):
    global resolution
    if height == 0: height = 1
    resolution = [width, height]
    glViewport(0, 0, width, height)

def keyboard(window, key, scancode, action, mods):
    global target_angle, target_elev
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE: 
            glfw.set_window_should_close(window, True)

        elif key == glfw.KEY_RIGHT:
            target_angle -= math.pi
        elif key == glfw.KEY_LEFT:
            target_angle += math.pi

        elif key == glfw.KEY_UP:
            target_elev = math.radians(75)
        elif key == glfw.KEY_DOWN:
            target_elev = math.radians(35)

def mousePosition(window, xpos, ypos):
    pass

def mouseClick(window, button, action, mods):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            pos = glfw.get_cursor_pos(window)
            print(f'Clique pressionado na posição {pos}')
        elif action == glfw.RELEASE:
            print(f'Clique liberado')

def mouseScroll(window, xoffset, yoffset):
    pass
    
def main():
    glfw.init() 
    glfw.window_hint(glfw.SAMPLES, 4) 
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(resolution[0], resolution[1], 'ToySoldiers - Protótipo', None, None)
    glfw.make_context_current(window) 
    
    init() 
    
    glfw.set_framebuffer_size_callback(window, updateFrameBuffer)
    glfw.set_key_callback(window, keyboard)
    glfw.set_mouse_button_callback(window, mouseClick)
    glfw.set_cursor_pos_callback(window, mousePosition)
    glfw.set_scroll_callback(window, mouseScroll)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        update(window)
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__=='__main__':
    main()