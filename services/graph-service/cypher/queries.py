GET_SUBGRAPH_QUERY = """
MATCH (n)-[r]->(m)
WHERE elementId(n) = $node_id OR n.id = $node_id
RETURN n, r, m
LIMIT 100
"""

GET_RECOMMENDATIONS_QUERY = """
MATCH (n)-[*1..2]-(m)
WHERE n.id = $node_id
RETURN m, count(*) as weight
ORDER BY weight DESC
LIMIT 10
"""

GET_PROJECT_GRAPH = """
MATCH (p:Project {id: $project_id})-[:DEPENDS_ON|GENERATED_FROM*1..3]-(related)
RETURN p, related
"""

GET_PATENT_LANDSCAPE = """
MATCH (p:Patent)-[:USES]->(t:Technology)
WHERE p.id = $patent_id
MATCH (t)<-[:USES]-(other:Patent)
RETURN p, t, other
LIMIT 50
"""

GET_SHORTEST_PATH = """
MATCH p = shortestPath((startNode {id: $start_id})-[:CITES|RELATED_TO|USES*]-(endNode {id: $end_id}))
RETURN p
"""

