import game
import copy
import numpy as np
import math
import random

class Position:
    def __init__(self,x,y):
        self.x=x
        self.y=y

    def setPosition(self,x,y):
        self.x=x
        self.y=y

    def __eq__(self, other):
        if self.x==other.x and self.y==other.y:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.x==other.x and self.y==other.y:
            return False
        else:
            return True

    def __add__(self, other):
        self.x=self.x+other.x
        self.y=self.y+other.y
        return self


class Node:
    def __init__(self):
        self.type = 0
        self.position=Position(-1,-1)
        self.Expand = False  # False：未扩展，为叶子节点 True：已扩展
        self.value=0.0 # value 定义为走了这步棋之后棋面上的己方棋子数-敌方棋子数
        self.N = 0  # 该节点的访问次数
        self.parent=None
        self.children=[]
        self.UCB1_value=self.value
        self.FlagDelete=False # 代表没有被删除
        self.Board=[]
        self.player=0

    def setPosition(self,x,y):
        self.position.x=x
        self.position.y=y

    def setPlayer(self,p):
        self.player=p

    def setParent(self,parent):
        self.parent=parent

    def add(self,node):
        node.setParent(self)
        self.children.append(node)

    # UCB1值相关，
    # 计算UCB1值
    def UCB1(self,sumNum):
        if self.value==0 or self.N==0 or sumNum == 0:
            self.UCB1_value=np.inf
            return self.UCB1_value
        if sumNum==1:
            self.UCB1_value=self.value/np.float(self.N)
        else:
             self.UCB1_value = self.value / np.float(self.N) + np.sqrt(
                    2.0 * math.log(math.e, np.float(sumNum)) / np.float(self.N))
        # print(self.N)
        return self.UCB1_value

    # 设置UCB1值
    def set_UCB1_value(self,num):
        self.UCB1_value=num

    # 获取UCB1值
    def getUCB1(self):
        return self.UCB1_value

########################
    # N相关
    # 增加N值，适用于backup
    def addN(self,num):
        self.N=self.N+num

    def set_N(self,N):
        self.N=N
########################
    def getNode(self):
        return self
########################
    # value 相关
    # 增加value值，适用backup
    def addValue(self,v):
        self.value=self.value+v

    def setValue(self,value):
        self.value=value
########################
    def isExpand(self):
        return self.Expand
    def setExpand(self,value):
        self.Expand=value