#!python3
import random
import sys
from math import atan2

import numpy as np
import pandas as pd
import pygame

pygame.init()

(WIDTH, HEIGHT) = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.Surface(screen.get_size())
clock = pygame.time.Clock()

proto_kinematics = {'x': [], 'y': [], 'vx': [], 'vy': []}
for i in range(25):
    proto_kinematics['x'].append(random.uniform(20.0, WIDTH - 20.0))
    proto_kinematics['y'].append(random.uniform(20.0, HEIGHT - 20.0))
    proto_kinematics['vx'].append(random.uniform(-1.0, 1.0))
    proto_kinematics['vy'].append(random.uniform(-1.0, 1.0))
kinematics = pd.DataFrame(proto_kinematics)

positions = kinematics[['x', 'y']].copy()
velocities = kinematics[['vx', 'vy']].copy()
del proto_kinematics
del kinematics


def move_in_velocity():
    positions.x += velocities.vx
    positions.y += velocities.vy


def wrap():
    positions.x = np.remainder(positions.x, WIDTH)
    positions.y = np.remainder(positions.y, HEIGHT)


def repel():
    def make_square(cs: np.ndarray):
        n = len(cs)
        vec = cs.reshape((-1, 1))
        return np.tile(vec, n)

    def repel_factor(xdistances: np.ndarray, ydistances: np.ndarray):
        """Sq. matrix, element i, j -> 1 / distance bwn pts i and j."""
        inv_sum_norm = np.power(xdistances, 2) + np.power(ydistances, 2)
        return np.nan_to_num(1 / inv_sum_norm, nan=0.0, posinf=0.0)

    # take vertical vector -> make copies of the column to make a square matrix
    xsveccopymat = make_square(positions.x.to_numpy())
    ysveccopymat = make_square(positions.y.to_numpy())

    # ... used to find the distance between two points i, j
    xdistances = xsveccopymat - xsveccopymat.T
    ydistances = ysveccopymat - ysveccopymat.T

    # ... which is used to find the 'repellent factor' that is 1 / distance^2
    repellent = repel_factor(xdistances, ydistances)

    # ... find the force exerted on the point (row i) by points (columns j)
    # (use elementwise product)
    xfreebody = repellent * xdistances
    yfreebody = repellent * ydistances

    # with mass = 1 unit, record the acceleration at point (row i)
    accelerations = pd.DataFrame()
    accelerations['ax'] = np.sum(xfreebody, axis=1)
    accelerations['ay'] = np.sum(yfreebody, axis=1)

    # effect change
    velocities.vx += accelerations.ax
    velocities.vy += accelerations.ay


obj_image0 = pygame.image.load('assets/boid0.png')
obj_rect0 = obj_image0.get_rect()
obj_rel_cent_x = obj_rect0.w / 2
obj_rel_cent_y = obj_rect0.h / 2


def draw_points(screen: pygame.Surface):
    def rotate_img_ccw(image, rect, angle):
        """Rotate preserving center"""
        image2 = pygame.transform.rotate(image, angle)
        rect2 = image2.get_rect(center=rect.center)
        return image2, rect2

    for row in positions.itertuples():
        # angle = atan2(row.)
        screen.blit(obj_image0,
                    (row.x - obj_rel_cent_x, row.y - obj_rel_cent_y))


background.fill((0, 0, 0))

while True:
    clock.tick(60)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            sys.exit(0)
    repel()
    move_in_velocity()
    wrap()

    screen.blit(background, (0, 0))
    draw_points(screen)
    pygame.display.flip()

    # print(clock.get_fps())
