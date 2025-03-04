################################################################################
# VPC
################################################################################

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags       = var.tags
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = var.tags
}

################################################################################
# Security Group
################################################################################

resource "aws_security_group" "main" {
  name        = "${var.project}-default"
  description = "Allows resources to access the internet"
  vpc_id      = aws_vpc.main.id
  tags        = var.tags
}

resource "aws_vpc_security_group_egress_rule" "main" {
  security_group_id = aws_security_group.main.id
  ip_protocol       = -1
  cidr_ipv4         = "0.0.0.0/0"
}

################################################################################
# Cloudwatch Log Group
################################################################################

resource "aws_cloudwatch_log_group" "flow_logs" {
  name              = "${var.project}-flow-logs"
  retention_in_days = 1
  tags              = var.tags
}

################################################################################
# IAM Role
################################################################################

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "main" {
  name               = "${var.project}-flow-log"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "traffic_log" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams"
    ]
    resources = ["${aws_cloudwatch_log_group.flow_logs.arn}:*"]
  }
}

resource "aws_iam_policy" "traffic_log_policy" {
  name        = "${var.project}-flow-log-policy"
  description = "Policy for allowing flow log to log to CloudWatch"
  policy      = data.aws_iam_policy_document.traffic_log.json
}

resource "aws_iam_role_policy_attachment" "main" {
  role       = aws_iam_role.main.name
  policy_arn = aws_iam_policy.traffic_log_policy.arn
}

################################################################################
# Flow Log
################################################################################

resource "aws_flow_log" "main" {
  traffic_type             = "ALL"
  iam_role_arn             = aws_iam_role.main.arn
  log_destination          = aws_cloudwatch_log_group.flow_logs.arn
  max_aggregation_interval = 60
  vpc_id                   = aws_vpc.main.id
  tags                     = var.tags
}

################################################################################
# Subnets
################################################################################

resource "aws_subnet" "public" {
  count             = length(["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"])
  cidr_block        = element(["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"], count.index)
  vpc_id            = aws_vpc.main.id
  availability_zone = element(["us-east-2a", "us-east-2b", "us-east-2c"], count.index)
  tags              = var.tags
}

resource "aws_subnet" "private" {
  count             = length(["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"])
  cidr_block        = element(["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"], count.index)
  vpc_id            = aws_vpc.main.id
  availability_zone = element(["us-east-2a", "us-east-2b"], count.index)
  tags              = var.tags
}

resource "aws_db_subnet_group" "private" {
  name        = "${var.project}-database"
  description = "Groups private subnets for RDS instance"
  subnet_ids  = aws_subnet.private.*.id
  tags        = var.tags
}

################################################################################
# Route Tables
################################################################################

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = var.tags

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  count          = length(["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"])
  subnet_id      = element(aws_subnet.public[*].id, count.index)
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags   = var.tags
}

resource "aws_route_table_association" "private" {
  count          = length(["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"])
  subnet_id      = element(aws_subnet.private[*].id, count.index)
  route_table_id = aws_route_table.private.id
}