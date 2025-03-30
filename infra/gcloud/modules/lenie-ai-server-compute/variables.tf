variable "instance_type" {
  type = string                     # The type of the variable, in this case a string
  default = "e2-micro"                 # Default value for the variable
  description = "The type of EC2 instance" # Description of what this variable represents
}

variable "zone" {
  type = string
  description = "GCP zone"
}
