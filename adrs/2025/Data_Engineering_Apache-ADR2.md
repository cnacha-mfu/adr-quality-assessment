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

Python
●​ Provides built-in ML algorithms and utilities 
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
