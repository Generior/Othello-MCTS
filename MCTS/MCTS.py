from math import *
import random

import pygame
from pygame.locals import *
import time
import os

#
# class GameState:
#     """ A state of the game, i.e. the game board. These are the only functions which are
#         absolutely necessary to implement UCT in any 2-player complete information deterministic
#         zero-sum game, although they can be enhanced and made quicker, for example by using a
#         GetRandomMove() function to generate a random move during rollout.
#         By convention the players are numbered 1 and 2.
#     """
#
#     def __init__(self):
#         self.playerJustMoved = 2  # At the root pretend the player just moved is player 2 - player 1 has the first move
#
#     def Clone(self):
#         """ Create a deep clone of this game state.
#         """
#         st = GameState()
#         st.playerJustMoved = self.playerJustMoved
#         return st
#
#     def DoMove(self, move):
#         """ Update a state by carrying out the given move.
#             Must update playerJustMoved.
#         """
#         self.playerJustMoved = 3 - self.playerJustMoved
#
#     def GetMoves(self):
#         """ Get all possible moves from this state.
#         """
#
#     def GetResult(self, playerjm):
#         """ Get the game result from the viewpoint of playerjm.
#         """
#
#     def __repr__(self):
#         """ Don't need this - but good style.
#         """
#         pass

board_weights = [
            [90, -60, 10, 10, 10, 10, -60, 90],
            [-60, -80, 5, 5, 5, 5, -80, -60],
            [10, 5, 1, 1, 1, 1, 5, 10],
            [10, 5, 1, 1, 1, 1, 5, 10],
            [10, 5, 1, 1, 1, 1, 5, 10],
            [10, 5, 1, 1, 1, 1, 5, 10],
            [-60, -80, 5, 5, 5, 5, -80, -60],
            [90, -60, 10, 10, 10, 10, -60, 90]
        ]
class OthelloState:
    """ A state of the game of Othello, i.e. the game board.
        The board is a 2D array where 0 = empty (.), 1 = player 1 (X), 2 = player 2 (O).
        In Othello players alternately place pieces on a square board - each piece played
        has to sandwich opponent pieces between the piece played and pieces already on the
        board. Sandwiched pieces are flipped.
        This implementation modifies the rules to allow variable sized square boards and
        terminates the game as soon as the player about to move cannot make a move (whereas
        the standard game allows for a pass move).
    """

    def __init__(self, sz=8):
        self.playerJustMoved = 2  # At the root pretend the player just moved is p2 - p1 has the first move
        self.board = []  # 0 = empty, 1 = player 1, 2 = player 2
        self.size = sz
        assert sz == int(sz) and sz % 2 == 0  # size must be integral and even
        for y in range(sz):
            self.board.append([0] * sz)
        self.board[int(sz / 2)][int(sz / 2)] = self.board[int(sz / 2 - 1)][int(sz / 2 - 1)] = 2
        self.board[int(sz / 2)][int(sz / 2 - 1)] = self.board[int(sz / 2 - 1)][int(sz / 2)] = 1 # 2是白的

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = OthelloState()
        st.playerJustMoved = self.playerJustMoved
        st.board = [self.board[i][:] for i in range(self.size)]
        st.size = self.size
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        (x, y) = (move[0], move[1])
        assert x == int(x) and y == int(y) and self.IsOnBoard(x, y) and self.board[x][y] == 0
        m = self.GetAllSandwichedCounters(x, y)
        self.playerJustMoved = 3 - self.playerJustMoved
        self.board[x][y] = self.playerJustMoved
        for (a, b) in m:
            self.board[a][b] = self.playerJustMoved

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        return [(x, y) for x in range(self.size) for y in range(self.size) if
                self.board[x][y] == 0 and self.ExistsSandwichedCounter(x, y)]

    def AdjacentToEnemy(self, x, y):
        """ Speeds up GetMoves by only considering squares which are adjacent to an enemy-occupied square.
        """
        for (dx, dy) in [(0, +1), (+1, +1), (+1, 0), (+1, -1), (0, -1), (-1, -1), (-1, 0), (-1, +1)]:
            if self.IsOnBoard(x + dx, y + dy) and self.board[x + dx][y + dy] == self.playerJustMoved:
                return True
        return False

    def AdjacentEnemyDirections(self, x, y):
        """ Speeds up GetMoves by only considering squares which are adjacent to an enemy-occupied square.
        """
        es = []
        for (dx, dy) in [(0, +1), (+1, +1), (+1, 0), (+1, -1), (0, -1), (-1, -1), (-1, 0), (-1, +1)]:
            if self.IsOnBoard(x + dx, y + dy) and self.board[x + dx][y + dy] == self.playerJustMoved:
                es.append((dx, dy))
        return es

    def ExistsSandwichedCounter(self, x, y):
        """ Does there exist at least one counter which would be flipped if my counter was placed at (x,y)?
        """
        for (dx, dy) in self.AdjacentEnemyDirections(x, y):
            if len(self.SandwichedCounters(x, y, dx, dy)) > 0:
                return True
        return False

    def GetAllSandwichedCounters(self, x, y):
        """ Is (x,y) a possible move (i.e. opponent counters are sandwiched between (x,y) and my counter in some direction)?
        """
        sandwiched = []
        for (dx, dy) in self.AdjacentEnemyDirections(x, y):
            sandwiched.extend(self.SandwichedCounters(x, y, dx, dy))
        return sandwiched

    def SandwichedCounters(self, x, y, dx, dy):
        """ Return the coordinates of all opponent counters sandwiched between (x,y) and my counter.
        """
        x += dx
        y += dy
        sandwiched = []
        while self.IsOnBoard(x, y) and self.board[x][y] == self.playerJustMoved:
            sandwiched.append((x, y))
            x += dx
            y += dy
        if self.IsOnBoard(x, y) and self.board[x][y] == 3 - self.playerJustMoved:
            return sandwiched
        else:
            return []  # nothing sandwiched

    def IsOnBoard(self, x, y):
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm.
        """
        jmcount = len([(x, y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == playerjm])
        notjmcount = len(
            [(x, y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == 3 - playerjm])
        if jmcount > notjmcount:
            return 1.0
        elif notjmcount > jmcount:
            return 0.0
        else:
            return 0.5  # draw

    def __repr__(self):
        s = ""
        for y in range(self.size - 1, -1, -1):
            for x in range(self.size):
                s += ".XO"[self.board[x][y]]
            s += "\n"
        return s


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """

    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves()  # future child nodes
        self.playerJustMoved = state.playerJustMoved  # the only part of the state that the Node needs later

    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key=lambda c: (c.wins*board_weights[c.move[0]][c.move[1]]) / c.visits + sqrt(2 * log(self.visits) / c.visits))[-1]
        return s

    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=m, parent=self, state=s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose=False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []:  # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            state.DoMove(m)
            node = node.AddChild(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []:  # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None:  # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(
                node.playerJustMoved))  # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    # if (verbose):
        # print(rootnode.TreeToString(0))
    # else:
        # print(rootnode.ChildrenToString())

    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    state = OthelloState(8) # uncomment to play Othello on a square board of the given size
    while (state.GetMoves() != []):
        print(str(state))
        if state.playerJustMoved == 1:
            m = UCT(rootstate=state, itermax=1000, verbose=False)  # play with values for itermax and verbose = True
        else:
            m = UCT(rootstate=state, itermax=100, verbose=False)
        print( "Best Move: " + str(m) + "\n")

        state.DoMove(m)
    if state.GetResult(state.playerJustMoved) == 1.0:
        print("Player " + str(state.playerJustMoved) + " wins!")
    elif state.GetResult(state.playerJustMoved) == 0.0:
        print("Player " + str(3 - state.playerJustMoved) + " wins!")
    else:
        print("Nobody wins!")


# 绘制白棋
def drawWhite(w,h,posx,posy,canvas):
    pygame.draw.circle(canvas, (255, 255, 255),(int((posy -1.5) * h), int((posx + 0.5) * w)), int(w / 2 - 4),0)
    # 外框
    pygame.draw.circle(canvas, (0, 0, 0),(int((posy - 1.5) * h),int((posx + 0.5) * w)), int(w / 2 - 4),1)

# 绘制黑棋
def drawBlack(w,h,posx,posy,canvas):
    pygame.draw.circle(canvas, (0, 0, 0),(int((posy - 1.5) * h), int((posx + 0.5) * w)), int(w / 2 - 4),0)

def drawText(font, string,color,position):
    textImageBlack = font.render(string, True, color)
    textRectObjBlack = textImageBlack.get_rect()
    textRectObjBlack.center = position
    screen.blit(textImageBlack, textRectObjBlack)

def drawChessBoard(screen,state,m):
    screen.blit(bg_img,(0,0))
    # 绘制棋盘外框
    pygame.draw.line(screen,line_color,(w, h * 2), (w * 9, h * 2),4)
    pygame.draw.line(screen, line_color, (w, h * 10), (w * 9, h * 10), 4)
    pygame.draw.line(screen, line_color,  (w, h * 2), (w, h * 10), 4)
    pygame.draw.line(screen, line_color, (w * 9, h * 2), (w * 9, h * 10), 4)

    # 绘制棋盘直线（内线）
    # 横线
    for i in range(8):
        pygame.draw.line(screen, line_color, (w, h * (2 + i)), (w * 9, h * (2 + i)), 1)
    # 竖线
    for i in range(8):
        pygame.draw.line(screen, line_color, (w * (i + 1), h * 2), (w * (i + 1), h * 10), 1)

    # 绘制棋子
    for i in range(8):
        for j in range(8):
            if state.board[i][j]==2:
                # print("(" + np.str(i) + "," + np.str(j) + ") white")
                drawWhite(w,h,px+i+1,py+j+1,screen)
            if state.board[i][j]==1:
                # print("(" + np.str(i) + "," + np.str(j) + ") black")
                drawBlack(w,h,px+i+1,py+j+1,screen)

    # 最新落子处
    if m:
        pygame.draw.circle(screen, (200, 0, 0),(int((m[1]+py+1 - 1.5) * h), int((m[0]+px+1 + 0.5) * w)), int(w / 2 - 4),2)

    myfont = pygame.font.Font(None, 30)
    myEndfont=pygame.font.Font(None,100)
    black=0
    white=0
    for i in range(8):
        for j in range(8):
           if state.board[i][j]==1:
               black=black+1
           elif state.board[i][j]==2:
               white=white+1
    drawText(myfont,"Black:"+str(black),(0,0,0),(540,70))
    drawText(myfont,"White:"+str(white),(255,255,255),(540,700))
    drawText(myfont,"Last Step:" + str(int(LastTimeBlack))+"s  Whole:"+str(int(WholeTimeBlack))+"s",(0, 0, 0),(190,70))
    drawText(myfont,"Last Step:" + str(int(LastTimeWhite))+"s  Whole:"+str(int(WholeTimeWhite))+"s",(255, 255, 255),(190,700))

    if state.playerJustMoved==2:
        pygame.draw.circle(screen, (0, 0, 0), (490, 70), 10, 0)
    elif state.playerJustMoved==1:
        pygame.draw.circle(screen, (255, 255, 255),(490,700),10,0)

    # if endValue==-1:
    #     drawText(myEndfont,"You Win",(255,255,128),(320,400))
    # elif endValue==1:
    #     drawText(myEndfont,"You Lose",(255,255,128),(320,400))
    # elif endValue==0:
    #     drawText(myEndfont,"A Tie",(255,255,128),(320,400))

    if StartFlag==0:
        drawText(myEndfont,"-Start-",(120,0,0),(320,400))

if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    w = 64  # 格子大小
    h = 64
    canvas_w = w * 10  # 棋盘格大小
    canvas_h = h * 12
    canvas_color = (240, 255, 240)  # 棋盘格背景
    line_color = (0, 0, 0)  # 线框颜色
    px = 1  # 棋盘格起始点（左上）横坐标/w轴坐标
    py = 2

    # 0：无子 1：黑子（电脑） 2：白子
    endValue = -2  # 不显示
    StartFlag = 0  # 游戏开始
    num=0 # 防止两方都无处可下

    TIME = 60  # 计时器
    time_start = 0.0
    time_end = 0.0
    WholeTimeBlack = 0.0
    WholeTimeWhite = 0.0
    LastTimeBlack = 0.0
    LastTimeWhite = 0.0

    pygame.init()
    screen = pygame.display.set_mode((canvas_w, canvas_h))
    pygame.display.set_caption("翻转棋")

    FPS = 30
    clock = pygame.time.Clock()

    # 加载背景图片
    base_folder = os.path.dirname(__file__)
    bg_img = pygame.image.load(os.path.join(base_folder, "boardBG.jpg")).convert()
    # UCTPlayGame()

    state = OthelloState(8)
    M=[]
    while True:
        drawChessBoard(screen,state,M)
        pygame.display.update()
        clock.tick(FPS)
        if state.GetMoves()==[]:
            blackChess = 0
            whiteChess = 0
            for i in range(8):
                for j in range(8):
                    if state.board[i][j] == 1:
                        blackChess = blackChess + 1
                    elif state.board[i][j] == -1:
                        whiteChess = whiteChess + 1
            if whiteChess > blackChess:
                endValue = -1
            elif whiteChess < blackChess:
                endValue = 1
            elif whiteChess == blackChess:
                endValue = 0
        if StartFlag==1 and state.GetMoves() != [] and state.playerJustMoved == 2:
            # print(str(state))
            num=0
            time_start = time.time()
            m = UCT(rootstate=state, itermax=1000, verbose=False)  # play with values for itermax and verbose = True
            state.DoMove(m)
            M.clear()
            M.append(m[0])
            M.append(m[1])
            time_end = time.time()
            LastTimeBlack = time_end - time_start
            WholeTimeBlack = LastTimeBlack + WholeTimeBlack
            time_start = time.time()
            if LastTimeBlack >= TIME:
                endValue = -1
        elif StartFlag == 1 and state.GetMoves() == [] and state.playerJustMoved == 2:
            state.playerJustMoved=3-state.playerJustMoved
            num=num+1
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                x = pos[1]
                y = pos[0]
                # print(pos[0], pos[1])
                if StartFlag==0:
                    if y>=200 and y<=450 and x>=350 and x<=450:
                        StartFlag=1
                        time_start=time.time()
                if StartFlag==1 and state.playerJustMoved == 1 and state.GetMoves() != []:
                    if y >= (1 * h) and y <= (10 * h) and x >= (w) and x <= (10 * w):
                        posy = int(y / h) - 1
                        posx = int(x / w) - 2
                        # print("(posx,posy)=(" + str(posx) + ", " + str(posy) + ")")
                        for i in state.GetMoves():
                            # print(i)
                            if (posx,posy)==i:# 这个点能下棋
                                num=0
                                state.DoMove(i)
                                M.clear()
                                M.append(i[0])
                                M.append(i[1])
                                time_end = time.time()
                                print("time_start:"+str(time_start))
                                print("time_end:"+str(time_end))
                                LastTimeWhite = time_end - time_start
                                WholeTimeWhite = WholeTimeWhite + LastTimeWhite
                                if LastTimeWhite>=TIME:
                                    endValue=1
                                print("white")
                                break
                elif StartFlag==1 and state.playerJustMoved == 1 and state.GetMoves() == [] and num<1:
                    state.playerJustMoved=3-state.playerJustMoved
                    num=num+1