provider aws{
    region= "ap-south-1"
    profile= "terraform_user"
}

resource "aws_vpc" "vpc" {
  
  cidr_block       = "10.0.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "web_vpc"
  }
}

resource "aws_subnet" "subnet1" {
  depends_on= [aws_vpc.vpc]
  vpc_id     = aws_vpc.vpc.id
  availability_zone = "ap-south-1a"
  cidr_block = "10.0.1.0/24"
  tags = {
    Name = "web_subnet1"
  }
}

resource "aws_internet_gateway" "igw" {
  depends_on= [aws_vpc.vpc]
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "web_igw"
  }
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.vpc.id
  depends_on= [aws_internet_gateway.igw]

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "web_route_table"
  }
}

resource "aws_route_table_association" "rt_subnet_asso" {
  subnet_id      = aws_subnet.subnet1.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_security_group" "web_sg" {
  name        = "web_allow_all"
  description = "Allow all traffic to k8s"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    description      = "Allow all Port"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web_allow_all"
  }
}

resource "aws_instance" "web" {
    ami= "ami-010aff33ed5991201" 
    availability_zone = "ap-south-1a"
    instance_type= "t2.micro"
    associate_public_ip_address = true
    key_name= "ansible"
    vpc_security_group_ids= ["${aws_security_group.web_sg.id}"] 
    subnet_id= aws_subnet.subnet1.id 
    tags={
        Name= "webos"
    }
    connection{
        type= "ssh"
        user= "ec2-user"
        private_key= file("ansible.pem")
        host= aws_instance.web.public_ip
    }
    provisioner "remote-exec" {
        inline= [
            "sudo yum install httpd -y",
            "sudo systemctl start httpd"
        ]
    }
} 


resource "aws_ebs_volume" "ebs1"{
    availability_zone= aws_instance.web.availability_zone
    size= 1
    tags={
        Name= "web_hd"
    }
}

resource "aws_volume_attachment" "ebs_attach"{
    device_name= "/dev/xvdc"
    volume_id= aws_ebs_volume.ebs1.id
    instance_id= aws_instance.web.id 
}

resource "null_resource" "web-attachEBS"{
depends_on = [
    aws_volume_attachment.ebs_attach,
  ]

    connection{
        type="ssh"
        user="ec2-user"
        private_key= file("ansible.pem")
        host= aws_instance.web.public_ip
    }
    provisioner "remote-exec" {
        inline=[
            "sudo mkfs.ext4 /dev/xvdc",
            "sudo mount /dev/xvdc /var/www/html"
        ]
    }
}
