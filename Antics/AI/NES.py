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


    # helper function for evaluate state
    #
    #finds the closest
    #
    def get_closest_enemy_food_dist(self, my_ant_coords, enemy_food_coords):

        enemy_food1_dist = approxDist(my_ant_coords, enemy_food_coords[0])
        enemy_food2_dist = approxDist(my_ant_coords, enemy_food_coords[1])

        if enemy_food1_dist < enemy_food2_dist:
            return enemy_food1_dist
        else:
            return enemy_food2_dist


    # Evaluates and scores a GameState Object
    #
    # Parameters
    #   state - the GameState object to evaluate
    #
    # Return
    #   a number between 0 and 1 inclusive
    #
    def evaluate_state(self, state):
        # return 0.5

        # the starting value, not winning or losing
        eval = 0.0

        # the AIs player ID
        me = state.whoseTurn

        # the inventories of this AI and the enemy
        my_inv = None
        enemy_inv = None

        # important number
        worker_count = 0
        drone_count = 0

        # sets up the inventories
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

        # coordinates of this AI's tunnel
        tunnel = my_inv.getTunnels()
        t_coords = tunnel[0].coords

        # coordinates of this AI's anthill
        ah_coords = my_inv.getAnthill().coords

        # A list that stores the evaluations of each worker
        wEval = []

        # A list that stores the evaluations of each drone, if they exist
        dEval = []

        # queen evaluation
        qEval = 0

        # iterates through ants and scores positioning
        for ant in my_inv.ants:

            # scores queen
            if ant.type == QUEEN:

                qEval = 50.0

                # if queen is on anthill, tunnel, or food it's bad
                if ant.coords == ah_coords or ant.coords == t_coords or ant.coords == food_coords[
                    0] or ant.coords == food_coords[1]:
                    qEval -= 10

                # if queen is out of rows 0 or 1 it's bad
                if ant.coords[0] > 1:
                    qEval -= 10

                # the father from enemy ants, the better
                qEval -= 2 * self.get_closest_enemy_dist(ant.coords, enemy_inv.ants)

            # scores worker to incentivize food gathering
            elif ant.type == WORKER:

                # tallies up workers
                worker_count += 1

                # if carrying, the closer to the anthill or tunnel, the better
                if ant.carrying:

                    wEval.append(100.0)

                    # distance to anthill
                    ah_dist = approxDist(ant.coords, ah_coords)

                    # distance to tunnel
                    t_dist = approxDist(ant.coords, t_coords)

                    # finds closest and scores
                    # if ant.coords == ah_coords or ant.coords == t_coords:
                    # print("PHill")
                    # eval += 100000000
                    if t_dist < ah_dist:
                        wEval[worker_count - 1] -= 5 * t_dist
                    else:
                        wEval[worker_count - 1] -= 5 * ah_dist

                # if not carrying, the closer to food, the better
                else:

                    wEval.append(80.0)

                    # distance to foods
                    f1_dist = approxDist(ant.coords, food_coords[0])
                    f2_dist = approxDist(ant.coords, food_coords[1])

                    # finds closest and scores
                    # if ant.coords == food_coords[0] or ant.coords == food_coords[1]:
                    # print("PFood")
                    # eval += 500

                    if f1_dist < f2_dist:
                        wEval[worker_count - 1] -= 5 * f1_dist
                    else:
                        wEval[worker_count - 1] -= 5 * f2_dist

                        # the father from enemy ants, the better
                        # eval += -5 + self.get_closest_enemy_dist(ant.coords, enemy_inv.ants)

            # scores soldiers to incentivize the disruption of the enemy economy
            else:

                # tallies up soldiers
                drone_count += 1

                dEval.append(50.0)

                nearest_enemy_worker_dist = self.get_closest_enemy_worker_dist(ant.coords, enemy_inv.ants)

                # if there is an enemy worker
                if not nearest_enemy_worker_dist == 100:
                    dEval[drone_count - 1] -= 5 * nearest_enemy_worker_dist

                # if there isn't an enemy worker, go to the food
                else:
                    dEval[drone_count - 1] -= 5 * self.get_closest_enemy_food_dist(ant.coords, enemy_food_coords)

        # scores other important things

        sEval = 0

        if worker_count == 2:
            sEval += 50
        elif worker_count < 2:
            sEval -= 10
        elif worker_count > 2:
            eval_num = 0.00001
            # print("Built a 3rd worker, returned 0.00001")
            return eval_num

        if drone_count == 2:
            sEval += 50
        elif drone_count < 2:
            sEval -= 10
        elif drone_count > 2:
            sEval = 0

        if not sEval == 0:
            sEval += 20 * my_inv.foodCount

        if my_inv.foodCount == 11:
            return 1
        if enemy_inv.foodCount == 11:
            return 0

        temp = 0

        for val in wEval:
            temp += val
        if worker_count == 0:
            wEvalAv = 0
        else:
            wEvalAv = temp / worker_count

        temp = 0

        for val in dEval:
            temp += val

        if not drone_count == 0:
            dEvalAv = temp / drone_count
        else:
            dEvalAv = 0

        total_possible = 100.0 + 50.0 + 50.0 + 300.0

        eval = (qEval + wEvalAv + dEvalAv + sEval) / total_possible
        if eval <= 0:
            eval = 0.00002

        # print(eval)
        return eval

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



testPlayer = AIPlayer(PLAYER_ONE)
#test get_closest_enemy_dist
testAntList = [Ant((2,4), 4, None), Ant((3,5), 2, None), Ant((2,5), 3, None), Ant((2,2), 1, None)]
val = AIPlayer.get_closest_enemy_dist(testPlayer, (2,1), testAntList)
assert (AIPlayer.get_closest_enemy_dist(testPlayer, (2,1), testAntList)==3), "get_closest_enemy_dist isn't working right(returned %d)" % val

#test get_closest_enemy_worker_dist
testAntList = [Ant((2,4), 1, None), Ant((3,5), 1, None), Ant((2,5), 1, None), Ant((2,2), 2, None)]
val = AIPlayer.get_closest_enemy_worker_dist(testPlayer, (2,1), testAntList)
assert (AIPlayer.get_closest_enemy_worker_dist(testPlayer, (2,1), testAntList)==3), "get_closest_enemy_worker_dist isn't working right(returned %d)" % val

#test get_closest_enemy_food_dist
val = AIPlayer.get_closest_enemy_food_dist(testPlayer, (2,3), [(2,4), (2,5)])
assert (AIPlayer.get_closest_enemy_food_dist(testPlayer, (2,3), [(2,4), (2,5)])==1), "get_closest_enemy_food_dist isn't working right(returned %d)" % val

#test evaluate_state
board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
testConstrList1=[Construction((1,1), ANTHILL), Construction((1,2), TUNNEL), Construction((9,1), FOOD), Construction((9,2), FOOD)]
testConstrList2=[Construction((9,9), ANTHILL), Construction((9,8), TUNNEL), Construction((1,8), FOOD), Construction((1,9), FOOD)]
p1Inventory = Inventory(PLAYER_ONE, [Ant((1,1), 0, PLAYER_ONE), Ant((1,5), 1, PLAYER_ONE)], testConstrList1, 0)
p2Inventory = Inventory(PLAYER_TWO, [Ant((1,2), 2, PLAYER_ONE), Ant((1,6), 2, PLAYER_ONE)], testConstrList2, 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)
testState1 = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)
eval1 = AIPlayer.evaluate_state(testPlayer, testState1)
board = [[Location((col, row)) for row in xrange(0,BOARD_LENGTH)] for col in xrange(0,BOARD_LENGTH)]
p1Inventory = Inventory(PLAYER_ONE, [Ant((1,1), 2, PLAYER_ONE), Ant((1,5), 2, PLAYER_ONE)], [Construction((1,1), ANTHILL), Construction((1,2), TUNNEL)], 0)
p2Inventory = Inventory(PLAYER_TWO, [Ant((1,2), 0, PLAYER_ONE), Ant((1,6), 1, PLAYER_ONE)], [Construction((9,9), ANTHILL), Construction((9,8), TUNNEL)], 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)
testState2 = GameState(board, [p1Inventory, p2Inventory, neutralInventory], MENU_PHASE, PLAYER_ONE)
eval2 = AIPlayer.evaluate_state(testPlayer, testState2)
assert(eval1<eval2), "evaluate_state is broken (returned %d and %d)" % (eval1, eval2)



