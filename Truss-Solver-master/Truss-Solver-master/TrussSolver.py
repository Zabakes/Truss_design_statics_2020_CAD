import numpy as np
import numpy.linalg as la 
import math as mt 
import pygame as pg 
import matplotlib.pyplot as plt

def checkInMembers(members, relation):
    i = relation[0]
    j = relation[1]
    output = False
    for n in members:
        if (i in n) and (j in n):
            output = True
    return output


class Truss:
    def __init__(self,nodes_, connections_):
        self.nodes = nodes_
        self.connections = connections_

        N = len(nodes_)

        self.loads = np.zeros(N*2)
        self.bars = []
        j = 0
        for connection in connections_:
            for i in connection:
                if not checkInMembers(self.bars,[i,j]):
                    self.bars.append([i,j])
            j += 1
        nForces = len(self.bars)
        self.G = np.zeros((2*N,nForces))
        self.F = np.zeros(len(self.bars))

        for i in range(2*N):
            if (i%2 == 0): #El indice de nodo es par por lo tanto se trata de la suma en x
                iNode = int(i/2)
                for iForce in range(nForces):
                    if iNode in self.bars[iForce]:
                        bar = list(self.bars[iForce])
                        bar.remove(iNode)
                        j = bar[0]
                        self.G[i,iForce] = self.c(iNode,j)
                    else:
                        self.G[i,iForce] = 0
            else : #El indice de nodo es impar por lo tanto se trata de la suma en y
                iNode = int((i-1)/2) 
                for iForce in range(nForces):
                    if iNode in self.bars[iForce]:
                        bar = list(self.bars[iForce])
                        bar.remove(iNode)
                        j = bar[0]
                        self.G[i,iForce] = self.s(iNode,j)
                    else:
                        self.G[i,iForce] = 0
                                           

    def addLoad(self,node, load):
        iX = node*2
        iY = node*2 + 1
        self.loads[iX] = -load[0]
        self.loads[iY] = -load[1]
    
    def c(self, i, j):
        x0 = self.nodes[i][0]
        x1 = self.nodes[j][0]
        y0 = self.nodes[i][1]
        y1 = self.nodes[j][1]

        d = mt.sqrt( (x0 - x1)**2 + (y0 - y1)**2 )

        if d == 0:
            return 0
        else:
            return (x1 - x0)/d

    def s(self, i, j):
        x0 = self.nodes[i][0]
        x1 = self.nodes[j][0]
        y0 = self.nodes[i][1]
        y1 = self.nodes[j][1]

        d = mt.sqrt( (x0 - x1)**2 + (y0 - y1)**2 )
        if d == 0:
            return 0
        else:
            return (y1 - y0)/d
    
    def k(self, i, j):
        if j in self.connections[i]:
            return 1
        else:
            return 0

    def solve(self):

        lst = la.lstsq(self.G, self.loads , rcond=None)
        fmax = 0
        fmax_tension = 0
        for force in lst[0]:
            if abs(force) > fmax:
                fmax = abs(force)
        for force in lst[0]:
            if force > fmax_tension:
                fmax_tension = force

        self.result = lst[0]
        self.fmax = fmax
        self.fmax_tension = fmax_tension


    def truss_weight(self):
        density = 1
        total_weight = 0
        for bar in self.bars:
            total_weight += density * mt.sqrt( (  self.nodes[bar[0]][0] - self.nodes[bar[1]][0] )**2 + (  self.nodes[bar[0]][1] - self.nodes[bar[1]][1]  )**2 )
        self.weight = total_weight
        self.ltw_tension = 1000 * 1/(self.fmax_tension * self.weight)
        self.ltw = 1000 * 1/(self.fmax * self.weight)
        return total_weight
        

class PgTruss:
    def __init__(self,truss_,screenSize_):
        self.truss = truss_
        self.xmaxS = screenSize_
        self.margin = 100
        xmaxR = 0
        ymaxR = 0
        for nodei in truss_.nodes:
            for nodej in truss_.nodes:
                if abs(nodei[0] - nodej[0]) > xmaxR:
                    xmaxR = abs(nodei[0] - nodej[0])
                if abs(nodei[1] - nodej[1]) > ymaxR:
                    ymaxR = abs(nodei[1] - nodej[1])

        self.xmaxR = xmaxR
        self.ymaxR = ymaxR 
        self.scale =(self.xmaxS - 2*self.margin)/xmaxR
        self.ymaxS = int((self.scale * self.ymaxR) + self.margin*2)
        pg.init()
        self.screen = pg.display.set_mode((self.xmaxS,self.ymaxS))

    def drawNodes(self):
        

        fig, ax = plt.subplots()

        screenNodes = []
        nodeIndx = 0
        for node in self.truss.nodes:
            screenNodes.append([node[0],node[1]])
            ax.scatter(node[0], node[1])
            xloadI = 2*nodeIndx
            yloadI = xloadI + 1
            if self.truss.loads[xloadI] != 0 or self.truss.loads[yloadI] != 0 :
                loadx = 0 - self.truss.loads[xloadI]
                loady = 0 - self.truss.loads[yloadI]
                text = " P" + str(nodeIndx) + " = " + str(round(loady,3)) 
                ax.annotate(text, xy = (node[0] - 10, node[1] - 25))
            nodeIndx += 1
            
            
        self.screenPoints = screenNodes

        barIndx = 0
        for bar in self.truss.bars:
            pointA = self.screenPoints[bar[0]]
            pointB = self.screenPoints[bar[1]]
            midPointx = int((pointA[0] + pointB[0])/2)
            midPointy = int((pointA[1] + pointB[1])/2)

            forceBar = round(self.truss.result[barIndx],2)
            if forceBar>0:
                color = 'r'
            else:
                color = 'b'

            ax.plot([pointA[0], pointB[0]], [pointA[1], pointB[1]], c = color)

            ax.annotate(forceBar, xy = (midPointx, midPointy))
            barIndx += 1
        
            return fig



