
# Deploying to AWS

Heroku is super expensive. So let's try to deploy to [AWS](https://aws.amazon.com/).

First, sign up for an AWS "root account". Provide credit card info.

## Creating a Server

Create a new ec2 server
  + AMI: "Amazon Linux 2"
  + Tier: t2.micro

Generate a key pair and download it. Move a copy into the root directory of this repo as "ResearchKeys0.pem" or something.

Note the server's IP address.

## Logging In

[Access the instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html):

```sh
ssh -i ResearchKeys0.pem ec2-user@ip-address
```

Running into "Permissions 0644 for 'ResearchKeys0.pem' are too open." Fix permissions:

```sh
chmod 400 ResearchKeys0.pem
```

Then login again.

## Preparing to Deploy

Once logged-in, [Verify the CodeDeploy agent is running"](https://docs.aws.amazon.com/codedeploy/latest/userguide/codedeploy-agent-operations-verify.html):

```sh
sudo service codedeploy-agent status
sudo service codedeploy-agent start
```

It is not. So [Lookup region and bucket](https://docs.aws.amazon.com/codedeploy/latest/userguide/resource-kit.html#resource-kit-bucket-names).
 then [Install CodeDeploy](https://docs.aws.amazon.com/codedeploy/latest/userguide/codedeploy-agent-operations-install-linux.html):

```sh
sudo yum update
sudo yum install ruby
sudo yum install wget

#wget https://bucket-name.s3.region-identifier.amazonaws.com/latest/install
wget https://aws-codedeploy-us-east-2.s3.us-east-2.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto

sudo service codedeploy-agent status
```


Alright we have installed the CodeDeploy agent.

## Preparing Repo for Deploy

  + https://docs.aws.amazon.com/codedeploy/latest/userguide/application-revisions-plan.html
  + https://docs.aws.amazon.com/codedeploy/latest/userguide/application-revisions-appspec-file.html




## Deploying

  + https://docs.aws.amazon.com/codedeploy/latest/userguide/tutorials-github.html
  + https://medium.com/innovation-incubator/deploying-code-from-github-to-aws-ec2-with-codepipeline-4639e8fbba28
