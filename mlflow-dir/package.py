import boto3

# AWS region
region = "us-east-2"

# SageMaker client
sagemaker_client = boto3.client("sagemaker", region_name=region)

# Registrar el model package
response = sagemaker_client.create_model_package(
    ModelPackageGroupName="my-model-registry",
    ModelPackageDescription="My first model version",
    InferenceSpecification={
        "Containers": [
            {
                "Image": "763104351884.dkr.ecr.us-east-2.amazonaws.com/pytorch-inference:1.5.0-cpu-py3",
                "ModelDataUrl": "s3://alberto-model-registry-001/model.tar.gz",
            }
        ],
        "SupportedContentTypes": ["application/json"],
        "SupportedResponseMIMETypes": ["application/json"],
    },
    ModelApprovalStatus="PendingManualApproval",
)

# Imprimir el ARN del model package
model_package_arn = response['ModelPackageArn']
print(f"Model Registered! ARN: {model_package_arn}")

# Aprobar el model package
response_approve = sagemaker_client.update_model_package(
    ModelPackageArn=model_package_arn,
    ModelApprovalStatus="Approved"
)
print("Model approved!")

# Crear el modelo usando el model package aprobado
model_name = "my-model"
execution_role = "arn:aws:iam::211125785534:role/sagemaker-model-registry-role"  # Reemplaza con tu role de SageMaker
model_response = sagemaker_client.create_model(
    ModelName=model_name,
    PrimaryContainer={
        "ModelPackageName": model_package_arn
    },
    ExecutionRoleArn=execution_role
)
print(f"Model Created! Name: {model_name}")