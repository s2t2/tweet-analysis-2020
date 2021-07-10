
# Deploying to AWS

Heroku is super expensive. So let's try to deploy to [AWS](https://aws.amazon.com/).

First, sign up for an AWS "root account". Provide credit card info.

# Creating a Server

Create a new ec2 server
  + AMI: "Amazon Linux 2"
  + Tier: t2.micro

Generate a key pair and download it. Move a copy into the root directory of this repo as "ResearchKeys0.pem" or something.

Note the server's IP address.

# Logging In

```sh
ssh -i ResearchKeys0.pem ec2-user@ip-address
```

Running into "Permissions 0644 for 'ResearchKeys0.pem' are too open."

```sh
chmod 400 ResearchKeys0.pem
```

# Deploying

  + https://docs.aws.amazon.com/codedeploy/latest/userguide/tutorials-github.html
  + https://medium.com/innovation-incubator/deploying-code-from-github-to-aws-ec2-with-codepipeline-4639e8fbba28
