resource "aws_s3_bucket" "example" {
  bucket = "alberto-renteria-terraform-bucket"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}
