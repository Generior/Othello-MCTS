import cv2 as cv
import Chess
import game
import copy
import Train
import os
import pygame
from pygame.locals import *
import time

ChessBoard=[[0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            ]


def Judge(posx,posy,board,root,step):
    maxium=0
    print("-----Judge-------")
    node=root
    for i in range(step):
        node=node.children[0]

    index=-1
    for j in node.children:
        index = index + 1
        if j.position==Chess.Position(posy,posx):
            return index
    index=-1
    return index


def isTurn(node, cur_player, step):
    temp_node=node
    for i in range(step):
        temp_node=temp_node.children[0]
    if not temp_node.children:
        tree = game.PossibleMove(temp_node.Board, temp_node, -temp_node.player)
    else:
        tree=temp_node
    if tree.children:
        return True
    else:
        return False
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

def drawChessBoard(screen):
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
            if board[i][j]==-1:
                # print("(" + np.str(i) + "," + np.str(j) + ") white")
                drawWhite(w,h,px+i+1,py+j+1,screen)
            if board[i][j]==1:
                # print("(" + np.str(i) + "," + np.str(j) + ") black")
                drawBlack(w,h,px+i+1,py+j+1,screen)
    cur_node=root
    for i in range(step):
        cur_node=cur_node.children[0]

    # 最新落子处
    if cur_node.position.x>=0 or cur_node.position.y>=0:
        pygame.draw.circle(screen, (200, 0, 0),(int((cur_node.position.y+py+1 - 1.5) * h), int((cur_node.position.x+px+1 + 0.5) * w)), int(w / 2 - 4),2)

    myfont = pygame.font.Font(None, 30)
    myEndfont=pygame.font.Font(None,100)
    black=0
    white=0
    for i in range(8):
        for j in range(8):
           if board[i][j]==1:
               black=black+1
           elif board[i][j]==-1:
               white=white+1
    drawText(myfont,"Black:"+str(black),(0,0,0),(540,70))
    drawText(myfont,"White:"+str(white),(255,255,255),(540,700))
    drawText(myfont,"Last Step:" + str(int(LastTimeBlack))+"s  Whole:"+str(int(WholeTimeBlack))+"s",(0, 0, 0),(190,70))
    drawText(myfont,"Last Step:" + str(int(LastTimeWhite))+"s  Whole:"+str(int(WholeTimeWhite))+"s",(255, 255, 255),(190,700))

    if cur_player==1:
        pygame.draw.circle(screen, (0, 0, 0), (490, 70), 10, 0)
    elif cur_player==-1:
        pygame.draw.circle(screen, (255, 255, 255),(490,700),10,0)

    if endValue==-1:
        drawText(myEndfont,"You Win",(255,255,128),(320,400))
    elif endValue==1:
        drawText(myEndfont,"You Lose",(255,255,128),(320,400))
    elif endValue==0:
        drawText(myEndfont,"A Tie",(255,255,128),(320,400))

    if StartFlag==0:
        drawText(myEndfont,"-Start-",(120,0,0),(320,400))

if __name__=="__main__":
    # 定义棋盘格长宽
    w=64 # 格子大小
    h=64
    canvas_w=w*10 # 棋盘格大小
    canvas_h=h*12
    canvas_color=(240,255,240) # 棋盘格背景
    line_color=(0,0,0) # 线框颜色
    px=1 # 棋盘格起始点（左上）横坐标/w轴坐标
    py=2
    begin=0 # 游戏开始开关
    # 0：无子 1：黑子（电脑） -1：白子
    cur_player=-1 # 黑子先行
    iterNum=150 # 迭代次数
    step=0 # 棋盘上落了多少颗子（来回共下了几次棋）
    endValue=-2 # 不显示
    StartFlag=0 #游戏开始

    TIME=60 # 计时器
    time_start=0.0
    time_end=0.0
    WholeTimeBlack=0.0
    WholeTimeWhite=0.0
    LastTimeBlack=0.0
    LastTimeWhite=0.0


    pygame.init()
    screen=pygame.display.set_mode((canvas_w,canvas_h))
    pygame.display.set_caption("翻转棋")

    FPS=30
    clock=pygame.time.Clock()

    # 加载背景图片
    base_folder=os.path.dirname(__file__)
    bg_img=pygame.image.load(os.path.join(base_folder,"boardBG.jpg")).convert()

    board = game.Init(ChessBoard)
    root=Chess.Node() # root就是棋盘初始的样子，判定条件为没有parents
    root=game.PossibleMove(board,root,cur_player)
    root.Board=board

    while True:
        drawChessBoard(screen)
        pygame.display.update()
        clock.tick(FPS)
        if StartFlag==1:
            if game.isTerminal(board, cur_player) == True:
                cur_player = 2
            if cur_player == 1:
                print("black")
                if isTurn(root, cur_player, step) == False:
                    cur_player = -1
                temp_board = copy.deepcopy(board)
                time_start = time.time()
                # 没有传回的值，经过Train之后，会剩下唯一一颗子树
                Train.TrainNode(temp_board, root, iterNum, cur_player, step)
                time_end = time.time()
                board = game.PutChess(root, step)
                LastTimeBlack = time_end - time_start
                WholeTimeBlack = LastTimeBlack + WholeTimeBlack
                step = step + 1
                cur_player = -1
                if LastTimeBlack >= TIME:
                    cur_player = 3
                    endValue = -1
            elif cur_player == 2:
                blackChess = 0
                whiteChess = 0
                for i in range(8):
                    for j in range(8):
                        if board[i][j] == 1:
                            blackChess = blackChess + 1
                        elif board[i][j] == -1:
                            whiteChess = whiteChess + 1
                if whiteChess > blackChess:
                    endValue = -1
                elif whiteChess < blackChess:
                    endValue = 1
                elif whiteChess == blackChess:
                    endValue = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                x = pos[1]
                y = pos[0]
                print(pos[0], pos[1])
                if StartFlag==0:
                    if y>=200 and y<=450 and x>=350 and x<=450:
                        StartFlag=1
                if StartFlag==1 and cur_player == -1:
                    if isTurn(root, cur_player, step) == False:
                        cur_player = 1
                        break
                    time_start=time.time()
                    if y >= (1 * h) and y <= (10 * h) and x >= (w) and x <= (10 * w):
                        posx = int(y / h) - 1
                        posy = int(x / w) - 2
                        print("(posx,posy)=(" + str(posx) + ", " + str(posy) + ")")
                        Index = Judge(posx, posy, board, root, step)
                        print("Index:" + str(Index))
                        if Index != -1:  # 判断这个点能下棋
                            node = root
                            for i in range(step):
                                node = node.children[0]
                            board = node.children[Index].Board
                            node.children[Index].setExpand(True)
                            Train.DeleteChildren(root, Index, step)
                            time_end=time.time()
                            LastTimeWhite=time_end-time_start
                            WholeTimeWhite=WholeTimeWhite+LastTimeWhite
                            if LastTimeWhite>=TIME:
                                cur_player=3
                                endValue=1
                            cur_player = 1
                            step = step + 1
                            print("white")





