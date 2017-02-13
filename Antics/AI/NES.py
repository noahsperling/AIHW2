import random
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
# AIPlayer
# Description: The responsibility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #list of nodes for search tree
    node_list = []

    #maximum depth
    max_depth = 2

    #current index - for recursive function
    cur_array_index = 0

    #highest evaluated move - to be reset every time the generate_states method is called
    highest_evaluated_move = None

    #highest move score - useful for finding highest evaluated move - to be reset
    highest_move_eval = -1




    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Nessie")

    def create_node(self, state, evaluation, move, current_depth, parent_index, index):
        node = [state, evaluation, move, current_depth, parent_index, index]
        self.node_list.append(node)

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        selectedMove = self.move_search(currentState, 0)

        if not selectedMove == None:
            #print("Move returned.")
            return selectedMove
        else:
            #print("Move returned by move_search was null.")
            #moves = listAllLegalMoves(currentState)
            #return moves[0]
            #print("Ended turn.")
            return Move(END, None, None)

        #moves = listAllLegalMoves(currentState)
        #selectedMove = moves[random.randint(0, len(moves) - 1)];

        # don't do a build move if there are already 3+ ants
        #numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        #while (selectedMove.moveType == BUILD and numAnts >= 3):
            #selectedMove = moves[random.randint(0, len(moves) - 1)];

        #return selectedMove


    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[0]


    #RECURSIVE WARNING!!!!
    #
    # Parameters:
    #   game_state - current state
    #   curr_depth - current search depth
    #
    # Return
    #   returns a move object
    #
    #
    def move_search(self, game_state, curr_depth):

        if curr_depth == self.max_depth + 1:
            return self.evaluate_state(game_state)

        #list all legal moves
        move_list = listAllLegalMoves(game_state)

        #remove end turn move
        move_list.pop()

        # list of nodes, which contain the state, move, and eval
        node_list = []

        #generate states based on moves, evaluate them and put them into a list in node_list
        for move in move_list:
            state = getNextState(game_state, move)
            state_eval = self.evaluate_state(state)
            #print(state_eval)
            node_list.append([state, move, state_eval])


        self.mergeSort(node_list)

        #for node in node_list:
            #print(node[2])

        best_ten = []

        for i in range (0,2):
            if not len(node_list) == 0:
                best_ten.append(node_list.pop())


        best_val = -1

        #if not at the max depth, expand all the nodes in node_list and return
        if curr_depth <= self.max_depth:
            for node in best_ten:
                best_val = self.move_search(node[0], curr_depth + 1)
                if best_val > node[2]:
                    node[2] = best_val

        if not curr_depth == 0:
            return best_val
        else:
            best_eval = -1
            best_node = []

            for node in best_ten:
                if node[2] > best_eval:
                    best_eval = node[2]
                    best_node = node

            #print(len(best_node))
            if not best_node == []:
                return best_node[1]
            else:
                return None


    # helper function for evaluate_state - self explanatory
    def get_closest_enemy_dist(self, my_ant_coords, enemy_ants):
        closest_dist = 100
        for ant in enemy_ants:
            if not ant.type == WORKER:
                dist = approxDist(my_ant_coords, ant.coords)
                if dist < closest_dist:
                    closest_dist = dist
        return closest_dist


    # helper function for evaluate state - self explanatory
    def get_closest_enemy_worker_dist(self, my_ant_coords, enemy_ants):
        closest_dist = 100
        for ant in enemy_ants:
            if ant.type == WORKER:
                dist = approxDist(my_ant_coords, ant.coords)
                if dist < closest_dist:
                    closest_dist = dist
        return closest_dist


    # helper function for evaluate state - self explanatory
    def get_closest_enemy_food_dist(self, my_ant_coords, enemy_food_coords):

        enemy_food1_dist = approxDist(my_ant_coords, enemy_food_coords[0])
        enemy_food2_dist = approxDist(my_ant_coords, enemy_food_coords[1])

        if enemy_food1_dist < enemy_food2_dist:
            return enemy_food1_dist
        else:
            return enemy_food2_dist


    #Evaluates and scores a GameState Object
    #
    # Parameters
    #   state - the GameState object to evaluate
    #
    # Return
    #   a number between 0 and 1 inclusive
    #
    def evaluate_state(self, state):
        #return 0.5

        #the starting value, not winning or losing
        eval = 500.0

        #the AIs player ID
        me = state.whoseTurn

        #the inventories of this AI and the enemy
        my_inv = None
        enemy_inv = None

        #important number
        worker_count = 0
        drone_count = 0

        #sets up the inventories
        if state.inventories[0].player == me:
            my_inv = state.inventories[0]
            enemy_inv = state.inventories[1]
        else:
            my_inv = state.inventories[1]
            enemy_inv = state.inventories[0]

        food_coords = []
        enemy_food_coords = []

        foods = getConstrList(state, None, (FOOD,))

        for food in foods:
            if food.coords[1] < 5:
                food_coords.append(food.coords)
            else:
                enemy_food_coords.append(food.coords)

        #print(food_coords)

        #if me == 0:
            #food_coords.append(foods[0].coords)
            #food_coords.append(foods[1].coords)
        #else:
            #food_coords.append(foods[2].coords)
            #food_coords.append(foods[3].coords)



        #coordinates of this AI's tunnel
        tunnel = my_inv.getTunnels()
        t_coords = tunnel[0].coords

        #coordinates of this AI's anthill
        ah_coords = my_inv.getAnthill().coords



        #iterates through ants and scores positioning
        for ant in my_inv.ants:

            #scores queen
            if ant.type == QUEEN:

                #if queen is on anthill, tunnel, or food it's bad
                if ant.coords == ah_coords or ant.coords == t_coords or ant.coords == food_coords[0] or ant.coords == food_coords[1]:
                    eval -= 200

                #if queen is out of rows 0 or 1 it's bad
                if ant.coords[0] > 1:
                    eval -= 100

                # the father from enemy ants, the better
                eval += -100 + (15 * self.get_closest_enemy_dist(ant.coords, enemy_inv.ants))

            #scores worker to incentivize food gathering
            elif ant.type == WORKER:

                #tallies up workers
                worker_count += 1

                #if carrying, the closer to the anthill or tunnel, the better
                if ant.carrying:

                    eval += 500

                    #distance to anthill
                    ah_dist = approxDist(ant.coords, ah_coords)

                    #distance to tunnel
                    t_dist = approxDist(ant.coords, t_coords)

                    #finds closest and scores
                    #if ant.coords == ah_coords or ant.coords == t_coords:
                        #print("PHill")
                        #eval += 100000000
                    if t_dist < ah_dist:
                        eval += 500 - (100 * t_dist)
                    else:
                        eval += 500 - (100 * ah_dist)

                #if not carrying, the closer to food, the better
                else:

                    #distance to foods
                    f1_dist = approxDist(ant.coords, food_coords[0])
                    f2_dist = approxDist(ant.coords, food_coords[1])

                    #finds closest and scores
                    #if ant.coords == food_coords[0] or ant.coords == food_coords[1]:
                        #print("PFood")
                        #eval += 500
                    if f1_dist < f2_dist:
                        eval += 500 - (100 * f1_dist)
                    else:
                        eval += 500 - (100 * f2_dist)

                #the father from enemy ants, the better
                eval += -5 + self.get_closest_enemy_dist(ant.coords, enemy_inv.ants)

            #scores soldiers to incentivize the disruption of the enemy economy
            else:

                #tallies up soldiers
                drone_count += 1

                nearest_enemy_worker_dist = self.get_closest_enemy_worker_dist(ant.coords, enemy_inv.ants)

                #if there is an enemy worker
                if not nearest_enemy_worker_dist == 100:
                    eval += 50 - (5 * nearest_enemy_worker_dist)

                #if there isn't an enemy worker, go to the food
                else:
                    eval += 50 - self.get_closest_enemy_food_dist(ant.coords, enemy_food_coords)

        #scores other important things

        if worker_count < 2:
            eval -= 50

        if drone_count < 2:
            eval -= 50

        if worker_count > 2:
            eval -= 100000000000

        if drone_count > 2:
            eval -= 1000000000000


        eval += 1500 * my_inv.foodCount

        #if my_inv.foodCount == 11 or enemy_inv.foodCount == 0:
            #return 1
        #else:
        return_eval = eval/1000
        #print(return_eval)
        return return_eval

    def mergeSort(self, alist):
        if len(alist) > 1:
            mid = len(alist) // 2
            lefthalf = alist[:mid]
            righthalf = alist[mid:]

            self.mergeSort(lefthalf)
            self.mergeSort(righthalf)

            i = 0
            j = 0
            k = 0
            while i < len(lefthalf) and j < len(righthalf):
                if lefthalf[i][2] < righthalf[j][2]:
                    alist[k] = lefthalf[i]
                    i = i + 1
                else:
                    alist[k] = righthalf[j]
                    j = j + 1
                k = k + 1

            while i < len(lefthalf):
                alist[k] = lefthalf[i]
                i = i + 1
                k = k + 1

            while j < len(righthalf):
                alist[k] = righthalf[j]
                j = j + 1
                k = k + 1





















    def getClose(self, node1):
        node = []
        node = node1
        thisCoords = node[2].coordList[0]
        if getAntAt(node[0], thisCoords).type == WORKER:
            enemyList = getAntList(node[0], 1-node[0].whoseTurn, [DRONE, SOLDIER, R_SOLDIER])
            closestDrone = None;
            for enemy in enemyList:
                if approxDist(thisCoords, enemy.coords)<approxDist(thisCoords, closestDrone.coords) or closestDrone==None:
                    closestDrone=enemy
            return closestDrone
        else:
            enemyList = getAntList(node[0], 1-node[0].whoseTurn, [WORKER])
            closestWorker = None;
            for enemy in enemyList:
                if approxDist(thisCoords, enemy.coords)<approxDist(thisCoords, closestDrone.coords) or closestWorker==None:
                    closestWorker=enemy
            return closestWorker

    def guideWorker(self, node):
        thisCoords = node[2].coordList[0]
        structList = getConstrList(node[0], node[0].whoseTurn, [ANTHILL, TUNNEL])
        nearStructCoords = None;
        for struct in structList:
            if approxDist(thisCoords, struct.coords)<approxDist(thisCoords, nearStructCoords) or nearStructCoords==None:
                nearStructCoords=struct.coords
        return nearStructCoords








#Stuff to do:
#   write helper method to evaluate whether or not the main evaluation method is necessary
#   test evaluation method with recursive method
#
#
#
#
#
#
#
#







    #recursive
    #
    #
    #
    def generate_states(self, game_state, curr_depth, index):
        if curr_depth < self.max_depth:
            move_list = listAllLegalMoves(game_state)
            move_list.pop()
            new_states = []
            for move in move_list:
                new_states.append(getNextState(game_state, move))
            i = 0
            for state in new_states:
                self.node_list.append(self.create_node(state, -1, move_list[i], curr_depth + 1, index, self.cur_array_index))
                node_eval = self.evaluateNode(self.cur_array_index)
                self.node_list[i][1] = node_eval
                self.cur_array_index += 1
                i += 1
            for j in range(self.cur_array_index - i, self.cur_array_index + 1):
                self.generate_states(self.node_list[j], curr_depth + 1, self.node_list[j][5])
        elif self.highest_move_eval == 1:
            return
        else:
            if self.node_list[index][1] > self.highest_move_eval:
                self.highest_evaluated_move = self.node_list[index][2]
                self.highest_move_eval = self.node_list[index][1]
                return




    def evaluateNode(self, node):
        eval = 0.5;
        x = .25;
        state = self.node_list[node][0]
        me = state.whoseTurn
        coords = self.node_list[node][2].coordList[0]
        theAnt = getAntAt(state, coords)
        if not theAnt == None:
            if (theAnt.type == WORKER):
                if (carrying):  # carrying food
                    coordsAnthill = guideWorker(node)
                    dist = approxDist(coords, coordsAnthill)
                    eval += x * (10 / dist)
                else:
                    coordsFood = guideWorker(node)
                    dist = approxDist(coords, coordsFood)
                    eval += x * (10 / dist)
                closeDrone = getClose(node)
                dist = approxDist(coords, closeDrone.coords)
                eval += .25 * (10 / dist)
                return eval
            if (theAnt.type == QUEEN):
                for con in getConstrList(state, me, (ANTHILL, TUNNEL, FOOD)):
                    if (theAnt.coords == con.coords):
                        eval -= .1
                if (theAnt.coords.x > 1):
                    eval -= .1
                closeDrone = getClose(node)
                dist = approxDist(theAnt.coords, closeDrone.coords)
                eval += .25 * (10 / dist)
                return eval
            if (theAnt.type == DRONE):
                closeWorker = getClose(node)
                dist = approxDist(coords, closeWorker.coords)
                eval += .25 * (10 / dist)
                return eval



