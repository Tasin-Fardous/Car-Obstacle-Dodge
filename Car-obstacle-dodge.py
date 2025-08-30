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


                # Enhanced Obstacles System
# -----------------
def spawn_obstacle():
    global obstacles, spawn_cooldown
    obstacle_types = ["box", "sphere", "cone", "barrier"]
    
    occupied_lanes = set()
    for c in collectibles:
        if abs(c["z"] - (player_z + spawn_distance_ahead)) < 200:
            for i, lane in enumerate(lanes_x):
                if abs(c["x"] - lane) < 50:
                    occupied_lanes.add(i)
    
    available_lanes = [i for i in range(len(lanes_x)) if i not in occupied_lanes]
    if not available_lanes:
        available_lanes = list(range(len(lanes_x)))
    
    lane_idx = choice(available_lanes)
    lane_x = lanes_x[lane_idx]
    
    obstacle_type = choice(obstacle_types)
    size = randint(40, 80)
    z = player_z + spawn_distance_ahead + randint(100, 500)
    
    destructible = obstacle_type in ["box", "barrier"] and random.random() < 0.3
    
    obstacles.append({
        "x": lane_x,
        "z": float(z),
        "type": obstacle_type,
        "size": float(size),
        "destructible": destructible,
        "rotation": 0.0
    })
    spawn_cooldown = spawn_interval

def update_obstacles(dt):
    global obstacles
    obstacles = [o for o in obstacles if o["z"] > player_z - 400.0]
    
    for o in obstacles:
        o["rotation"] += 30.0 * dt

def draw_obstacles():
    for o in obstacles:
        glPushMatrix()
        glTranslatef(o["x"], 0, o["z"])
        glRotatef(o["rotation"], 0, 1, 0)
        
        if o.get("destructible", False):
            glColor3f(0.6, 0.4, 0.2)
        else:
            if o["type"] == "box":
                glColor3f(0.8, 0.4, 0.2)
            elif o["type"] == "sphere":
                glColor3f(0.6, 0.6, 0.7)
            elif o["type"] == "cone":
                glColor3f(0.9, 0.5, 0.1)
            else:  
                glColor3f(0.7, 0.1, 0.1)
        
        if o["type"] == "box":
            draw_cuboid(o["size"], o["size"], o["size"])
        elif o["type"] == "sphere":
            draw_sphere(o["size"] * 0.6, 16, 16)
        elif o["type"] == "cone":
            draw_cone(o["size"] * 0.5, o["size"], 12)
        else:  
            draw_cuboid(o["size"] * 1.5, o["size"] * 0.3, o["size"] * 0.5)
        
        glPopMatrix()

def check_collision_bounds(bounds1, bounds2):
    x1, y1, z1, w1, h1, l1 = bounds1
    x2, y2, z2, w2, h2, l2 = bounds2
    
    return (abs(x1 - x2) * 2 < (w1 + w2) and
            abs(y1 - y2) * 2 < (h1 + h2) and
            abs(z1 - z2) * 2 < (l1 + l2))

def check_collisions():
    global lives, state, flash_timer, shake_timer, shake_intensity, slow_timer, pre_slow_speed
    
    if invincible_timer > 0:
        return
    
    ax, ay, az = player_x, player_y, player_z
    aw, ah, al = player_width * current_vehicle["size_mult"], player_height, player_length * current_vehicle["size_mult"]

    for o in list(obstacles):
        if o["type"] == "box" or o["type"] == "barrier":
            bw = bh = bl = o["size"]
        elif o["type"] == "cone":
            bw = bh = bl = o["size"]
        else:  # sphere
            r = o["size"] * 0.6
            bw = bh = bl = r * 2
        
        bx, by, bz = o["x"], 0.0, o["z"]

        if check_collision_bounds((ax, ay, az, aw, ah, al), (bx, by, bz, bw, bh, bl)):
            if current_vehicle["special"] == "smash" and o.get("destructible", False):
                try:
                    obstacles.remove(o)
                    score += 50
                    create_particle_effect(o["x"], 0, o["z"], "explosion")
                except ValueError:
                    pass
                continue
            
            lives -= 1
            stats["total_crashes"] += 1
            try:
                obstacles.remove(o)
            except ValueError:
                pass

            trigger_hit_feedback()
            pre_slow_speed = max(min_speed, speed)
            globals()['speed'] = max(min_speed, pre_slow_speed * 0.5)
            slow_timer = 120

            if lives <= 0:
                end_game()
            break

# -----------------
# Weather & Time System 
# -----------------
def update_weather_and_time(dt):
    global time_of_day, weather_timer, weather_type, weather_intensity, rain_drops, snow_flakes
    
    time_of_day += dt * 0.001
    if time_of_day > 1.0:
        time_of_day = 0.0
    
    weather_timer += dt
    if weather_timer > 30.0:
        weather_timer = 0.0
        weather_type = choice(["clear", "clear", "rain", "fog", "snow"])
        weather_intensity = uniform(0.3, 1.0) if weather_type != "clear" else 0.0
    
    if weather_type == "rain":
        if len(rain_drops) < 100:
            for _ in range(10):
                rain_drops.append({
                    "x": uniform(player_x - 300, player_x + 300),
                    "y": uniform(50, 200),
                    "z": uniform(player_z - 100, player_z + 500),
                    "speed": uniform(200, 400)
                })
        
        for drop in rain_drops[:]:
            drop["y"] -= drop["speed"] * dt
            if drop["y"] < -30:
                rain_drops.remove(drop)
    
    elif weather_type == "snow":
        if len(snow_flakes) < 150:
            for _ in range(15):
                snow_flakes.append({
                    "x": uniform(player_x - 400, player_x + 400),
                    "y": uniform(50, 250),
                    "z": uniform(player_z - 200, player_z + 600),
                    "speed": uniform(30, 80),
                    "drift": uniform(-20, 20)
                })
        
        for flake in snow_flakes[:]:
            flake["y"] -= flake["speed"] * dt
            flake["x"] += flake["drift"] * dt
            if flake["y"] < -30:
                snow_flakes.remove(flake)

def draw_weather_effects():
    if weather_type == "rain":
        glColor3f(0.6, 0.8, 1.0)
        glBegin(GL_LINES)
        for drop in rain_drops:
            glVertex3f(drop["x"], drop["y"], drop["z"])
            glVertex3f(drop["x"], drop["y"] - 20, drop["z"])
        glEnd()
    
    elif weather_type == "snow":
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POINTS)
        for flake in snow_flakes:
            glVertex3f(flake["x"], flake["y"], flake["z"])
        glEnd()

def get_lighting_for_time():
    if time_of_day < 0.3:
        ambient = [0.1, 0.1, 0.2, 1.0]
        diffuse = [0.3, 0.3, 0.5, 1.0]
        clear_color = (0.02, 0.02, 0.08)
    elif time_of_day < 0.4:
        ambient = [0.3, 0.2, 0.1, 1.0]
        diffuse = [0.8, 0.6, 0.4, 1.0]
        clear_color = (0.4, 0.2, 0.1)
    elif time_of_day < 0.7:
        ambient = [0.4, 0.4, 0.4, 1.0]
        diffuse = [0.9, 0.9, 0.8, 1.0]
        clear_color = (0.5, 0.7, 0.9)
    elif time_of_day < 0.8:
        ambient = [0.3, 0.2, 0.1, 1.0]
        diffuse = [0.8, 0.5, 0.3, 1.0]
        clear_color = (0.6, 0.3, 0.1)
    else:
        ambient = [0.1, 0.1, 0.2, 1.0]
        diffuse = [0.3, 0.3, 0.5, 1.0]
        clear_color = (0.02, 0.02, 0.08)
    
    if weather_type == "fog":
        clear_color = (0.8, 0.8, 0.8)
        ambient = [a * 1.5 for a in ambient]
    elif weather_type == "rain":
        clear_color = tuple(c * 0.7 for c in clear_color)
    
    return ambient, diffuse, clear_color

# -----------------
# Particle Effects System 
# -----------------
def create_particle_effect(x, y, z, effect_type):
    global particle_effects
    
    if effect_type == "explosion":
        for _ in range(20):
            particle_effects.append({
                "x": x + uniform(-20, 20),
                "y": y + uniform(10, 40),
                "z": z + uniform(-20, 20),
                "vx": uniform(-50, 50),
                "vy": uniform(20, 80),
                "vz": uniform(-50, 50),
                "life": 60,
                "max_life": 60,
                "type": "spark"
            })

def update_particle_effects(dt):
    global particle_effects
    
    for particle in particle_effects[:]:
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["z"] += particle["vz"] * dt
        particle["vy"] -= 100 * dt
        particle["life"] -= 1
        
        if particle["life"] <= 0:
            particle_effects.remove(particle)

def draw_particle_effects():
    for particle in particle_effects:
        alpha = particle["life"] / particle["max_life"]
        glColor3f(1.0, 0.5 + alpha * 0.5, 0.0)
        
        glPushMatrix()
        glTranslatef(particle["x"], particle["y"], particle["z"])
        draw_sphere(2, 6, 6)
        glPopMatrix()

# -----------------
# Animals & Interactive Environment 
# -----------------
def spawn_animal():
    global animals
    
    if random.random() < 0.02:
        animal_types = ["deer", "rabbit"]
        animal_type = choice(animal_types)
        
        start_side = choice([-1, 1])
        start_x = start_side * (road_half_width + 200)
        target_x = -start_side * (road_half_width + 200)
        
        z = player_z + spawn_distance_ahead + randint(300, 800)
        
        animals.append({
            "type": animal_type,
            "x": start_x,
            "y": -15,
            "z": z,
            "target_x": target_x,
            "speed": uniform(80, 150),
            "size": 25 if animal_type == "deer" else 15
        })

def update_animals(dt):
    global animals
    
    for animal in animals[:]:
        if animal["x"] < animal["target_x"]:
            animal["x"] += animal["speed"] * dt
        else:
            animal["x"] -= animal["speed"] * dt
        
        if (abs(animal["x"] - animal["target_x"]) < 20 or 
            animal["z"] < player_z - 500):
            animals.remove(animal)

def draw_animals():
    for animal in animals:
        glPushMatrix()
        glTranslatef(animal["x"], animal["y"], animal["z"])
        
        if animal["type"] == "deer":
            glColor3f(0.6, 0.4, 0.2)
            draw_sphere(animal["size"], 12, 12)
            # Antlers
            glPushMatrix()
            glTranslatef(0, animal["size"], 0)
            glColor3f(0.8, 0.7, 0.5)
            draw_cuboid(3, 15, 3)
            glPopMatrix()
        else:  # rabbit
            glColor3f(0.8, 0.8, 0.8)
            draw_sphere(animal["size"], 8, 8)
            # Ears
            glPushMatrix()
            glTranslatef(-5, animal["size"], 0)
            draw_cuboid(2, 8, 2)
            glTranslatef(10, 0, 0)
            draw_cuboid(2, 8, 2)
            glPopMatrix()
        
        glPopMatrix()

def check_animal_collision():
    global lives, score
    
    if invincible_timer > 0:
        return
    
    for animal in animals[:]:
        distance = math.sqrt((player_x - animal["x"])**2 + (player_z - animal["z"])**2)
        if distance < (player_width/2 + animal["size"]):
            animals.remove(animal)
            lives -= 1
            score -= 200
            trigger_hit_feedback()
            if lives <= 0:
                end_game()
            break

# -----------------
# Achievements System
# -----------------
def check_achievement(achievement_id):
    global achievement_notification, notification_timer, unlocked_vehicles
    
    achievement = achievements[achievement_id]
    if achievement["unlocked"]:
        return
    
    unlock = False
    
    if achievement_id == "first_coin" and total_coins >= 1:
        unlock = True
    elif achievement_id == "collector" and total_coins >= 100:
        unlock = True
    elif achievement_id == "speed_demon" and speed >= max_speed:
        unlock = True
    elif achievement_id == "survivor" and player_z >= 5000:
        unlock = True
    elif achievement_id == "jumper" and achievement_counters["super_jumps"] >= 10:
        unlock = True
    elif achievement_id == "distance_master" and achievement_counters["total_distance"] >= 20000:
        unlock = True
    
    if unlock:
        achievement["unlocked"] = True
        achievement_notification = f"Achievement Unlocked: {achievement['name']}!"
        notification_timer = 300
        
        reward = achievement["reward"]
        if reward in vehicle_types and reward not in unlocked_vehicles:
            unlocked_vehicles.append(reward)
        elif reward == "color":
            pass

# -----------------
# Enhanced Environment Rendering 
# -----------------
def draw_realistic_grass_texture(x_start, x_end, z_start, z_end, base_y=-25):
    """Draw realistic grass using GL_QUADS"""
    random.seed(int(x_start * 17 + z_start * 23) % 1000)
    
    grass_colors = [
        (0.15, 0.6, 0.2),
        (0.25, 0.7, 0.25),
        (0.3, 0.8, 0.3),
        (0.2, 0.65, 0.22),
    ]
    
    segment_size = 50.0
    x = x_start
    while x < x_end:
        z = z_start
        while z < z_end:
            height_variation = random.uniform(-3, 2)
            grass_y = base_y + height_variation
            
            color = random.choice(grass_colors)
            glColor3f(color[0], color[1], color[2])
            
            patch_size = segment_size + random.uniform(-10, 10)
            glBegin(GL_QUADS)
            glVertex3f(x, grass_y, z)
            glVertex3f(x + patch_size, grass_y, z)
            glVertex3f(x + patch_size, grass_y, z + patch_size)
            glVertex3f(x, grass_y, z + patch_size)
            glEnd()
            
            z += patch_size * 0.8
        x += segment_size * 0.8

def draw_enhanced_environment():
    field_width = 1200.0
    road_edge = road_half_width + 30.0
    
    draw_realistic_grass_texture(-road_edge - field_width, -road_edge, 
                                player_z - 1200, player_z + 3500)
    draw_realistic_grass_texture(road_edge, road_edge + field_width,
                                player_z - 1200, player_z + 3500)

def draw_road_with_enhancements():
    # Road surface
    glColor3f(0.15, 0.15, 0.15)
    glBegin(GL_QUADS)
    glVertex3f(-road_half_width, -22, player_z - 1000)
    glVertex3f( road_half_width, -22, player_z - 1000)
    glVertex3f( road_half_width, -22, player_z + 3000)
    glVertex3f(-road_half_width, -22, player_z + 3000)
    glEnd()

    # Lane markers using quads instead of lines
    glColor3f(0.9, 0.9, 0.1)
    for lane in [-lane_width/2, lane_width/2]:
        z = int((player_z - 1000) // 80) * 80
        while z < player_z + 3000:
            glBegin(GL_QUADS)
            glVertex3f(lane - 2, -20, z)
            glVertex3f(lane + 2, -20, z)
            glVertex3f(lane + 2, -20, z + 40)
            glVertex3f(lane - 2, -20, z + 40)
            glEnd()
            z += 80

    # Road edges using quads instead of lines
    glColor3f(0.9, 0.9, 0.9)
    for x in [-road_half_width, road_half_width]:
        z = player_z - 1000
        while z < player_z + 3000:
            glBegin(GL_QUADS)
            glVertex3f(x - 1.5, -20, z)
            glVertex3f(x + 1.5, -20, z)
            glVertex3f(x + 1.5, -20, z + 100)
            glVertex3f(x - 1.5, -20, z + 100)
            glEnd()
            z += 120

# -----------------
# Enhanced Camera System 
# -----------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    dynamic_fov = fovY + (speed - base_speed) * 10
    dynamic_fov = max(90, min(140, dynamic_fov))
    
    gluPerspective(dynamic_fov, 1.25, 0.1, 6000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person_view:
        fp_height = player_y + 25.0
        look_ahead_distance = 200.0 + speed * 50.0
        
        eye_x = player_x + shake_offset_x * 0.5
        eye_y = fp_height + shake_offset_y * 0.5
        eye_z = player_z + 30.0
        
        look_x = player_x
        look_y = player_y + 10.0
        look_z = player_z + look_ahead_distance
        
        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0, 1, 0)
    else:
        dynamic_distance = cam_distance + speed * 30.0
        yaw_rad = math.radians(cam_yaw)
        cx = player_x - math.sin(yaw_rad) * dynamic_distance
        cz = player_z - math.cos(yaw_rad) * dynamic_distance
        cy = cam_height + player_y * 0.5 + speed * 20.0

        cx += shake_offset_x
        cy += shake_offset_y

        gluLookAt(cx, cy, cz,
                  player_x, player_y + 10.0, player_z + 120.0,
                  0, 1, 0)

# -----------------
# Input System 
# -----------------
def keyboardListener(key, x, y):
    global speed, jumping, vy, cheat, state, selected_vehicle, player_x, lives, first_person_view
    global menu_selection, garage_selection, current_vehicle, max_speed, selected_color_index
    global super_jump_timer
    
    if state == STATE_MENU:
        if key == b'1':
            state = STATE_PLAYING
            start_game()
        elif key == b'2':
            state = STATE_GARAGE
        elif key == b'3':
            state = STATE_ACHIEVEMENTS
        elif key == b'q':
            exit()
        return

    elif state == STATE_GARAGE:
        if key == b'1':
            if garage_selection < len(unlocked_vehicles):
                selected_vehicle = unlocked_vehicles[garage_selection]
                current_vehicle = vehicle_types[selected_vehicle]
        elif key == b'2':
            selected_color_index = (selected_color_index + 1) % len(vehicle_colors)
        elif key == b'b':
            state = STATE_MENU
        elif key == b'w':
            garage_selection = max(0, garage_selection - 1)
        elif key == b's':
            garage_selection = min(len(unlocked_vehicles) - 1, garage_selection + 1)
        return

    elif state == STATE_ACHIEVEMENTS:
        if key == b'b':
            state = STATE_MENU
        return

    elif state == STATE_GAMEOVER:
        if key == b'r':
            reset_game()
            start_game()
        elif key == b'b':
            state = STATE_MENU
        return

    vehicle_handling = current_vehicle["handling"]
    vehicle_speed_mult = current_vehicle["speed_mult"]
    
    if key == b'd':
        move_amount = 12.0 * vehicle_handling
        player_x -= move_amount
        if abs(player_x) > lane_width * 1.2:
            handle_offroad_collision()
    elif key == b'a':
        move_amount = 12.0 * vehicle_handling
        player_x += move_amount
        if abs(player_x) > lane_width * 1.2:
            handle_offroad_collision()
    elif key == b'w':
        speed = min(max_speed * vehicle_speed_mult, speed + 0.2)
        check_achievement("speed_demon")
    elif key == b's':
        speed = max(min_speed, speed - 0.2)
    elif key == b' ':
        if not jumping:
            jumping = True
            if super_jump_timer > 0:
                vy = jump_impulse * 1.8
                super_jump_timer = max(0, super_jump_timer - 60)
            else:
                vy = jump_impulse 
    elif key == b'c':
        cheat = not cheat
    elif key == b'v':
        first_person_view = not first_person_view
    elif key == b'r':
        reset_game()
        start_game()

def handle_offroad_collision():
    global lives, player_x, flash_timer, shake_timer, shake_intensity, slow_timer, pre_slow_speed
    
    if invincible_timer > 0:
        return
    
    lives -= 1
    player_x = max(-lane_width*1.2, min(lane_width*1.2, player_x))
    trigger_hit_feedback()
    pre_slow_speed = max(min_speed, speed)
    globals()['speed'] = max(min_speed, pre_slow_speed * 0.5)
    slow_timer = 120
    stats["total_crashes"] += 1
    if lives <= 0:
        end_game()

def trigger_hit_feedback():
    global jumping, vy, player_y, player_x, flash_timer, shake_timer, shake_intensity
    vy = jump_impulse * 0.6
    jumping = True
    
    if player_x < -lane_width * 0.5:
        player_x = -lane_width
    elif player_x > lane_width * 0.5:
        player_x = lane_width
    else:
        player_x = 0.0

    flash_timer = 40
    shake_timer = 20
    shake_intensity = min(5.0, speed * 1.5)

def specialKeyListener(key, x, y):
    global cam_height, cam_yaw, garage_selection
    
    if state == STATE_GARAGE:
        if key == GLUT_KEY_UP:
            garage_selection = max(0, garage_selection - 1)
        elif key == GLUT_KEY_DOWN:
            garage_selection = min(len(unlocked_vehicles) - 1, garage_selection + 1)
    elif not first_person_view and state == STATE_PLAYING:
        if key == GLUT_KEY_UP:
            cam_height = min(420.0, cam_height + 8.0)
        elif key == GLUT_KEY_DOWN:
            cam_height = max(120.0, cam_height - 8.0)
        elif key == GLUT_KEY_LEFT:
            cam_yaw -= 2.0
        elif key == GLUT_KEY_RIGHT:
            cam_yaw += 2.0

def mouseListener(button, state_btn, x, y):
    pass

# -----------------
# Game Flow Management
# -----------------
def start_game():
    global current_vehicle, state, lives, player_x, player_y, player_z, vy, jumping, speed, score
    global spawn_interval, spawn_cooldown, cam_yaw, cam_height, slow_timer, pre_slow_speed
    global first_person_view, super_jump_timer, speed_boost_timer, invincible_timer, coins
    global max_speed, obstacles, collectibles, animals, particle_effects, rain_drops, snow_flakes
    
    # Reset all game variables to initial state
    current_vehicle = vehicle_types[selected_vehicle]
    state = STATE_PLAYING
    lives = 5  # 
    player_x = 0.0
    player_y = 0.0
    player_z = 0.0
    vy = 0.0
    jumping = False
    speed = base_speed
    score = 0.0
    coins = 0
    obstacles = []
    collectibles = []
    animals = []
    particle_effects = []
    rain_drops = []
    snow_flakes = []
    spawn_interval = 65.0
    spawn_cooldown = 0.0
    cam_yaw = 0.0
    cam_height = 260.0
    slow_timer = 0
    pre_slow_speed = None
    first_person_view = False
    super_jump_timer = 0
    speed_boost_timer = 0
    invincible_timer = 0
    max_speed = original_max_speed
    
    stats["games_played"] += 1

def end_game():
    global state
    state = STATE_GAMEOVER
    
    if score > stats["best_score"]:
        stats["best_score"] = int(score)
    if player_z > stats["best_distance"]:
        stats["best_distance"] = int(player_z)

def reset_game():
    global state, player_x, player_y, player_z, vy, jumping, speed, score, lives, obstacles, collectibles
    global spawn_interval, spawn_cooldown, cam_yaw, cam_height, slow_timer, pre_slow_speed
    global first_person_view, super_jump_timer, speed_boost_timer, invincible_timer, coins
    global max_speed, animals, particle_effects, rain_drops, snow_flakes
    
    state = STATE_MENU
    player_x = 0.0
    player_y = 0.0
    player_z = 0.0
    vy = 0.0
    jumping = False
    speed = base_speed
    score = 0.0
    lives = 5  
    coins = 0
    obstacles = []
    collectibles = []
    animals = []
    particle_effects = []
    rain_drops = []
    snow_flakes = []
    spawn_interval = 65.0
    spawn_cooldown = 0.0
    cam_yaw = 0.0
    cam_height = 260.0
    slow_timer = 0
    pre_slow_speed = None
    first_person_view = False
    super_jump_timer = 0
    speed_boost_timer = 0
    invincible_timer = 0
    max_speed = original_max_speed

# -----------------
# Auto-pilot 
# -----------------
def auto_dodge():
    global player_x
    ahead_obstacles = [o for o in obstacles if o["z"] > player_z + 120 and o["z"] < player_z + 520]
    ahead_animals = [a for a in animals if a["z"] > player_z + 100 and a["z"] < player_z + 400]
    
    if not ahead_obstacles and not ahead_animals:
        return
    
    current_lane = min(range(3), key=lambda i: abs(player_x - lanes_x[i]))
    lane_danger = [0, 0, 0]
    
    for o in ahead_obstacles:
        for i, lx in enumerate(lanes_x):
            if abs(o["x"] - lx) < 60:
                lane_danger[i] += 1
    
    for a in ahead_animals:
        for i, lx in enumerate(lanes_x):
            if abs(a["x"] - lx) < 80:
                lane_danger[i] += 0.5
    
    safest_lane = min(range(3), key=lambda i: lane_danger[i])
    
    if lane_danger[current_lane] > 0 and safest_lane != current_lane:
        target_x = lanes_x[safest_lane]
        move_speed = 10.0 * current_vehicle["handling"]
        
        if abs(player_x - target_x) > 2:
            player_x += move_speed if target_x > player_x else -move_speed
        else:
            player_x = target_x

# -----------------
# Game Update Loop
# -----------------
def update_game(dt):
    global jumping, vy, player_y, player_z, score, spawn_cooldown, spawn_interval
    global slow_timer, pre_slow_speed, speed, super_jump_timer, speed_boost_timer, invincible_timer
    
    if spawn_interval > min_spawn_interval:
        spawn_interval -= 0.003

    spawn_cooldown -= 1
    if spawn_cooldown <= 0:
        spawn_obstacle()
        spawn_collectible()
    
    spawn_animal()

    if cheat:
        auto_dodge()

    forward_movement = speed * 420.0 * dt * current_vehicle["speed_mult"]
    globals()['player_z'] += forward_movement
    achievement_counters["total_distance"] += forward_movement

    if jumping:
        player_y += vy
        vy += gravity
        if player_y <= 0:
            player_y = 0
            jumping = False
            vy = 0

    update_obstacles(dt)
    update_collectibles(dt)
    update_animals(dt)
    update_particle_effects(dt)
    update_weather_and_time(dt)
    
    check_collisions()
    check_collectible_collision()
    check_animal_collision()

    globals()['score'] += speed * 0.8 + current_vehicle["speed_mult"] * 0.2

    if super_jump_timer > 0:
        super_jump_timer -= 1
    
    if speed_boost_timer > 0:
        speed_boost_timer -= 1
    else:
        globals()['max_speed'] = original_max_speed
    
    if invincible_timer > 0:
        invincible_timer -= 1

    if slow_timer > 0:
        slow_timer -= 1
        if pre_slow_speed is not None:
            speed = min(pre_slow_speed, speed + speed_recover_rate * current_vehicle["speed_mult"])
            globals()['speed'] = speed
    else:
        pre_slow_speed = None

    check_achievement("survivor")
    check_achievement("distance_master")

# -----------------
# HUD System
# -----------------
def draw_enhanced_hud():
    global life_icon_angle, flash_timer, notification_timer
    
    view_mode = "First Person" if first_person_view else "Third Person"
    vehicle_name = current_vehicle["name"]
    
    draw_text(15, 770, f"Score: {int(score)}   Speed: {speed:.1f}   Distance: {int(player_z/10)}m")
    draw_text(15, 745, f"Vehicle: {vehicle_name}   Coins: {coins}   Lives: {lives}")
    draw_text(15, 720, f"View: {view_mode}   Weather: {weather_type.title()}")

    y_offset = 695
    if super_jump_timer > 0:
        draw_text(15, y_offset, f"Super Jump: {super_jump_timer//60 + 1}s", color=(0.2, 0.8, 1.0))
        y_offset -= 20
    
    if speed_boost_timer > 0:
        draw_text(15, y_offset, f"Speed Boost: {speed_boost_timer//60 + 1}s", color=(1.0, 0.2, 0.2))
        y_offset -= 20
    
    if invincible_timer > 0:
        draw_text(15, y_offset, f"Invincible: {invincible_timer//60 + 1}s", color=(1.0, 1.0, 0.0))
        y_offset -= 20

    if notification_timer > 0:
        draw_text(300, 400, achievement_notification, color=(0.0, 1.0, 0.0))
        notification_timer -= 1

    if cheat:
        draw_text(15, y_offset, "CHEAT MODE ON", color=(1.0, 0.0, 0.0))

    # Simplified 2D life indicators to avoid matrix stack issues
    draw_simple_life_indicators()

def draw_simple_life_indicators():
    # Draw hearts for life display
    for i in range(lives):
        x_pos = 850 + i * 25
        y_pos = 770
        
        if flash_timer > 0 or invincible_timer > 0:
            color = (1.0, 1.0, 0.0)  # Yellow when invincible/hit
        else:
            color = (1.0, 0.0, 0.0)  # Red hearts
        
        draw_text(x_pos, y_pos, "♥", color=color)

# -----------------
# Menu Systems
# -----------------
def draw_main_menu():
    # Simplified background without complex matrix operations
    draw_text(250, 730, "3D CAR OBSTACLE DODGE", font=GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(400, 690, " EDITION", color=(1.0, 0.5, 0.0))
    draw_text(350, 620, "1 - Start Game", color=(0.0, 1.0, 0.0))
    draw_text(350, 590, "2 - Garage/Vehicles", color=(0.0, 0.8, 1.0))
    draw_text(350, 560, "3 - Achievements", color=(1.0, 0.8, 0.0))
    draw_text(350, 530, "Q - Quit", color=(1.0, 0.0, 0.0))
    
    draw_text(200, 480, "Game Controls:", color=(0.8, 0.8, 0.8))
    draw_text(50, 450, "A/D - Steer  |  W/S - Speed  |  SPACE - Jump  |  V - First Person  |  C - Cheat")

def draw_garage():
    draw_text(400, 750, "VEHICLE GARAGE", font=GLUT_BITMAP_TIMES_ROMAN_24)
    
    y_pos = 680
    for i, vehicle_key in enumerate(unlocked_vehicles):
        vehicle_data = vehicle_types[vehicle_key]
        color = (1.0, 1.0, 0.0) if i == garage_selection else (1.0, 1.0, 1.0)
        marker = ">>> " if vehicle_key == selected_vehicle else "    "
        
        draw_text(50, y_pos, f"{marker}{vehicle_data['name']}", color=color)
        draw_text(300, y_pos, f"Speed: {vehicle_data['speed_mult']:.1f}x")
        draw_text(450, y_pos, f"Handling: {vehicle_data['handling']:.1f}x")
        draw_text(600, y_pos, f"Special: {vehicle_data['special'].title()}")
        y_pos -= 30
    
    draw_text(50, y_pos - 20, "LOCKED VEHICLES:", color=(0.5, 0.5, 0.5))
    y_pos -= 50
    for vehicle_key, vehicle_data in vehicle_types.items():
        if vehicle_key not in unlocked_vehicles:
            draw_text(70, y_pos, f"{vehicle_data['name']} - Complete achievements to unlock", color=(0.5, 0.5, 0.5))
            y_pos -= 25

    draw_text(50, 150, "Controls:", color=(0.8, 0.8, 0.8))
    draw_text(50, 120, "1 - Select Vehicle  |  2 - Change Color  |  W/S - Navigate  |  B - Back to Menu")
    draw_text(50, 90, f"Current Color: RGB({vehicle_colors[selected_color_index][0]:.1f}, {vehicle_colors[selected_color_index][1]:.1f}, {vehicle_colors[selected_color_index][2]:.1f})")

def draw_achievements():
    draw_text(350, 750, "ACHIEVEMENTS", font=GLUT_BITMAP_TIMES_ROMAN_24)
    
    y_pos = 680
    for achievement_id, achievement_data in achievements.items():
        status = "✓" if achievement_data["unlocked"] else "✗"
        color = (0.0, 1.0, 0.0) if achievement_data["unlocked"] else (0.8, 0.8, 0.8)
        
        draw_text(50, y_pos, f"{status} {achievement_data['name']}", color=color)
        draw_text(350, y_pos, achievement_data["desc"], color=color)
        draw_text(700, y_pos, f"Reward: {achievement_data['reward'].title()}", color=color)
        y_pos -= 40

    draw_text(50, 350, "Progress:", color=(1.0, 1.0, 0.0))
    draw_text(50, 320, f"Total Coins Collected: {total_coins}/100")
    draw_text(50, 290, f"Super Jumps Used: {achievement_counters['super_jumps']}/10")
    draw_text(50, 260, f"Total Distance: {int(achievement_counters['total_distance']/10)}m/2000m")
    draw_text(50, 230, f"Current Distance: {int(player_z/10)}m/500m")
    
    draw_text(50, 180, "Statistics:", color=(1.0, 1.0, 0.0))
    draw_text(50, 150, f"Games Played: {stats['games_played']}")
    draw_text(50, 120, f"Best Score: {stats['best_score']}")
    draw_text(50, 90, f"Best Distance: {int(stats['best_distance']/10)}m")
    draw_text(50, 60, f"Total Crashes: {stats['total_crashes']}")
    
    draw_text(400, 30, "Press B to return to menu", color=(0.8, 0.8, 0.8))

def draw_game_over():
    draw_text(400, 500, "GAME OVER", font=GLUT_BITMAP_TIMES_ROMAN_24, color=(1.0, 0.0, 0.0))
    draw_text(350, 450, f"Final Score: {int(score)}")
    draw_text(340, 420, f"Distance: {int(player_z/10)}m")
    draw_text(350, 390, f"Coins Collected: {coins}")
    draw_text(320, 360, f"Vehicle Used: {current_vehicle['name']}")
    
    if score == stats["best_score"]:
        draw_text(350, 320, "NEW HIGH SCORE!", color=(0.0, 1.0, 0.0))
    
    draw_text(280, 250, "R - Restart Game  |  B - Back to Menu")

# -----------------
# Rendering Pipeline
# -----------------
def draw_game_scene():
    # Set up dynamic lighting based on time and weather
    ambient, diffuse, clear_color = get_lighting_for_time()
    
    glClearColor(clear_color[0], clear_color[1], clear_color[2], 1.0)
    
    # Basic lighting setup 
    light_pos = [0.0, 500.0, 500.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)

    # Draw environment
    draw_enhanced_environment()
    draw_road_with_enhancements()

    # Draw interactive elements
    draw_animals()
    draw_obstacles()
    draw_collectibles()
    draw_particle_effects()
    draw_weather_effects()

    # Draw player vehicle (only in third person)
    if not first_person_view:
        glPushMatrix()
        glTranslatef(player_x, player_y, player_z)
        
        # Apply invincibility effect
        if invincible_timer > 0 and (invincible_timer // 5) % 2:
            pass  # Skip drawing every few frames for blinking effect
        else:
            current_color = vehicle_colors[selected_color_index]
            glow_effect = (flash_timer > 0 or invincible_timer > 0)
            draw_vehicle(selected_vehicle, current_color, glow=glow_effect)
        
        glPopMatrix()

    draw_enhanced_hud()

# -----------------
# GLUT Functions 
# -----------------
def idle():
    global last_time_ms, life_icon_angle, flash_timer, shake_timer, shake_offset_x, shake_offset_y
    
    now = glutGet(GLUT_ELAPSED_TIME)
    if last_time_ms == 0:
        last_time_ms = now
    dt_ms = now - last_time_ms
    last_time_ms = now
    dt = max(0.001, dt_ms / 1000.0)

    if state == STATE_PLAYING:
        update_game(dt)

    life_icon_angle += (speed if state == STATE_PLAYING else 1.0) * 60 * dt
    if life_icon_angle > 360:
        life_icon_angle -= 360

    if flash_timer > 0:
        flash_timer -= 1

    if shake_timer > 0:
        shake_timer -= 1
        shake_offset_x = random.uniform(-1.0, 1.0) * shake_intensity
        shake_offset_y = random.uniform(-1.0, 1.0) * shake_intensity
    else:
        shake_offset_x = 0.0
        shake_offset_y = 0.0

    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    if state == STATE_MENU:
        setupCamera()
        draw_main_menu()
    elif state == STATE_GARAGE:
        setupCamera()
        draw_garage()
    elif state == STATE_ACHIEVEMENTS:
        setupCamera()
        draw_achievements()
    elif state == STATE_PLAYING:
        setupCamera()
        draw_game_scene()
    elif state == STATE_GAMEOVER:
        setupCamera()
        draw_game_scene()
        draw_game_over()

    glutSwapBuffers()

# -----------------
# Initialization 
# -----------------
def init_gl():
    print("=== 3D CAR OBSTACLE DODGE ===")
    
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.5, 0.7, 0.9, 1.0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"3D Car Obstacle Dodge ")

    init_gl()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    print("=== CONTROLS ===")
    print("MENU: 1=Play, 2=Garage, 3=Achievements, Q=Quit")
    print("GAME: A/D=Steer, W/S=Speed, SPACE=Jump, V=First Person, C=Cheat, R=Restart")
    print("GARAGE: 1=Select Vehicle, 2=Change Color, W/S=Navigate, B=Back")
    print("CAMERA: Arrow Keys (Third Person Only)")
    print("GAMEOVER: R=Restart, B=Back to Menu")
    print("")
    print("=== VEHICLE SPECIAL ABILITIES ===")
    print("Sport Car: High Speed")
    print("Truck: Can Smash Destructible Obstacles")
    print("Motorcycle: Super Agile & Fast")
    print("Rally Car: Better Jumping")
    print("Luxury: Comfortable Ride")
    print("")
    print("Starting game... Have fun!")

    glutMainLoop()

if __name__ == "__main__":
    main()
