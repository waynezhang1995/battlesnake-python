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
    mySnake = filter(lambda x: x["name"] == "Enemy Snake", data["snakes"])[0]
    myPos = mySnake["coords"][0]
    if (len(data["food"]) == 0):
        return {
        'move': 'east',
        'taunt': 'Snake master'
        }
    else:
        food = {"coor": data["food"][0], "dis": heuristic(myPos, data["food"][0])}
        foodArray = []
        for sFood in data["food"]:
            foodArray.append({"coor": sFood, "dis": heuristic(myPos, sFood)})

        foodArray.sort(key=lambda x: x["dis"])
        for sFood in foodArray:
            if (sFood["coor"][0] - 1 > 0 and sFood["coor"][0] + 1 < boardSize["height"] and sFood["coor"][1] + 1 < boardSize["width"] and sFood["coor"][1] - 1 > 0):
                food = sFood
                break
        print food["coor"]
        board = [[0 for x in range(boardSize["height"])] for y in range(boardSize["width"])]
        count = 0
        for snake in data["snakes"]:
            for coords in snake["coords"]:
                board[coords[0]][coords[1]] = 1
                count = count + 1
        board[food["coor"][0]][food["coor"][1]] = 2
        
        #Build Wall

        for i in range(0, boardSize["width"]):
            board[0][i] = 1
            board[boardSize["height"] - 1][i] = 1
        
        for j in range(0, boardSize["height"]):
            board[j][0] = 1
            board[j][boardSize["width"] - 1] = 1
        
        #print myPos
        path = BFS(myPos[0],myPos[1],board)
        #print path[len(path) - 2]
        print len(path)
        #print nextDirection(myPos,path[len(path) - 2])

    return {
    'move': nextDirection(myPos,path[len(path) - 2]),
    'taunt': nextDirection(myPos,path[len(path) - 2])
    }

@bottle.post('/end')
def end():
    data = bottle.request.json

    return {
        'taunt': 'GG'
    }

def nextDirection(last, next):
    if (last[0] == next[0]):
        if(next[1] - last[1] < 0):
            return 'north'
        else:
            return 'south'
    elif(last[1] == next[1]):
        if(next[0] - last[0] < 0):
            return 'west'
        else:
            return 'east'


def BFS(x,y,Map):
    Map[x][y] = 0
    queue = deque( [(x,y,None)]) #create queue

    while len(queue)>0: #make sure there are nodes to check left
        node = queue.popleft() #grab the first node
        
        x = node[0] #get x and y
        y = node[1]
        #print "(x , y) is ===> (", x, " , ", y, ")"
        if (x < boardSize["width"] and y < boardSize["height"]): 
            if Map[x][y] == 2: #check if it's an exit
                return GetPathFromNodes(node) #if it is then return the path
            if (Map[x][y] != 0): #if it's not a path, we can't try this spot
                continue
            Map[x][y]= -1 #make this spot explored so we don't try again
            for i in [[x-1,y],[x+1,y],[x,y-1],[x,y+1]]: #new spots to try
                queue.append((i[0],i[1],node)) #create the new spot, with node as the parent
    return []

def GetPathFromNodes(node):
    path = []
    while(node != None):
        path.append((node[0],node[1]))
        node = node[2]
    return path

def heuristic(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '127.0.0.1'), port=os.getenv('PORT', '5002'))
