from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
from random import choice, randint, uniform
import math
import time

# -----------------
# Camera & Globals
# -----------------
camera_pos = (0, 500, 500)
fovY = 120
GRID_LENGTH = 600
rand_var = 423

# Game State
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_GARAGE = 3
STATE_ACHIEVEMENTS = 4
state = STATE_MENU

# Enhanced Vehicle System
vehicle_types = {
    "sport": {"name": "Sports Car", "body_color": (1.0, 0.0, 0.0), "accent": (1.0, 0.4, 0.4), 
              "speed_mult": 1.2, "handling": 1.0, "size_mult": 1.0, "special": "speed"},
    "truck": {"name": "Heavy Truck", "body_color": (0.2, 0.2, 0.8), "accent": (0.5, 0.5, 1.0),
              "speed_mult": 0.8, "handling": 0.7, "size_mult": 1.4, "special": "smash"},
    "motorcycle": {"name": "Sport Bike", "body_color": (0.8, 0.0, 0.8), "accent": (1.0, 0.5, 1.0),
                   "speed_mult": 1.5, "handling": 1.3, "size_mult": 0.6, "special": "agility"},
    "rally": {"name": "Rally Car", "body_color": (0.0, 0.8, 0.0), "accent": (0.3, 1.0, 0.3),
              "speed_mult": 1.1, "handling": 1.2, "size_mult": 0.9, "special": "jump"},
    "luxury": {"name": "Luxury Sedan", "body_color": (0.1, 0.1, 0.1), "accent": (0.8, 0.8, 0.8),
               "speed_mult": 1.0, "handling": 0.9, "size_mult": 1.1, "special": "comfort"}
}

selected_vehicle = "sport"
unlocked_vehicles = ["sport"]
vehicle_colors = [(1.0, 0.0, 0.0), (0.0, 0.8, 0.0), (0.0, 0.2, 1.0), (1.0, 0.5, 0.0), (0.8, 0.0, 0.8)]
selected_color_index = 0

# Track & Lanes
lane_width = 160.0
lanes_x = [-lane_width, 0.0, lane_width]
road_half_width = lane_width * 1.5 + 50.0

# Player
player_x = 0.0
player_y = 0.0
player_z = 0.0
player_width = 90.0
player_length = 160.0
player_height = 70.0

# Jump physics
jumping = False
vy = 0.0
gravity = -0.6
jump_impulse = 12.0
super_jump_timer = 0

# Speed & Difficulty
base_speed = 1.6
speed = base_speed
min_speed, max_speed = 0.8, 5.5
score = 0.0
coins = 0
total_coins = 0
lives = 5
cheat = False
invincible_timer = 0

# Vehicle stats
current_vehicle = vehicle_types[selected_vehicle]

# Speed boost power-up
speed_boost_timer = 0
original_max_speed = max_speed

# Speed slowdown/recovery after collision
slow_timer = 0
pre_slow_speed = None
speed_recover_rate = 0.015

# Obstacles & Collectibles
obstacles = []
collectibles = []
spawn_distance_ahead = 2000.0
spawn_cooldown = 0.0
spawn_interval = 65.0
min_spawn_interval = 25.0

# Power-up types
POWERUP_COIN = "coin"
POWERUP_JUMP = "super_jump"
POWERUP_SPEED = "speed_boost"
POWERUP_INVINCIBLE = "invincible"
POWERUP_LIFE = "extra_life"

# Camera system
cam_yaw = 0.0
cam_height = 260.0
cam_distance = 420.0
first_person_view = False

# Weather & Time System
time_of_day = 0.5
weather_type = "clear"
weather_intensity = 0.0
weather_timer = 0.0
rain_drops = []
snow_flakes = []

# Environmental elements
animals = []
bridges = []
particle_effects = []

# Achievements System
achievements = {
    "first_coin": {"name": "First Coin", "desc": "Collect your first coin", "unlocked": False, "reward": "motorcycle"},
    "speed_demon": {"name": "Speed Demon", "desc": "Reach maximum speed", "unlocked": False, "reward": "rally"},
    "survivor": {"name": "Survivor", "desc": "Survive for 5000m", "unlocked": False, "reward": "truck"},
    "collector": {"name": "Coin Collector", "desc": "Collect 100 coins total", "unlocked": False, "reward": "luxury"},
    "jumper": {"name": "High Jumper", "desc": "Use super jump 10 times", "unlocked": False, "reward": "color"},
    "distance_master": {"name": "Distance Master", "desc": "Travel 20000m total", "unlocked": False, "reward": "color"}
}

achievement_counters = {"super_jumps": 0, "total_distance": 0}
achievement_notification = ""
notification_timer = 0

# Statistics
stats = {
    "games_played": 0,
    "best_score": 0,
    "best_distance": 0,
    "total_coins": 0,
    "total_crashes": 0
}

# Timing
last_time_ms = 0

# HUD / Feedback globals
life_icon_angle = 0.0
flash_timer = 0
shake_timer = 0
shake_offset_x = 0.0
shake_offset_y = 0.0
shake_intensity = 0.0

# Environment scrolling
field_scroll_offset = 0.0

# Menu navigation
menu_selection = 0
garage_selection = 0

# -------------
# Text Utility 
# -------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(color[0], color[1], color[2])
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# ---------------
#  SHAPE FUNCTIONS 
# ---------------
def draw_cuboid(w, h, l):
    glPushMatrix()
    glScalef(w/2, h/2, l/2)
    
    # Front face
    glBegin(GL_QUADS)
    glVertex3f(-1, -1, 1)
    glVertex3f(1, -1, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)
    glEnd()
    
    # Back face
    glBegin(GL_QUADS)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, -1, -1)
    glEnd()
    
    # Top face
    glBegin(GL_QUADS)
    glVertex3f(-1, 1, -1)
    glVertex3f(-1, 1, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(1, 1, -1)
    glEnd()
    
    # Bottom face
    glBegin(GL_QUADS)
    glVertex3f(-1, -1, -1)
    glVertex3f(1, -1, -1)
    glVertex3f(1, -1, 1)
    glVertex3f(-1, -1, 1)
    glEnd()
    
    # Right face
    glBegin(GL_QUADS)
    glVertex3f(1, -1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, 1, 1)
    glVertex3f(1, -1, 1)
    glEnd()
    
    # Left face
    glBegin(GL_QUADS)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1, -1, 1)
    glVertex3f(-1, 1, 1)
    glVertex3f(-1, 1, -1)
    glEnd()
    
    glPopMatrix()

def draw_sphere(radius, slices=16, stacks=16):
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + float(i) / stacks)
        z0 = radius * math.sin(lat0)
        zr0 = radius * math.cos(lat0)
        
        lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
        z1 = radius * math.sin(lat1)
        zr1 = radius * math.cos(lat1)
        
        glBegin(GL_QUADS)
        for j in range(slices):
            lng = 2 * math.pi * float(j) / slices
            x = math.cos(lng)
            y = math.sin(lng)
            
            glVertex3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr1, y * zr1, z1)
            
            lng = 2 * math.pi * float(j + 1) / slices
            x = math.cos(lng)
            y = math.sin(lng)
            
            glVertex3f(x * zr1, y * zr1, z1)
            glVertex3f(x * zr0, y * zr0, z0)
        glEnd()

def draw_cone(base_radius, height, slices=12):
    # Base circle
    glBegin(GL_TRIANGLES)
    for i in range(slices):
        angle1 = 2.0 * math.pi * i / slices
        angle2 = 2.0 * math.pi * (i + 1) / slices
        
        x1 = base_radius * math.cos(angle1)
        y1 = base_radius * math.sin(angle1)
        x2 = base_radius * math.cos(angle2)
        y2 = base_radius * math.sin(angle2)
        
        # Base triangle
        glVertex3f(0, 0, 0)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        
        # Side triangle
        glVertex3f(x1, y1, 0)
        glVertex3f(0, 0, height)
        glVertex3f(x2, y2, 0)
    glEnd()

def draw_torus(inner_radius, outer_radius, sides=16, rings=16):
    for i in range(rings):
        glBegin(GL_QUADS)
        for j in range(sides):
            for k in range(2):
                s = (i + k) % rings + 0.5
                t = j % sides
                
                angle1 = s * 2.0 * math.pi / rings
                angle2 = t * 2.0 * math.pi / sides
                
                cos_angle1 = math.cos(angle1)
                sin_angle1 = math.sin(angle1)
                cos_angle2 = math.cos(angle2)
                sin_angle2 = math.sin(angle2)
                
                r = inner_radius + outer_radius * cos_angle2
                x = r * cos_angle1
                y = r * sin_angle1
                z = outer_radius * sin_angle2
                
                glVertex3f(x, y, z)
        glEnd()

def draw_octahedron():
    vertices = [
        (1, 0, 0), (-1, 0, 0), (0, 1, 0),
        (0, -1, 0), (0, 0, 1), (0, 0, -1)
    ]
    
    faces = [
        (0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2),
        (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)
    ]
    
    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex_idx in face:
            x, y, z = vertices[vertex_idx]
            glVertex3f(x * 15, y * 15, z * 15)
    glEnd()

def draw_dodecahedron():
    radius = 8
    slices = 12
    
    glBegin(GL_TRIANGLES)
    for i in range(slices):
        angle1 = 2.0 * math.pi * i / slices
        angle2 = 2.0 * math.pi * (i + 1) / slices
        
        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        # Top triangle
        glVertex3f(0, 0, radius)
        glVertex3f(x1, y1, radius/2)
        glVertex3f(x2, y2, radius/2)
        
        # Bottom triangle
        glVertex3f(0, 0, -radius)
        glVertex3f(x2, y2, -radius/2)
        glVertex3f(x1, y1, -radius/2)
        
        # Side triangles
        glVertex3f(x1, y1, radius/2)
        glVertex3f(x1, y1, -radius/2)
        glVertex3f(x2, y2, -radius/2)
        
        glVertex3f(x1, y1, radius/2)
        glVertex3f(x2, y2, -radius/2)
        glVertex3f(x2, y2, radius/2)
    glEnd()

def draw_wheel(radius=22.0, thickness=12.0):
    draw_torus(radius * 0.35, radius, 16, 16)

# ---------------
# Enhanced Vehicle Rendering
# ---------------
def draw_vehicle(vehicle_type, color_override=None, scale=1.0, glow=False):
    vehicle = vehicle_types[vehicle_type]
    body_color = color_override if color_override else vehicle["body_color"]
    accent = vehicle["accent"]
    size_mult = vehicle["size_mult"]
    
    glPushMatrix()
    glScalef(scale * size_mult, scale * size_mult, scale * size_mult)

    if vehicle_type == "motorcycle":
        draw_motorcycle(body_color, accent, glow)
    elif vehicle_type == "truck":
        draw_truck(body_color, accent, glow)
    else:
        draw_standard_car(body_color, accent, glow)

    glPopMatrix()

def draw_standard_car(body_color, accent, glow):
    # chassis
    if glow:
        glColor3f(1.0, 0.5, 0.5)
    else:
        glColor3f(body_color[0], body_color[1], body_color[2])
    draw_cuboid(90, 28, 130)

    # cabin
    glPushMatrix()
    glTranslatef(0, 25, 5)
    if glow:
        glColor3f(1.0, 0.8, 0.8)
    else:
        glColor3f(min(1.0, body_color[0] + 0.2), min(1.0, body_color[1] + 0.2), min(1.0, body_color[2] + 0.2))
    draw_cuboid(70, 35, 70)
    glPopMatrix()

    # bumpers
    glPushMatrix()
    glTranslatef(0, -14, 65)
    glColor3f(accent[0], accent[1], accent[2])
    draw_cuboid(88, 6, 10)
    glTranslatef(0, 0, -130)
    draw_cuboid(88, 6, 10)
    glPopMatrix()

    # wheels
    draw_vehicle_wheels()

def draw_truck(body_color, accent, glow):
    # Main cab
    if glow:
        glColor3f(1.0, 0.5, 0.5)
    else:
        glColor3f(body_color[0], body_color[1], body_color[2])
    
    # Cab
    glPushMatrix()
    glTranslatef(0, 0, 40)
    draw_cuboid(100, 50, 80)
    glPopMatrix()
    
    # Cargo area
    glPushMatrix()
    glTranslatef(0, 10, -50)
    draw_cuboid(95, 70, 100)
    glPopMatrix()
    
    # Grille
    glPushMatrix()
    glTranslatef(0, -10, 80)
    glColor3f(accent[0], accent[1], accent[2])
    draw_cuboid(90, 20, 8)
    glPopMatrix()
    
    draw_vehicle_wheels(radius=28.0)

def draw_motorcycle(body_color, accent, glow):
    # Main body
    if glow:
        glColor3f(1.0, 0.5, 0.5)
    else:
        glColor3f(body_color[0], body_color[1], body_color[2])
    
    # Frame
    draw_cuboid(30, 20, 100)
    
    # Seat
    glPushMatrix()
    glTranslatef(0, 15, -20)
    glColor3f(0.2, 0.2, 0.2)
    draw_cuboid(35, 12, 40)
    glPopMatrix()
    
    # Handlebars
    glPushMatrix()
    glTranslatef(0, 25, 35)
    glColor3f(accent[0], accent[1], accent[2])
    draw_cuboid(50, 5, 5)
    glPopMatrix()
    
    # Wheels (only 2)
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, -18, 45)
    glRotatef(90, 0, 1, 0)
    draw_wheel(radius=25.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, -18, -45)
    glRotatef(90, 0, 1, 0)
    draw_wheel(radius=25.0)
    glPopMatrix()

def draw_vehicle_wheels(radius=22.0):
    glColor3f(0.1, 0.1, 0.1)
    for dx, dz in [(-35,45),(35,45),(-35,-45),(35,-45)]:
        glPushMatrix()
        glTranslatef(dx, -18, dz)
        glRotatef(90, 0, 1, 0)
        draw_wheel(radius)
        glPopMatrix()

# -----------------
# Power-ups & Collectibles System 
# -----------------
def spawn_collectible():
    collectible_types = [POWERUP_COIN, POWERUP_COIN, POWERUP_COIN, POWERUP_JUMP, POWERUP_SPEED, POWERUP_INVINCIBLE, POWERUP_LIFE]
    weights = [0.5, 0.5, 0.5, 0.1, 0.08, 0.05, 0.02]
    
    if random.random() < 0.4:
        collectible_type = random.choices(collectible_types, weights=weights)[0]
        lane_x = choice(lanes_x)
        z = player_z + spawn_distance_ahead + randint(200, 800)
        
        collectibles.append({
            "type": collectible_type,
            "x": lane_x,
            "z": float(z),
            "y": 20.0,
            "rotation": 0.0,
            "bounce": 0.0
        })

def update_collectibles(dt):
    global collectibles
    collectibles = [c for c in collectibles if c["z"] > player_z - 400.0]
    
    for c in collectibles:
        c["rotation"] += 120.0 * dt
        c["bounce"] = math.sin(c["rotation"] * 0.05) * 8.0
        c["y"] = 20.0 + c["bounce"]

def draw_collectibles():
    for c in collectibles:
        glPushMatrix()
        glTranslatef(c["x"], c["y"], c["z"])
        glRotatef(c["rotation"], 0, 1, 0)
        
        if c["type"] == POWERUP_COIN:
            glColor3f(1.0, 0.8, 0.0)
            draw_torus(3, 12, 12, 16)
        elif c["type"] == POWERUP_JUMP:
            glColor3f(0.2, 0.8, 1.0)
            draw_sphere(15, 12, 12)
        elif c["type"] == POWERUP_SPEED:
            glColor3f(1.0, 0.2, 0.2)
            draw_cone(12, 20, 8)
        elif c["type"] == POWERUP_INVINCIBLE:
            glColor3f(1.0, 1.0, 0.0)
            draw_octahedron()
        elif c["type"] == POWERUP_LIFE:
            glColor3f(1.0, 0.0, 0.5)
            draw_dodecahedron()
        
        glPopMatrix()

def check_collectible_collision():
    global coins, lives, super_jump_timer, speed_boost_timer, invincible_timer, total_coins
    global max_speed, achievement_notification, notification_timer
    
    player_bounds = (player_x, player_y, player_z, player_width, player_height, player_length)
    
    for c in list(collectibles):
        c_bounds = (c["x"], c["y"], c["z"], 25, 25, 25)
        
        if check_collision_bounds(player_bounds, c_bounds):
            collectibles.remove(c)
            
            if c["type"] == POWERUP_COIN:
                coins += 1
                total_coins += 1
                stats["total_coins"] += 1
                check_achievement("first_coin")
                check_achievement("collector")
                
            elif c["type"] == POWERUP_JUMP:
                super_jump_timer = 300
                achievement_counters["super_jumps"] += 1
                check_achievement("jumper")
                
            elif c["type"] == POWERUP_SPEED:
                speed_boost_timer = 450
                max_speed = original_max_speed * 1.5
                
            elif c["type"] == POWERUP_INVINCIBLE:
                invincible_timer = 300
                
            elif c["type"] == POWERUP_LIFE:
                lives = min(lives + 1, 10)
