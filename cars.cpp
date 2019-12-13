// Program to find Dijkstra's shortest path using 
// priority_queue in STL 
#include <vector>
#include <queue>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <random>
#include <algorithm>

using namespace std; 
# define INF 0x3f3f3f3f

const int MAX_DEGREE = 100;
  
struct Edge {
public:
    int n1, n2;

    int count;

    double time() const { 
        return length * (1.0 + count * 0.01 / lanes);
    }
    double time_total() const { 
        return length * (1.0 + max(0, (count - 1)) * 0.01 / lanes);
    }
    int lanes;
    double length;
    Edge(string line) {
        count = 0;
        sscanf(line.c_str(), "%d %d %lf %d", &n1, &n2, &length, &lanes);
    }
};

struct Driver {
    int start, end;
};

// This class represents a directed graph using 
// adjacency list representation 
class Graph 
{ 
    int V;    // No. of vertices 
    vector< vector<Edge> > edges;
    vector<Driver> drivers;
public: 
    Graph(const string& filename, pair<int, int> exclude_node);  // Constructor 
  
    // function to add an edge to graph 
    void addEdge(const Edge& e);
  
    int num_nodes() { return V; }

    // prints shortest path from s 
    double shortestPath(int src, int dest, vector<Edge*>& path);
    double energy();

    void addDriver(int start, int end) {
        drivers.push_back(Driver{start, end});
    }

    void write(const string& outfile) {
        ofstream out(outfile);

        out << energy() << endl;

        for (const vector<Edge>& e : edges) {
            for (const auto& edge : e) {
                out << edge.n1 << ' ' << edge.n2 << ' ' << edge.count << ' ' << edge.time() << endl;
            }
        }
    }
}; 
  
// Allocates memory for adjacency list 
Graph::Graph(const string& filename, pair<int, int> exclude_node)
{
    ifstream infile(filename);
    string line;

    getline(infile, line);

    istringstream iss(line);
    iss >> V;

    for (int i = 0; i < V; i++) {
        vector<Edge> v;
        v.reserve(MAX_DEGREE);
        edges.push_back(v);
    }

    while (getline(infile, line))
    {
        Edge e = Edge(line);
        if (e.n1 == exclude_node.first && e.n2 == exclude_node.second) {
            continue;
        }
        addEdge(e);
    }
}
  
void Graph::addEdge(const Edge& e) 
{
    edges[e.n1].push_back(e);
}


double Graph::energy() {

    double e = 0;

    for (Driver d : drivers) {
        vector<Edge*> p;
        double length = shortestPath(d.start, d.end, p);
        if (std::isinf(length)) {
            e += 10000;
        }
        else {
            e += length;
        }
    }

    return e;
}
  
bool comp(const pair<double, int>& a, const pair<double, int>& b) {
    return a.first > b.first;
}
// Prints shortest paths from src to all other vertices 
double Graph::shortestPath(int src, int dest, vector<Edge*>& path)
{ 
    // Create a priority queue to store vertices that 
    // are being preprocessed. This is weird syntax in C++. 
    // Refer below link for details of this syntax 
    // https://www.geeksforgeeks.org/implement-min-heap-using-stl/ 
    priority_queue< pair<double, int>, vector < pair<double, int> > , decltype(&comp)> pq(comp); 
  
    const int V = edges.size();

    vector<double> dist(V, numeric_limits<double>::infinity());
    vector<int> backward(V, -1);
    vector<Edge*> backward_edges(V, nullptr);
  
    // Insert source itself in priority queue and initialize 
    // its distance as 0. 
    pq.push(make_pair(0, src));
    dist[src] = 0; 
  
    /* Looping till priority queue becomes empty (or all 
      distances are not finalized) */
    while (!pq.empty()) 
    {
        // The first vertex in pair is the minimum distance 
        // vertex, extract it from priority queue. 
        // vertex label is stored in second of pair (it 
        // has to be done this way to keep the vertices 
        // sorted distance (distance must be first item 
        // in pair)
        int u = pq.top().second; 
        pq.pop();

        if (u == dest) {
            int i = dest;

            double cost = 0;

            while (i != src) {
                if (backward_edges[i] != nullptr) {
                    path.push_back(backward_edges[i]);
                    cost += backward_edges[i]->time_total();
                    i = backward[i];
                }
            }
            return cost;
        }
  
        // 'i' is used to get all adjacent vertices of a vertex 
        for (auto& edge : edges[u])
        { 
            //  If there is shorted path to v through u. 
            if (dist[edge.n2] > dist[edge.n1] + edge.time()) 
            {
                // Updating distance of v
                dist[edge.n2] = dist[edge.n1] + edge.time();
                backward[edge.n2] = edge.n1;
                backward_edges[edge.n2] = &edge;
                pq.push(make_pair(dist[edge.n2], edge.n2)); 
            }
        }
    }

    return numeric_limits<double>::infinity();
}
  

double greedy_simulation(Graph& g, int num_drivers) {
    vector<Edge*> path;

    const int EQUILIBRIUM_ITERATIONS = 6;
    vector<int> srcs;
    vector<int> dests;
    std::default_random_engine generator;
    generator.seed(3141);
    std::uniform_int_distribution<int> distribution(0, g.num_nodes() - 1);
    vector< vector<Edge*> > paths;

    for (int i = 0; i < num_drivers;i++) {
        srcs.push_back(distribution(generator));
        dests.push_back(distribution(generator));
        paths.push_back(vector<Edge*>());

        g.addDriver(srcs[i], dests[i]);
    }

    for (int i = 0; i < EQUILIBRIUM_ITERATIONS; i++) {
        for (int j = 0; j < num_drivers; j++) {
            vector<Edge*> shortest;
            for (Edge* e : paths[j]) {
                if (e->count > 0) {
                    e->count--;
                }
            }
            double res = g.shortestPath(srcs[j], dests[j], shortest);
            if (std::isinf(res)) {
                for (Edge* e : paths[j]) {
                    if (e->count > 0) {
                        e->count++;
                    }
                }
                continue;
            }
            for (Edge* e : shortest) {
                e->count++;
            }
            paths[j] = shortest;
        }
    }
    return g.energy();
}

// Driver program to test methods of graph class 
int main(int argc, char** argv) 
{
    if (argc < 6) {
        cerr << "Not enough arguments!" << endl;
        return -1;
    }

    string infile(argv[1]);
    string outfile(argv[2]);

    const int num_cars = atoi(argv[3]);
    const int node_a = atoi(argv[4]);
    const int node_b = atoi(argv[5]);

    Graph g(infile, make_pair(node_a, node_b));
    greedy_simulation(g, num_cars);
    g.write(outfile);
    return 0; 
} 
