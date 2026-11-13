#  import existing ecr repository to avoid recreating them
import {
  to = aws_ecr_repository.entries_api
  id = "entries-api"
}

import {
  to = aws_ecr_lifecycle_policy.entries_api
  id = "entries-api"
}

resource "aws_ecr_repository" "entries_api" {
  name                 = "entries-api"
  image_tag_mutability = "MUTABLE"

  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = false
  }

  lifecycle {
    prevent_destroy = true # protects the existing repo from accidental deletion
  }
}

resource "aws_ecr_lifecycle_policy" "entries_api" {
  repository = aws_ecr_repository.entries_api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the last 3 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
