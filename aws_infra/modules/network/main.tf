resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Project = var.project
    Name = "VPC"
    Description = "Main VPC of the service"
  }
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = [ "vpc-flow-logs.amazonaws.com" ]
    }
    actions = [ "sts:AssumeRole" ]
  }
}

resource "aws_cloudwatch_log_group" "main" {
  name = "${var.project}-flow-logs"
  retention_in_days = 1

  tags = {
    Project = var.project
    Name = "Cloudwatch Flow Logs"
    Description = "Logs of traffic in the VPC"
  }
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
    resources = [ "${aws_cloudwatch_log_group.main.arn}:*" ]
  }
}

resource "aws_iam_role" "main" {
  name = "${var.project}-flow-log"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  inline_policy {
    name = "${var.project}-flow-log-cloudwatch-access"
    policy = data.aws_iam_policy_document.traffic_log.json
  }

  tags = {
    Project = var.project
    Name = "Flow Log IAM Role"
    Description = "IAM role to allow flow log to alter Cloudwatch log group"
  }
}

resource "aws_flow_log" "main" {
  traffic_type = "ALL"
  iam_role_arn = aws_iam_role.main.arn
  log_destination = aws_cloudwatch_log_group.main.arn
  max_aggregation_interval = 60
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "public" {
  count             = length(["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"])
  cidr_block        = element(["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"], count.index)
  vpc_id            = aws_vpc.main.id
  availability_zone = element(["us-east-2a", "us-east-2b", "us-east-2c"], count.index)


  tags = {
    Project = var.project
    Name = "Public Subnet ${count.index + 1}"
    Description = "Public subnet of the VPC"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Project = var.project
    Name = "Internet Gateway"
    Description = "Public subnet internet access"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Project = var.project
    Name = "Public Route Table"
    Description = "Route table of public subnet to Internet Gateway"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"])
  subnet_id      = element(aws_subnet.public[*].id, count.index)
  route_table_id = aws_route_table.public.id
}

resource "aws_subnet" "private" {
  count             = length(["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"])
  cidr_block        = element(["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"], count.index)
  vpc_id            = aws_vpc.main.id
  availability_zone = element(["us-east-2a", "us-east-2b"], count.index)

  tags = {
    Project = var.project
    Name = "Private Subnet ${count.index + 1}"
    Description = "Private subnet of the VPC"
  }
}

resource "aws_db_subnet_group" "private" {
  name = "${var.project}-database"
  description = "Groups private subnets for RDS instance"
  subnet_ids = aws_subnet.private.*.id

  tags = {
    Project = var.project
    Name = "Private DB Subnet Group"
    Description = "Groups private subnets for RDS instance"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Project = var.project
    Name = "Private Route Table"
    Description = "Route table of private subnet"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"])
  subnet_id      = element(aws_subnet.private[*].id, count.index)
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "main" {
  name        = "${var.project}-default"
  description = "Allows resources to access the internet"
  vpc_id      = aws_vpc.main.id

  tags = {
    Project = var.project
    Name = "Main security group"
    Description = "Allows resources to access the internet"
  }
}

resource "aws_vpc_security_group_egress_rule" "main" {
  security_group_id = aws_security_group.main.id
  ip_protocol       = -1
  cidr_ipv4         = "0.0.0.0/0"
}