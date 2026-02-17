ADR 2: Using Amazon S3 for Unstructured Data Storage 
 
Context 
Our system requires a scalable and cost-effective solution to store and 
manage unstructured data, such as images, videos, logs, and backups. The solution 
should support lifecycle management, security, and easy access. 
 
Decision 
​
We will use Amazon S3 (Simple Storage Service) as our primary storage for 
unstructured data. 
 
Rationale 
●​ Scalability: Virtually unlimited storage capacity. 
●​ Durability: 99.999999999% (11 nines) data durability. 
●​ Security: Supports encryption, IAM policies, and bucket policies. 
●​ Lifecycle Management: Automatic archiving to Amazon Glacier for cost 
optimization. 
●​ Easy Integration: Compatible with AWS Lambda, CloudFront, and AI/ML 
services. 
 
Consequences 
Cros 
●​ Reduces infrastructure complexity. 
●​ Ensures high availability and data protection. 
●​ Enables cost savings with lifecycle policies. 
 
Pros 
●​ Latency may be higher than block storage (EBS). 
●​ Data transfer costs apply for frequent cross-region access. 
 
Sample Code 
1. Add AWS SDK Dependency (Maven) 
 
<dependency> 
    <groupId>software.amazon.awssdk</groupId> 
    <artifactId>s3</artifactId> 
    <version>2.17.89</version> 
</dependency> 
 
 
 
 

2. Upload File to S3 
 
import software.amazon.awssdk.services.s3.S3Client; 
import 
software.amazon.awssdk.services.s3.model.PutObjectRequest; 
import software.amazon.awssdk.core.sync.RequestBody; 
import java.nio.file.Paths; 
 
public class S3Service { 
    private final S3Client s3 = S3Client.create(); 
    private final String bucketName = "your-bucket-name"; 
 
    public void uploadFile(String filePath, String keyName) { 
        s3.putObject(PutObjectRequest.builder() 
                .bucket(bucketName) 
                .key(keyName) 
                .build(), 
                RequestBody.fromFile(Paths.get(filePath))); 
 
        System.out.println("File uploaded successfully!"); 
    } 
}
