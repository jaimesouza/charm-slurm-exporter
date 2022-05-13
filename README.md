# charm-slurm-exporter

Install https://github.com/vpenso/prometheus-slurm-exporter

juju deploy ./slurm-exporter_ubuntu-20.04-amd64_centos-7-amd64.charm --resource slurm-exporter=./slurm-exporter.tar.gz

juju deploy

$ juju relate prometheus2:scrape slurm-exporter:prometheus

