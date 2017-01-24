# Lambda Environment Variable Encryptor

Lambda Function to encrypt secret environment variables of Lambda Functions.

This Function is integrated with CodePipeline to encrypt secret values after target Lambda Functions are successfully deployed.

Please see this for more details on how to integrate Lambda Functions in CodePipeline,
http://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-lambda-integration.html#how-to-lambda-integration-add-action

![aws-services][aws-services-image]

## How To Setup a CodePipeline

- First, create a S3 Bucket where the deployment files will be uploaded with below naming convention. *(You can use a different convention, but you need to add a permission for the CodeBuild to access this S3 bucket)*.

  >

      codepipeline-<region>-<account_num>-<project_name>

  like

      codepipeline-us-east-1-9999999999-aws-services-encryption


- Follow the steps in http://docs.aws.amazon.com/lambda/latest/dg/automating-deployment.html along with an additional step to set an environment variable under 'Advanced' setting when creating a new project in CodeBuild

  > S3_BUCKET_NAME : S3 bucket name you created above


## How To Test Lambda Functions

- $ cd tests
- $ python test.py

## [![Sungard Availability Services | Labs][labs-logo]][labs-github-url]

This project is maintained by the Labs group at [Sungard Availability
Services](http://sungardas.com)

GitHub: [https://sungardas.github.io](https://sungardas.github.io)

Blog:
[http://blog.sungardas.com/CTOLabs/](http://blog.sungardas.com/CTOLabs/)

[labs-github-url]: https://sungardas.github.io
[labs-logo]: https://raw.githubusercontent.com/SungardAS/repo-assets/master/images/logos/sungardas-labs-logo-small.png
[aws-services-image]: ./docs/images/logo.png?raw=true
