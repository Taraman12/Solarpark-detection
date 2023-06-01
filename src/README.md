### Deployment:
Don't forget to add IAM role in AWS Elastic Beanstalk

Role EC2

add SSH port 22 in security group

do not select default security group (Create a new one instead, and add SSH port 22)

#### NOTE: eb cli will use the main branch for deployment
even if you are on a different branch

CMD eb init
choose location
Frankfurt (eu-central-1)
choose application
choose platform -> Docker 3
choose platform branch -> Docker running on 64bit Amazon Linux 2
continue woth CodeCommit -> no
Do you want to set up SSH for your instances? -> yes
keypair name -> eb-keypair (or any other name)
Enter pasphrase -> empty for no passphrase
same for confirm passphrase
NOTE: The ssh keypair will be generated in the .ssh folder in your home User directory (C:\Users\username\.ssh\eb-keypair)

CMD eb create --service-role aws-elasticbeanstalk-service-role
environment name -> eb-env
DNS CNAME prefix -> eb-env
Select a load balancer type -> 2
enable spot fleet -> no

CMD eb status eb-env

CMD eb health eb-env

 eb logs --zip