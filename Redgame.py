import pygame
import random
import math
import time

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Module Entrainement SNCF")
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

score = 100
intercept_bonus = 7
PIXELS_PER_SECOND = 60

class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.edges = []

class Edge:
    def __init__(self, from_node, to_node, has_red_zone=False):
        self.from_node = from_node
        self.to_node = to_node
        self.has_red_zone = has_red_zone
        self.red_zone_pos = 0.6
        self.length = math.hypot(to_node.x - from_node.x, to_node.y - from_node.y)

class Mobile:
    def __init__(self, id):
        self.id = id
        self.current_edge = None
        self.t = 0
        self.deleted = False
        self.entered_red_zone = False

    def start_at(self, node):
        if not node.edges:
            self.deleted = True
            return
        self.current_edge = random.choice(node.edges)
        self.t = 0
        self.entered_red_zone = False

    def update(self, dt):
        if self.deleted or not self.current_edge:
            return
        edge = self.current_edge
        delta_t = (PIXELS_PER_SECOND * dt) / edge.length
        self.t += delta_t

        if edge.has_red_zone and not self.entered_red_zone and self.t >= edge.red_zone_pos - 0.02:
            self.entered_red_zone = True

        if edge.has_red_zone and self.entered_red_zone and self.t >= edge.red_zone_pos:
            self.deleted = True
            remove_mobile(self)
            global score
            score = max(0, score - 5)
            return

        if self.t >= 1:
            self.start_at(edge.to_node)

    def position(self):
        if not self.current_edge:
            return (0, 0)
        a = self.current_edge.from_node
        b = self.current_edge.to_node
        x = a.x + (b.x - a.x) * self.t
        y = a.y + (b.y - a.y) * self.t
        return (x, y)

    def is_interceptable(self):
        return (
            self.current_edge and
            self.current_edge.has_red_zone and
            self.entered_red_zone and
            self.t < self.current_edge.red_zone_pos and
            not self.deleted
        )

nodes = {
    "start": Node("start", 40, 300),
    "A": Node("A", 150, 300),
    "B": Node("B", 300, 300),
    "C": Node("C", 450, 300),
    "D": Node("D", 570, 300),
    "E": Node("E", 700, 300),
    "F": Node("F", 800, 300),
    "G": Node("G", 180, 250),
    "H": Node("H", 210, 200),
    "I": Node("I", 260, 130),
    "J": Node("J", 660, 250),
    "K": Node("K", 330, 340),
    "L": Node("L", 360, 390),
    "M": Node("M", 250, 200),
    "N": Node("N", 300, 130),
    "O": Node("O", 380, 130),
    "P": Node("P", 430, 250),
    "Q": Node("Q", 555, 130),
    "R": Node("R", 440, 130),
    "S": Node("S", 460, 90),
    "T": Node("T", 520, 90),
    "U": Node("U", 390, 340),
    "V": Node("V", 540, 340),
    "W": Node("W", 420, 390),
    "X": Node("X", 635, 390),
    "Y": Node("Y", 750, 390),
    "AA": Node("AA", 775, 340),
    "AB": Node("AB", 670, 340),
    "end": Node("end", 860, 300)
}

edges = [
    ("start", "A", False), ("A", "B", False), ("B", "C", False), ("C", "D", False),
    ("D", "E", False), ("E", "F", False), ("F", "end", False),
    ("A", "G", False), ("G", "H", False), ("H", "I", False), ("H", "M", False),
    ("I", "N", False), ("M", "N", True), ("N", "O", False), ("O", "P", False),
    ("P", "C", False), ("G", "P", False), ("P", "J", True), ("J", "E", False),
    ("O", "R", False), ("R", "S", False), ("S", "T", False), ("T", "Q", False),
    ("R", "Q", True), ("Q", "J", False),
    ("B", "K", False), ("K", "L", False), ("L", "W", True), ("W", "X", False),
    ("X", "Y", False), ("Y", "AA", True), ("AA", "F", False),
    ("K", "U", False), ("U", "W", False), ("U", "V", False),
    ("V", "D", False), ("V", "AB", True), ("AB", "AA", False), ("X", "AB", False)
]

for frm, to, red in edges:
    if frm not in nodes or to not in nodes:
        continue
    edge = Edge(nodes[frm], nodes[to], red)
    nodes[frm].edges.append(edge)

mobiles = []
available_ids = list(range(1, 10))
next_spawn_time = time.time() + random.uniform(2.5, 5)

def create_mobile():
    if not available_ids:
        return
    id = random.choice(available_ids)
    available_ids.remove(id)
    mob = Mobile(id)
    mob.start_at(nodes["start"])
    mobiles.append(mob)

def remove_mobile(mobile):
    if mobile.id not in available_ids:
        available_ids.append(mobile.id)
    if mobile in mobiles:
        mobiles.remove(mobile)

def draw_graph():
    for node in nodes.values():
        pygame.draw.circle(screen, (0, 0, 0), (node.x, node.y), 8)
        label = font.render(node.id, True, (255, 255, 255))
        screen.blit(label, (node.x - 10, node.y - 10))
    for node in nodes.values():
        for edge in node.edges:
            pygame.draw.line(screen, (150, 150, 150),
                             (edge.from_node.x, edge.from_node.y),
                             (edge.to_node.x, edge.to_node.y), 5)
            if edge.has_red_zone:
                rx = edge.from_node.x + (edge.to_node.x - edge.from_node.x) * edge.red_zone_pos
                ry = edge.from_node.y + (edge.to_node.y - edge.from_node.y) * edge.red_zone_pos
                pygame.draw.line(screen, (255, 0, 0), (rx, ry - 15), (rx, ry + 15), 3)

def draw_mobile(mob):
    x, y = mob.position()
    color = (255, 165, 0) if mob.is_interceptable() else (0, 0, 255)
    pygame.draw.circle(screen, color, (int(x), int(y)), 12)
    label = font.render(str(mob.id), True, (255, 255, 255))
    screen.blit(label, (x - 8, y - 8))

running = True
while running:
    dt = clock.tick(60) / 1000
    screen.fill((250, 250, 250))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            try:
                num = int(event.unicode)
                for mob in mobiles:
                    if mob.id == num and mob.is_interceptable():
                        score += intercept_bonus
                        mob.deleted = True
                        remove_mobile(mob)
                        break
            except ValueError:
                pass

    if time.time() >= next_spawn_time:
        create_mobile()
        next_spawn_time = time.time() + random.uniform(2.5, 5)

    for mob in mobiles[:]:
        mob.update(dt)

    draw_graph()
    for mob in mobiles:
        draw_mobile(mob)

    score_txt = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_txt, (20, 20))
    pygame.display.flip()

pygame.quit()
