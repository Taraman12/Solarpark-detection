### Deployment:
Don't forget to add IAM role in AWS Elastic Beanstalk

Role EC2

add SSH port 22 in security group

do not select default security group (Create a new one instead, and add SSH port 22)

Make sure your ec2 instance are in the same VPC and subnet!
Also activate the inbound rules for the security group of the ec2 instance (so all instances with the same security group can communicate with each other)

If you create a new VPC and subnet, you need also create a new internet gateway and attach it to the VPC.
Then you need to create a new route table and add the internet gateway to it.
Then you need to add the route table to the subnet.

Also add outbound rules to the security group of the ec2 instance on port 8000 so that the api can connect with aws to get the credentials for IAM.

A more detailed explanation will be added in the future.

### secrurity group for ec2 instance
https://aws.plainenglish.io/using-aws-to-create-a-docker-swarm-b48731c850c

### Deploy containers with docker swarm
Set up docker swarm on ec2 instance
```bash
docker swarm init --advertise-addr <private ip address of ec2 instance>
```
Join docker swarm on other ec2 instances
```bash
docker swarm join --token <token> <private ip address of ec2 instance>:2377
```
OR
```bash
client.swarm.join(remoteAddrs, opts, callback)
```
Create overlay network in docker compose file:
https://stackoverflow.com/questions/71034142/is-it-possible-to-create-an-external-attachable-overlay-network-from-within-a-do

Create docker network
```bash
docker network create --driver overlay --attachable mynetwork
```
Deploy containers
NOTE: stack deploy does not work with .env files so here is a workaround
(see more here: https://github.com/moby/moby/issues/29133)
all variables in the .env file need an export in front of them
```bash
source .env
envsubst < docker-compose.yml | sudo docker stack deploy -c - main
```

Remove containers
```bash
docker stack rm main
```


### Debugging
```bash
sudo docker service logs -f -t [SERVICE]
```

### Deploying to AWS Elastic Beanstalk
#### NOTE: eb cli will use the main branch for deployment
even if you are on a different branch locally

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

 eb logs --all "name of the environment"
