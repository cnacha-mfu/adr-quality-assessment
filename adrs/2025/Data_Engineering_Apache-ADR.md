Architecture Decision Record: Data 
Engineering Tools 
 
ADR 1: Selecting tools for handle big data 
 
Context 
Our application needs an effective way to store, process, and manage large amounts of data. 
We have been experiencing some challenges due to increasing data volumes, slow processing 
speeds, and difficulties in managing multiple data sources. Among various problems, we are 
considering data engineering tools as a solution. 
 
 
Decision 
We choose a combination of data engineering tools from apache: 
●​ Storage: We use Hadoop Distributed File System (HDFS). 
●​ Processing: Apache Spark for fast data processing. 
●​ Workflow Management: Apache Airflow to automate and schedule data pipelines. 
 
Rationale 
 
●​ Scalability: We choose these tools because it's can handle large data efficiently  
●​ Speed: It can process in a short period of time  
●​ Cost savings: Open source tools reduce expenses while developing applications  
 
Consequences 
Pros: 
●​ Fast data processing  
●​ Distributing data in storage  
●​ Better data quality  
●​ Easy to integrate with other tools  
Cons: 
●​ Setup and maintenance require expertise  
●​ Need training to effectively use these tools 
●​ Continuously monitoring and maintaining are necessary  
 

Sample code 
 
Hadoop setup in command prompt 
 
●​ Create ubuntu user : “tan” , use password as “tan” 
 
useradd tan 
passwd tan 
 
●​ Create home directory put  user tan in group sudo 
mkhomedir_helper tan 
usermod -aG sudo tan 
 
●​ Create SSH Channel for Hadoop 
ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa 
 
●​ Install Hadoop 
sudo mkdir -p /usr/local/hadoop 
sudo chown tan:tan -R /usr/local/hadoop 
sudo mkdir /var/log/hadoop 
sudo chown -R tan:tan /var/log/hadoop 
 
sudo mkdir -p /var/hadoop_data 
sudo mkdir -p /var/hadoop_data/namenode 
sudo mkdir -p /var/hadoop_data/datanode 
sudo chown tan:tan -R /var/hadoop_data 
wget 
https://archive.apache.org/dist/hadoop/core/hadoop-2.7.3/hadoop-
2.7.3.tar.gz 
 

tar -xvf hadoop-2.7.3.tar.gz 
cd hadoop-2.7.3/ 
sudo mv * /usr/local/hadoop 
Cd 
cd 
vi .bashrc  
 
export HADOOP_HOME=/usr/local/hadoop 
export PATH=$PATH:$HADOOP_HOME/bin 
export PATH=$PATH:$HADOOP_HOME/sbin 
 
●​ Use environment that already setup 
 
source .bashrc 
 
export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64 
export HADOOP_LOG_DIR=/var/log/hadoop 
 
export YARN_LOG_DIR=/var/log/hadoop 
 
 
 
Sample code of Apache Spark in Python 
 
from pyspark import SparkContext 
 
# Create SparkContext 
sc = SparkContext("local", "First Spark App") 
 
# Prepare data (this could be files, databases, or data on memory). 
data = [1, 2, 3, 4, 5] 
distData = sc.parallelize(data) 
 
# processing 
result = distData.reduce(lambda a, b: a + b) 
 
# output 
print(result) 
 
# stop SparkContext 
sc.stop() 
 
 

Architecture Decision Record: Machine 
Learning with Apache Spark 
 
ADR 2: Using Apache Spark for Machine 
Learning 
Context  
Application requires a scalable and efficient method for processing large datasets to train 
machine learning (ML) models. The increasing complexity and volume of data make it 
challenging to manage ML workflows efficiently. We need a data engineering tool that can 
handle distributed data processing, support ML workloads, and integrate seamlessly with our 
existing big data infrastructure. 
Decision  
We choose Apache Spark's MLlib for handling machine learning tasks. This decision aligns with 
our data processing architecture, which already leverages Apache Spark for fast and scalable 
computation. 
Rationale 
●​ Scalability: Spark MLlib supports distributed training, allowing us to process large 
datasets efficiently. 
●​ Integration: Since we already use Spark for data processing, using Spark MLlib for ML 
ensures smooth integration. 
●​ Performance: In-memory computation in Spark speeds up ML training and reduces 
latency. 
●​ Cost Savings: As an open-source tool, Spark MLlib minimizes infrastructure and 
licensing costs. 
Consequences  
Pros: 
●​ Enables distributed ML training at scale 
●​ Optimized for large-scale data processing 
●​ Seamless integration with existing Apache Spark workflows 
●​ Provides built-in ML algorithms and utilities 

Python
Cons: 
●​ Requires expertise to optimize and tune models for performance 
●​ More complex setup compared to standalone ML libraries 
●​ Continuous monitoring and maintenance required for production environments 
Sample code 
Apache Spark MLlib for Linear Regression 
from pyspark.sql import SparkSession 
from pyspark.ml.regression import LinearRegression 
from pyspark.ml.feature import VectorAssembler 
 
spark = SparkSession.builder.appName("MLlib 
Example").getOrCreate() 
 
data = spark.read.csv("data.csv", header=True, inferSchema=True) 
 
assembler = VectorAssembler(inputCols=["feature1", "feature2"], 
outputCol="features") 
assembled_data = assembler.transform(data) 
 
train_data, test_data = assembled_data.randomSplit([0.8, 0.2], 
seed=42) 
 
lr = LinearRegression(featuresCol="features", labelCol="label") 
model = lr.fit(train_data) 
 
predictions = model.transform(test_data) 
predictions.select("features", "label", "prediction").show() 
 
spark.stop()
