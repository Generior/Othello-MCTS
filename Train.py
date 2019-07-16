import copy
import random
import game

# Train结束后，剩下该步唯一一棵子树
def TrainNode(board,root,iterNum,cur_player,step):
    for i in range(iterNum):
        # print(i)
        SumNum = root.N  # 树的根节点的访问次数，如果已经下了一步棋，就把其他的children给删除
        node = root  # node作为指向root的指针
        temp_player=cur_player
        while node.isExpand() == True:  # 已扩展，不是叶子节点
            # 有孩子
            if node.children: # 要进入就为真，当存在值的时候为真
                CalculateUCB1(node, SumNum)  # 计算node所有孩子的UCB1值
                index = MaxUCB1(node)  # 获得node孩子中的UCB1值最大的那个节点的下标
                node = node.children[index]  # 把指针指向最大的孩子
            # 没有孩子
            else:
                temp_player=-node.player
                node=game.PossibleMove(node.Board,node,temp_player)
                if not node.children:
                    break
        # 未扩展，是叶子节点？
        value=Rollout(node,cur_player,node.Board)  # 获得叶子节点后，对节点进行rollout,获得最终的value，其中，要将node的Expand值改为True
        BackUp(node,value,cur_player)  # 对叶子节点和它的所有的祖先的value和N都更新一遍
    # 扩展结束后，选择root的孩子中最大的那个
    index = MaxUCB1(root)
    # 选择了之后，就把同一个父母的其他孩子给删除
    DeleteChildren(root,index,step)
    # return index
    return


def DeleteChildren(root,index,step):
    # 删除第step步的子树
    node=root
    # 找到要删除其他节点的那一层（此时，默认之前所有的节点都是只有一个孩子的）
    for i in range(step):
        node=node.children[0]
    # 第一种方法，真正的删除，释放空间
    tempNode=node.children[index]
    node.children.clear()
    node.children.append(tempNode)

def CalculateUCB1(node,SumNum):
    for i in range(len(node.children)): # 遍历这一个节点的所有孩子，并计算她的UCB1值
        node.children[i].set_UCB1_value(node.children[i].UCB1(SumNum)) # UCB1要传入总访问次数


# 返回节点下children的UCB1值最大的那个子节点的下标
def MaxUCB1(node):
    # 将这个节点下的所有的children的值比较一遍，选择值最大的那个孩子的下标
    index=0
    max=0
    for i in range(len(node.children)):
        # 如果有UCB1值一样大的，就选择下标更加靠前的那个孩子
        if max<node.children[i].getUCB1():
            index=i
            max=node.children[i].getUCB1()
    return index


# 返回黑子的最终value
def Rollout(node,cur_player,board):
    # 进行一个快速的选择，随机选择children并深入，直到游戏结束
    temp_board=copy.deepcopy(board)
    temp_player = -cur_player
    list=[]
    # subTree=node
    flag=1
    while game.isTerminal(temp_board,temp_player)==False:
        # 因为都是叶子节点，所以没有孩子，并且孩子不放入正式的树中
        list.clear()
        # 这里可以优化，不过现在先不动
        if node.children:
            list = node.children
        else:
            node = game.PossibleMove(temp_board, node, temp_player)
            list=node.children

        if list: # 如果list中有内容，那么就随机选择能下的地方并下
            index = getRandomChild(len(list))  # 随机选择了能下的地方
            # 将棋盘更新为选择的棋盘，将下棋的人变更。将
            temp_board = node.children[index].Board
            temp_player = -node.children[index].player
            node=node.children[index]

        else: # 如果没有地方可以下，那么就换成对方下棋
            temp_player=-temp_player
            # print("temp_player:"+str(temp_player))
            if flag==1:
                flag=flag-1
            elif flag==0:
                break

    # 当下棋结束，统计现有棋面上各个子的数量
    blackNum=0
    whiteNum=0
    for i in range(8):
        for j in range(8):
            if temp_board[i][j]==1:
                blackNum=blackNum+1
            elif temp_board[i][j]==-1:
                whiteNum=whiteNum+1
    # 因为只有黑子是需要进行rollout的，所以只返回黑子的最终value
    return blackNum-whiteNum

# 返回随机一个孩子
def getRandomChild(length):
    random_choice= random.randint(0,length-1)
    return random_choice

# 回传值，但是不返回
def BackUp(node,value,cur_player):
    node.addValue(value)
    node.setExpand(True)
    node.addN(1)
    # 可以优化的地方
    if not node.children:
        node=game.PossibleMove(node.Board,node,-node.player)
    while node.parent: # 如果节点存在父节点，就把值往回传
        node.parent.addValue(value)
        node.parent.addN(1)
        node=node.parent
