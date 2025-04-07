provider "aws" {
  region = "us-east-2"
}

resource "aws_s3_bucket" "model_registry_bucket" {
  bucket = "alberto-model-registry-001"

  tags = {
    Name        = "Memelo Model Registry"
    Environment = "Development"
  }
}

resource "aws_s3_object" "model_object" {
  bucket = aws_s3_bucket.model_registry_bucket.bucket
  key    = "model.tar.gz"
  source = "model.tar.gz"
  acl    = "private"
}

resource "aws_iam_role" "sagemaker_role" {
  name = "sagemaker-model-registry-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "sagemaker_s3_policy" {
  name        = "sagemaker-s3-access-policy"
  description = "Allows SageMaker to access the model registry bucket"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
        Resource = [
          aws_s3_bucket.model_registry_bucket.arn,
          "${aws_s3_bucket.model_registry_bucket.arn}/*",
          "*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_s3_policy" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = aws_iam_policy.sagemaker_s3_policy.arn
}

resource "aws_iam_policy" "sagemaker_ecr_policy" {
  name        = "SageMakerECRPullPolicy"
  description = "Allow SageMaker to pull images from ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ecr_policy" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = aws_iam_policy.sagemaker_ecr_policy.arn
}

resource "aws_sagemaker_model_package_group" "example" {
  model_package_group_name        = "my-model-registry"
  model_package_group_description = "Registry for ML models"
}