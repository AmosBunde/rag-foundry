output "rendered_compose_path" {
  description = "Path to the rendered docker-compose.yml"
  value       = local_file.docker_compose.filename
}

output "rendered_nginx_path" {
  description = "Path to the rendered nginx.conf"
  value       = local_file.nginx_conf.filename
}

output "rendered_env_path" {
  description = "Path to the rendered .env file"
  value       = local_file.env_file.filename
}

output "deploy_script_path" {
  description = "Path to the generated deploy.sh script"
  value       = local_file.deploy_script.filename
}

output "deployment_url" {
  description = "Public URL of the deployed API"
  value       = var.enable_https ? "https://${var.domain}" : "http://${var.domain}"
}

output "ssh_target" {
  description = "SSH target string for the bare-metal host"
  value       = "${var.host_user}@${var.host_ip}"
}
