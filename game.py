import Chess
import copy
import cv2 as cv

def Init(board):
    board[3][3]=-1
    board[3][4]=1
    board[4][3]=1
    board[4][4]=-1

    #测试用
    # board[1][1]=-1
    # board[2][2]=-1
    return board


# board：当前棋盘
# pos：当前位置
# direction：搜索方向
# cur_player：将要下棋的玩家/当前玩家
# number：当前玩家位置至已经在棋盘上的己方棋子中间的对手的棋子数
# 返回值：个数
# 关于board：直接改变了传入board的值
def MoveSearch(temp_board, pos, direction,cur_player,number):
    # if pos.x<0 or pos.y<0 or pos.x>7 or pos.y>7: # 位置超出棋盘
    x=-1
    y=-1
    # Position = Chess.Position(-1, -1)
    Num=0

    if direction==1:
        x=pos.x-1
        y=pos.y-1
    elif direction==2:
        x=pos.x
        y=pos.y-1
    elif direction==3:
        x=pos.x+1
        y=pos.y-1
    elif direction==4:
        x=pos.x-1
        y=pos.y
    elif direction==5:
        x=pos.x+1
        y=pos.y
    elif direction==6:
        x=pos.x-1
        y=pos.y+1
    elif direction==7:
        x=pos.x
        y=pos.y+1
    elif direction==8:
        x=pos.x+1
        y=pos.y+1


    # print("MoveSearch Position:" + str(x) + " " + str(y))
    if x < 0 or x > 7 or y < 0 or y > 7:  # 该方向超出棋盘
        return Num  # 没有可行位置
    if temp_board[x][y] == 0:  # 该方向没有棋子
        return Num  # 没有可行位置

    if temp_board[x][y] == -cur_player:  # 该方向有对手的棋子
        Num = MoveSearch(temp_board, Chess.Position(x, y), direction, cur_player, number + 1)
    if temp_board[x][y] == cur_player:  # 找到终点的己方棋子
        if number == 0 and Num==0:  # 中间没有棋子
            return Num  # 没有可行位置
        else:
            # print("game MoveSearch pos:("+str(pos.x)+","+str(pos.y)+")")
            temp_board[pos.x][pos.y] = cur_player  # 翻转棋子
            if Num<number:
                Num=number
            return Num # 找到当前可行位置
    else:
        Num=0
        return Num



def ExpandTree(board,node,cur_player,level):
    temp_board=copy.deepcopy(board)
    if node.Expand==True: # 如果已经被扩展了，那么就访问它的子节点，并计算出子节点各自的UCB1 value，选择一个子节点进行判定
        children=node.children
        for i in range(len(children)): # 遍历每个子节点,并计算子节点的UCB1值
            children[i].set_UCB1_value(children[i].UCB1(node.N))
        MaxUCB1=-100000000
        index=0
        for i in range(len(children)): # 选择值最大的那个子节点进入计算，如果子节点的UCB1值一样，那就选择第一个子节点进入
            if MaxUCB1<children[i].UCB1_value:
                MaxUCB1=children[i].UCB1_value
                index=i

        # 进入UCB1值最大的那个子节点，将子节点的访问次数加一，父节点的访问次数加一，并进行rollout
        node.set_N(node.N+1)
        children[index].set_N(children[index].N+1)
        # value=Rollout(children[index],temp_board)
        # 将rollout的结果value赋给这个子节点和它的父节点
        # children[index].set_value(value)
        # node.set_value(value)
        ExpandTree(board,node,cur_player,level)


# 找到当前玩家所在节点的孩子，并插入Tree中
# 此时，child节点的最终Board被确定，以及它下在哪个位置，它是哪个玩家下的，这些都被确定了
# 返回值为当前节点以及它的孩子
def PossibleMove(board,node,cur_player):
    # 遍历棋盘格
    # node 是父节点

    subtree=node
    subtree.setExpand(True)
    for i in range(8):
        for j in range(8):
            temp_board = copy.deepcopy(board)
            if temp_board[i][j]==0:  # 找到一个可能的起始位置
                # 搜索八宫格
                flag = 1
                pos=Chess.Position(i,j)
                # 往八个方向搜索，123...8这些代表可能方向
                for direction in range(8):
                    num=MoveSearch(temp_board,pos,direction+1,cur_player,0)  # 最后的0代表中间没有对手的棋
                    # print(num)
                    if num!=0 and flag==1:  # 说明有一个可能的起始位置
                        n=Chess.Node()
                        n.player=cur_player
                        n.setPosition(i,j)
                        n.Board=temp_board
                        subtree.add(n)
                        flag=0
    # subtree.Expand=True
    return subtree


def isTerminal(board, cur_player):
    # 若棋局已经下满棋子
    flag = 0  # 代表棋局没有地方落子
    black=0
    white=0
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                flag = 1
            elif board[i][j] == 1:
                black=black+1
            elif board[i][j] == -1:
                white=white+1
    if flag == 0 or white==0 or black==0:  # 代表已经没有地方落子了
        return True
    return False

# 更改棋盘储存的矩阵上的样子，并进行绘制
def PutChess(root,step):
    node=root
    for i in range(step):
        node=node.children[0]

    node=node.children[0]
    board=node.Board
    # print("game PutChess board")
    # for i in range(8):
    #     print(board[i])
    # print("----------")
    return board
    # 重新绘制图像
    # ChessUI.draw(board,BoardUI,w,h,px,py)
