"""
GCP Telemetry & Resource Management Interface
Module: gcp_telemetry.py
Provides live/mock telemetry for Google Cloud Run, Cloud SQL pgvector,
and Google Cloud Monitoring metrics.
"""

from typing import Dict, Any, Optional


class GCPResourceManager:
    """Manages GCP infrastructure telemetry and configuration updates."""

    def __init__(self):
        # Initial simulated enterprise cluster state on GCP
        self._cloud_run_services = {
            "payment-gateway": {
                "service_name": "payment-gateway",
                "region": "asia-east1",
                "status": "DEGRADED",
                "min_instances": 0,
                "max_instances": 10,
                "active_instances": 2,
                "p99_latency_ms": 1420.5,
                "error_rate_504": "3.8%",
                "container_concurrency": 80,
                "cpu_boost_enabled": False
            },
            "order-processor": {
                "service_name": "order-processor",
                "region": "asia-east1",
                "status": "HEALTHY",
                "min_instances": 2,
                "max_instances": 20,
                "active_instances": 5,
                "p99_latency_ms": 115.0,
                "error_rate_504": "0.0%",
                "container_concurrency": 20,
                "cpu_boost_enabled": True
            }
        }

        self._cloud_sql_instances = {
            "enterprise-db-primary": {
                "instance_id": "enterprise-db-primary",
                "database_version": "POSTGRES_16",
                "region": "asia-east1",
                "cpu_utilization": "92.4%",
                "pgvector_extension": "ENABLED",
                "active_indexes": ["idx_chunks_gin"],
                "missing_indexes": ["idx_knowledge_chunks_hnsw"],
                "active_connections": 182,
                "max_connections": 200
            }
        }

    def get_cloud_run_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        return self._cloud_run_services.get(service_name)

    def list_cloud_run_services(self) -> Dict[str, Any]:
        return {"services": list(self._cloud_run_services.keys())}

    def get_cloud_sql_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        return self._cloud_sql_instances.get(instance_id)

    def update_cloud_run_scaling(
        self, 
        service_name: str, 
        min_instances: int, 
        max_instances: int,
        container_concurrency: Optional[int] = None,
        cpu_boost_enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Applies scaling update to Cloud Run service."""
        if service_name not in self._cloud_run_services:
            raise ValueError(f"Cloud Run service '{service_name}' not found.")

        svc = self._cloud_run_services[service_name]
        svc["min_instances"] = min_instances
        svc["max_instances"] = max_instances
        if container_concurrency is not None:
            svc["container_concurrency"] = container_concurrency
        if cpu_boost_enabled is not None:
            svc["cpu_boost_enabled"] = cpu_boost_enabled

        # After scaling up min_instances and enabling cpu boost, latency recovers
        if min_instances >= 2:
            svc["status"] = "HEALTHY"
            svc["p99_latency_ms"] = 185.0
            svc["error_rate_504"] = "0.01%"

        return {
            "status": "SUCCESS",
            "message": f"Successfully updated Cloud Run service '{service_name}' config.",
            "updated_state": svc
        }
