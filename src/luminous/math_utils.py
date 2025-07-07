import math
import numpy as np


def compute_axis(pitch: float, yaw: float, roll: float, radians=False) -> tuple[np.array, np.array, np.array]:

    if radians is False:
        pitch = math.radians(pitch)
        yaw = math.radians(yaw)
        roll = math.radians(roll)

    yawMatrix = np.matrix([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1]
    ])

    pitchMatrix = np.matrix([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]
    ])

    rollMatrix = np.matrix([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]
    ])

    R = yawMatrix * pitchMatrix * rollMatrix
    R_t = np.transpose(R)

    forward = R_t[0]
    left = R_t[1]
    up = R_t[2]
    
    return forward, left, up


def compute_dot_product(reference_vector: np.array, my_position: list[int], object_position: list[int]) -> float:
    v1 = reference_vector
    v2 = np.array(object_position) - np.array(my_position)
    v2 = v2 / np.linalg.norm(v2)
    return np.dot(v1, v2)


def main():
    forward, left, up = compute_axis(pitch=0, yaw=0, roll=0)
    print(f"Forward: {forward}")
    print(f"LEFT: {left}")
    print(f"Up: {up}")

    reference_vector = np.array([1, 0, 0])
    my_position = [0, 0, 0]
    object_position = [2, -1, 0]
    value = compute_dot_product(reference_vector, my_position, object_position)
    print(f"Value: {value}")

if __name__ == "__main__":
    main()
