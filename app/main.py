import bottle
import os
from Queue import PriorityQueue
from collections import deque
from heapq import heappop, heappush

boardSize = {"width": 0,"height": 0}
@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.get('/')
def index():
    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        'color': '#00ff00',
        'head': head_url
    }

@bottle.post('/start')
def start():
    data = bottle.request.json
    boardSize["width"] = data["width"]
    boardSize["height"] = data["height"]
    return {
        'taunt': 'Snake master'
    }

@bottle.post('/move')
def move():
    data = bottle.request.json
    mySnake = filter(lambda x: x["name"] == "Wayne", data["snakes"])[0]
    myPos = mySnake["coords"][0]
    if (len(data["food"]) == 0):
        print "" # detect wall other snakes
        return {
        'move': 'east',
        'taunt': 'Snake master'
        }
    else:
        food = {"coor": data["food"][0], "dis": heuristic(myPos, data["food"][0])}
        for sFood in data["food"]:
            if heuristic(myPos, sFood) < food["dis"]:
                food["coor"] = sFood
                food["dis"] = heuristic(myPos, sFood)
        board = [[0 for x in range(boardSize["height"])] for y in range(boardSize["width"])]
        for snake in data["snakes"]:
            for coords in snake["coords"]:
                board[coords[1]][coords[0]] = 1
        board[myPos[0]][myPos[1]] = 1
        path = find_path_astar(board, myPos,food["coor"])

        print direction(path[0])
    return {
    'move': direction(path[0]),
    'taunt': 'Snake master'
    }

@bottle.post('/end')
def end():
    data = bottle.request.json

    return {
        'taunt': 'wt---------f'
    }

def direction(ini):
    if(ini == 'W'):
        return 'west'
    elif (ini == 'E'):
        return 'east'
    elif (ini == 'N'):
        return 'north'
    else:
        return 'south'

def maze2graph(maze):
    height = len(maze)
    width = len(maze[0]) if height else 0
    graph = {(i, j): [] for j in range(width) for i in range(height)}

    for col in range(height):
        for row in range(width):
            if (row < height - 1):
                if (maze[row+1][col] == 0):
                    graph[(row, col)].append(("S", (row + 1, col)))
                if (maze[row][col] == 0):
                    graph[(row + 1, col)].append(("N", (row, col)))
            if (col < width - 1 ):
                if (maze[row][col+1] == 0):
                    graph[(row, col)].append(("E", (row, col + 1)))
                if (maze[row][col] == 0):
                    graph[(row, col + 1)].append(("W", (row, col)))

    return graph

def heuristic(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


def find_path_astar(maze, myPos, food):
    start, goal = (myPos[0], myPos[1]), (food[0] + 1,food[1] + 1)
    pr_queue = []
    heappush(pr_queue, (0 + heuristic(start, goal), 0, "", start))
    visited = set()
    graph = maze2graph(maze)
    while pr_queue:
        _, cost, path, current = heappop(pr_queue)
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        tmp = (current[1], current[0])
        for direction, neighbour in graph[tmp]:
            heappush(pr_queue, (cost + heuristic(neighbour, goal), cost + 1,
                                path + direction, neighbour))

    return "w"

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '127.0.0.1'), port=os.getenv('PORT', '8080'))
