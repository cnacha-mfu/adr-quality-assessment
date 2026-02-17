ADR2: Decision to Use MongoDB Replication for High Availability 
 
Title 
Decision to Use MongoDB Replication for High Availability 
 
Context 
Our application requires high availability and fault tolerance to ensure minimal 
downtime. A single database instance creates a single point of failure, which is 
unacceptable for our use case. We need a mechanism that ensures automatic failover 
and data redundancy to maintain system reliability. 
 
Decision 
We have decided to implement MongoDB Replica Sets to enhance availability. A 
Replica Set consists of: 
●​ Primary Node: Handles all write operations. 
●​ Secondary Nodes: Replicate data asynchronously from the Primary. 
●​ Automatic Failover: If the Primary Node fails, a new Primary is elected 
automatically. 
●​ Read Load Balancing: Read operations can be distributed across secondary 
nodes. 
●​ Data Redundancy & Disaster Recovery: Automatic backups through replication 
ensure data safety. 
 
Rationale 
We choose MongoDB replication because it provides a robust solution for ensuring high 
availability, fault tolerance, and data redundancy. A single-node database creates a 
significant risk of downtime in case of failure. With a replica set, we achieve automatic 
failover, allowing uninterrupted service even if a node fails. Additionally, replication 
improves read performance by distributing read operations across secondary nodes. 
 
Consequences 
Pros: 
●​ High availability with automatic failover. 
●​ Load balancing across multiple nodes improves read performance. 
●​ Data redundancy ensures disaster recovery. 
Cons: 
●​ Increased infrastructure costs due to multiple nodes. 
●​ Replication lag can cause slight inconsistencies in real-time applications. 
●​ Network overhead due to continuous data synchronization. 

 
Sample Code 
1.​ Start MongoDB Instances 
mongod --replSet myReplicaSet --port 27017 --dbpath /data/node1 
--bind_ip localhost &​
mongod --replSet myReplicaSet --port 27018 --dbpath /data/node2 
--bind_ip localhost &​
mongod --replSet myReplicaSet --port 27019 --dbpath /data/node3 
--bind_ip localhost & 
 
2.​ Initialize the Replica Set 
mongo --port 27017 
 
rs.initiate(​
  {​
    _id: "myReplicaSet",​
    members: [​
      { _id: 0, host: "localhost:27017" },​
      { _id: 1, host: "localhost:27018" },​
      { _id: 2, host: "localhost:27019" }​
    ]​
  }​
); 
 
3.​ Check Replica Set Status 
rs.status(); 
 
4.​ Set Read Preference for Load Balancing 
db.getMongo().setReadPref("secondaryPreferred"); 
 
5.​ Application Connection to Replica Set 
MongoClient mongoClient = new MongoClient(​
    new 
MongoClientURI("mongodb://localhost:27017,localhost:27018,localhost:2
7019/?replicaSet=myReplicaSet")​
);​
MongoDatabase database = mongoClient.getDatabase("myDB"); 

 
 
6.​ Monitor Replica Set 
mongostat --host localhost:27017
