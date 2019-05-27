import socket
from _thread import *
import time
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
from random import randint
import sys
import pickle

FOOD = []
result = []
WIDTH = 35
HEIGHT = 20
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 5
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 500
snake= []
dead_players = []

class Snake(object):
    REV_DIR_MAP = {
        KEY_UP: KEY_DOWN, KEY_DOWN: KEY_UP,
        KEY_LEFT: KEY_RIGHT, KEY_RIGHT: KEY_LEFT,
    }

    def __init__(self, x, y, window):
        self.body_list = []
        self.hit_score = 0
        self.timeout = TIMEOUT

        for i in range(SNAKE_LENGTH, 0, -1):
            self.body_list.append(Body(x - i, y))

        self.body_list.append(Body(x, y, '0'))
        self.window = window
        self.direction = KEY_RIGHT
        self.last_head_coor = (x, y)
        self.direction_map = {
            KEY_UP: self.move_up,
            KEY_DOWN: self.move_down,
            KEY_LEFT: self.move_left,
            KEY_RIGHT: self.move_right
        }

    @property
    def score(self):
        return 'Score : {}'.format(self.hit_score)

    def add_body(self, body_list):
        self.body_list.extend(body_list)

    def eat_food(self, food):
        # food.reset()
        body = Body(self.last_head_coor[0], self.last_head_coor[1])
        self.body_list.insert(-1, body)
        self.hit_score += 1
        if self.hit_score % 3 == 0:
            self.timeout -= 5
            self.window.timeout(self.timeout)

    @property
    def collided(self):
        return any([body.coor == self.head.coor
                    for body in self.body_list[:-1]])
   
    def update(self):
        last_body = self.body_list.pop(0)
        last_body.x = self.body_list[-1].x
        last_body.y = self.body_list[-1].y
        self.body_list.insert(-1, last_body)
        self.last_head_coor = (self.head.x, self.head.y)
        self.direction_map[self.direction]()

    def change_direction(self, direction):
        if direction != Snake.REV_DIR_MAP[self.direction]:
            self.direction = direction

    def render(self):
        for body in self.body_list:
            self.window.addstr(body.y, body.x, body.char)

    @property
    def head(self):
        return self.body_list[-1]

    @property
    def coor(self):
        return self.head.x, self.head.y

    def move_up(self):
        self.head.y -= 1
        if self.head.y < 1:
            self.head.y = MAX_Y

    def move_down(self):
        self.head.y += 1
        if self.head.y > MAX_Y:
            self.head.y = 1

    def move_left(self):
        self.head.x -= 1
        if self.head.x < 1:
            self.head.x = MAX_X

    def move_right(self):
        self.head.x += 1
        if self.head.x > MAX_X:
            self.head.x = 1

class Body(object):
    def __init__(self, x, y, char='='):
        self.x = x
        self.y = y
        self.char = char

    @property
    def coor(self):
        return self.x, self.y

class Food(object):
    def __init__(self,food_x,food_y, window, char='&'):
        self.x = food_x
        self.y = food_y
        self.char = char
        self.window = window

    def render(self):
        self.window.addstr(self.y, self.x, self.char)

    def reset(self,F_x,F_y):
        self.x = F_x
        self.y = F_y

def server_thread(client):
    global result
    global FOOD
    while True:
        olddata = client.recv(64)
        # print ("DATA: ",olddata)
        data = pickle.loads(olddata)
        # print ("DATA1: ",data)
        if not data:
            break
        else:
        	if data[0]==-1:
        		FOOD = data
        	else:
        		result = data
    client.close()

def main(argv):
    try:
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((argv[1],int(argv[2])))
        playernum = int(client.recv(64))
        print ("You are client ",playernum)
        Total_players = int(client.recv(64))
        global snake
        global result
        global FOOD
        global dead_players
        curses.initscr()
        curses.beep()
        curses.beep()
        window = curses.newwin(HEIGHT, WIDTH, 0, 0)
        window.timeout(TIMEOUT)
        window.keypad(1)
        curses.noecho()
        curses.curs_set(0)
        window.border(0)
        food_xy = client.recv(64)
        food_xy = pickle.loads(food_xy)
        
        for i in range(Total_players):
            snake.append(Snake(SNAKE_X+i, SNAKE_Y+i, window))
        
        food = Food(food_xy[0],food_xy[1],window, '*')
        start_new_thread(server_thread, (client,))
        tem = 0
        while True:
            move = []
            FOOD = []
            result = []
            window.clear()
            window.border(0)
        
            for x in range(Total_players):
                if x not in dead_players:  
                    snake[x].render()
        
            food.render()
            window.addstr(0, 5, snake[playernum-1].score)
            window.addstr(0, 20, 'Kills : {}'.format(tem))
            event = window.getch()

            if event == 27:
                break

            if event in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
                move.append(playernum)
                move.append(event)
                tosend = pickle.dumps(move)
                client.send(tosend) 

            if result != []:
	            if result[1] in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
	                snake[result[0]-1].change_direction(result[1])
            
            temp = 0
            for snk in snake:
                if snk.head.x == food.x and snk.head.y == food.y:
                	f = []
                	f.append(playernum)
                	f.append(-1)
                	client.send(pickle.dumps(f))
                	snk.eat_food(food)
                for snak in snake:
                    for body in snak.body_list[:-1]:
                        if snk != snake[playernum-1]:
                            if snk.head.coor == snake[playernum-1].head.coor:
                                d = []
                                d.append(1)
                                d.append(1)
                                client.send(pickle.dumps(d))
                                print("YOU LOST")
                                curses.endwin()
                                quit()
                            if snk.head.coor == body.coor:
                                if temp not in dead_players:
                                	tem += 1
                                	dead_players.append(temp)
                            if snk.head.x in [1,33] or snk.head.y in [1,18]:
                                if temp not in dead_players:
                                	tem += 1
                                	dead_players.append(temp)
                        else:
                            if snk.head.x in [1,33] or snk.head.y in [1,18]:
                                if (Total_players-1) == len(dead_players):
                                    print("YOU WON")
                                else:
                                    d = []
                                    d.append(1)
                                    d.append(1)
                                    client.send(pickle.dumps(d))
                                    print("YOU LOST")
                                curses.endwin()
                                quit()
                            if snk.head.coor == body.coor:
                                if (Total_players-1) == len(dead_players):
                                    print("YOU WON")
                                else:
                                    d = []
                                    d.append(1)
                                    d.append(1)
                                    client.send(pickle.dumps(d))
                                    print("YOU LOST")
                                curses.endwin()
                                quit()
                temp += 1
            
            if FOOD != []:
            	food.reset(FOOD[1],FOOD[2])
            for x in range(Total_players):
                if x not in dead_players:
                    snake[x].update()
         
        curses.endwin()

    except socket.error:
        print ("I am sorry")
        sys.exit()
    
if __name__ == '__main__':
    main(sys.argv)