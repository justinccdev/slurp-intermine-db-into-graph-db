# slurp-intermine-db-into-graph-db

## About
Experiments with slurping data directly from the InterMine database into neo4j then
spitting it out again as RDF

## Programs
`slurp.py` - slurper from InterMine into Neo4J

`spit.py` - spitter from Neo4J as RDF

## Data
The `slurp.py` script is hard-coded to use a database called synbiomine-v5-poc4 (a database created using InterMine for synthetic biology). You can find them at `/micklem/releases/synbiomine/synbiomine-v5-db`
