# Terraform foundation

This folder intentionally provisions only the reusable foundation:

- ECR repositories;
- ECS cluster;
- CloudWatch log group;
- API workload role with Bedrock invoke permission.

A production environment should add environment-specific networking, ALB/API Gateway, ECS services/task definitions, RDS PostgreSQL for LangGraph checkpoints/application data, Secrets Manager, KMS keys, WAF, Verified Permissions/PDP integration and private connectivity as required.

The repository avoids inventing a networking topology because VPC/subnet/private-endpoint constraints are organization-specific and should be decided through an ADR.
