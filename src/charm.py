#!/usr/bin/env python3
# Copyright 2022 Omnivector Solutions LLC
# See LICENSE file for licensing details.

"""Slurm Exporter Charm."""

import logging
from pathlib import Path

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, ModelError

from prometheus_exporter import Prometheus
from slurm_exporter_ops import SlurmExporterOps

logger = logging.getLogger(__name__)


class SlurmExporterCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        """Initialize charm."""
        super().__init__(*args)

        self._prometheus = Prometheus(self, "prometheus")
        self._slurm_exporter_ops = SlurmExporterOps()

        # juju core hooks
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.stop, self._on_stop)

    def _on_install(self, event):
        logger.debug("## Installing charm")
        self.unit.status = MaintenanceStatus("Installing slurm-exporter")

        logger.debug("## Retrieving slurm-exporter resource to install it")
        try:
            slurm_exporter_path = self.model.resources.fetch("slurm-exporter")
            logger.debug(f"## Found slurm-exporter resource: {slurm_exporter_path}")
        except ModelError:
            logger.error("## Missing slurm-exporter resource")
            self.unit.status = BlockedStatus("Missing slurm-exporter resource")
            event.defer()
            return

        self._slurm_exporter_ops.install(slurm_exporter_path)

        self._set_charm_version()
        self.unit.status = ActiveStatus("slurm-exporter installed")

    def _on_upgrade_charm(self, event):
        """Perform upgrade operations."""
        logger.debug("## Upgrading charm")
        self.unit.status = MaintenanceStatus("Upgrading node-exporter")

        logger.debug("## Retrieving slurm-exporter resource to install it")
        try:
            slurm_exporter_path = self.model.resources.fetch("slurm-exporter")
            logger.debug(f"## Found slurm-exporter resource: {slurm_exporter_path}")
        except ModelError:
            logger.error("## Missing slurm-exporter resource")
            self.unit.status = BlockedStatus("Missing slurm-exporter resource")
            event.defer()
            return
        self._slurm_exporter_ops.install(slurm_exporter_path)

        self._set_charm_version()
        self.unit.status = ActiveStatus("node-exporter upgraded")

    def _on_config_changed(self, event):
        """Handle configuration updates."""
        logger.debug("## Configuring charm")

        params = dict()
        params["listen_address"] = self.model.config.get("listen-address")
        params["gpu_accounting"] = self.model.config.get("gpu-accounting")

        logger.debug(f"## Configuration options: {params}")
        self._slurm_exporter_ops.configure(params)

        self._prometheus.set_relation_data()

    def _on_start(self, event):
        logger.debug("## Starting daemon")
        self._slurm_exporter_ops.start()
        self.unit.status = ActiveStatus("slurm-exporter started")

    def _on_stop(self, event):
        logger.debug("## Stopping daemon and uninstalling")
        self._slurm_exporter_ops.uninstall()

    def _set_charm_version(self):
        """Set the application version for Juju Status."""
        self.unit.set_workload_version(Path("version").read_text().strip())

    @property
    def port(self) -> str:
        """Return the port used for the HTTP connection."""
        return self.model.config.get("listen-address").split(":")[1]


if __name__ == "__main__":
    main(SlurmExporterCharm)
