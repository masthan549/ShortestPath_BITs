from collections import deque, namedtuple
import os, sys


# we'll use infinity as a default distance to nodes.
inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')


def make_edge(start, end, cost=1):
  return Edge(start, end, cost)


class Graph:
    def __init__(self, edges):
        # let's check that the data is right
        wrong_edges = [i for i in edges if len(i) not in [2, 3]]
        if wrong_edges:
            raise ValueError('Wrong edges data: {}'.format(wrong_edges))

        self.edges = [make_edge(*edge) for edge in edges]

    @property
    def vertices(self):
        return set(
            sum(
                ([edge.start, edge.end] for edge in self.edges), []
            )
        )

    def get_node_pairs(self, n1, n2, both_ends=True):
        if both_ends:
            node_pairs = [[n1, n2], [n2, n1]]
        else:
            node_pairs = [[n1, n2]]
        return node_pairs

    def remove_edge(self, n1, n2, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        edges = self.edges[:]
        for edge in edges:
            if [edge.start, edge.end] in node_pairs:
                self.edges.remove(edge)

    def add_edge(self, n1, n2, cost=1, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        for edge in self.edges:
            if [edge.start, edge.end] in node_pairs:
                return ValueError('Edge {} {} already exists'.format(n1, n2))

        self.edges.append(Edge(start=n1, end=n2, cost=cost))
        if both_ends:
            self.edges.append(Edge(start=n2, end=n1, cost=cost))

    @property
    def neighbours(self):
        neighbours = {vertex: set() for vertex in self.vertices}
        for edge in self.edges:
            neighbours[edge.start].add((edge.end, edge.cost))

        return neighbours

    def dijkstra(self, source, dest):
        assert source in self.vertices, 'Such source node doesn\'t exist'
        distances = {vertex: inf for vertex in self.vertices}
        previous_vertices = {
            vertex: None for vertex in self.vertices
        }
        distances[source] = 0
        vertices = self.vertices.copy()

        while vertices:
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])
            vertices.remove(current_vertex)
            if distances[current_vertex] == inf:
                break
            for neighbour, cost in self.neighbours[current_vertex]:
                alternative_route = distances[current_vertex] + cost
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        return path

def checkIfInputFileDataIncorrectInfo(routeInfoList, HospitalStartNode, AirportEndNode):

    errorConditionExist = False
    global outputPS6_fPtr

    #Ensure Start and End node shouldnt be NULL
    if HospitalStartNode is None:
        outputPS6_fPtr.write("Hospital node (or start node) cannot be empty or exist in input file with proper format")
        errorConditionExist = True

    if AirportEndNode is None:
        outputPS6_fPtr.write("Airport node (or end node) cannot be empty or exist in input file with proper format")
        errorConditionExist = True

    #check if start and end nodes are in given route list
    startNodeExistInGraph = False
    endNodeExistInGraph = False

    for indx in routeInfoList:
        if (HospitalStartNode in indx) and (startNodeExistInGraph is False):
            startNodeExistInGraph = True
        if (AirportEndNode in indx) and (endNodeExistInGraph is False):
            endNodeExistInGraph = True

    if (errorConditionExist is False) and ((startNodeExistInGraph is False) or (endNodeExistInGraph is False)):
        outputPS6_fPtr.write("Make sure Hospital Start Node and Airport End Node exist in given route graph")
        errorConditionExist = True

    return errorConditionExist

def readRouteInfoFromInputFile():

    routeInfoList = []
    HospitalStartNode = None
    AirportEndNode = None
    global outputPS6_fPtr

    try:
        fPtr = open("inputPS6.txt")

        for fileLineInfo in fPtr.readlines():
            dirConnRoute = []
            if fileLineInfo.strip():

                #Check if it is route information
                splitInfoList = fileLineInfo.split("/")
                if len(splitInfoList) == 3:
                    dirConnRoute.append(splitInfoList[0].strip())
                    dirConnRoute.append(splitInfoList[1].strip())
                    dirConnRoute.append(int(splitInfoList[2].strip()))


                    routeInfoList.append(tuple(dirConnRoute))

                #Check if the information is of type start and end node
                splitInfoList = fileLineInfo.split(":")
                if (splitInfoList[0].strip() == "Hospital Node") and (HospitalStartNode is None):
                    HospitalStartNode = splitInfoList[1].strip()
                elif (splitInfoList[0].strip() == "Airport Node") and (AirportEndNode is None):
                    AirportEndNode = splitInfoList[1].strip()

        return routeInfoList, HospitalStartNode, AirportEndNode;
    except:
        outputPS6_fPtr.write("make sure inputPS6.txt file available in current directory.")
        sys.exit(0)

def findMinimumTravelDist(shortestPath, routeList):

    minimumTravenDist = 0
    for indxVertex in range(0, len(shortestPath)-1):
        for indxCost in routeList:
            if ((shortestPath[indxVertex] in indxCost) and (shortestPath[indxVertex+1] in indxCost)):
                minimumTravenDist = minimumTravenDist + indxCost[2]
                break

    return minimumTravenDist

if __name__ == "__main__":

    os.chdir(".")
    routeList = []
    StartNode = None
    EndNode = None
    outputPS6_fPtr = open("outputPS6.txt", 'w')

    #Read city route information from text file
    routeList,StartNode,EndNode = readRouteInfoFromInputFile()

    #check Error Data
    errorExist = checkIfInputFileDataIncorrectInfo(routeList,StartNode,EndNode)

    if errorExist is True:
        sys.exit(0)

    #Set the graph with given vertex and its cost
    graph = Graph(routeList)

    #Run dijkstra on given graph
    shortestPathObj = graph.dijkstra(StartNode, EndNode)
    shortestPath = []
    for indx in shortestPathObj:
        shortestPath.append(indx)

    minDistance = findMinimumTravelDist(shortestPath, routeList)


    outputPS6_fPtr.write("Shortest route from the hospital "+StartNode+" to reach the airport "+EndNode+" is " +str(shortestPath))
    outputPS6_fPtr.write("\nand it has minimum travel distance "+str(minDistance)+"km")
    outputPS6_fPtr.write("\nit will take "+str((minDistance/80)*60)+" minutes for the ambulance to reach the airport.")
    outputPS6_fPtr.close()