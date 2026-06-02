#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]


def valid_name(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]([-a-z0-9]*[a-z0-9])?", name))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: ./scripts/create-service.py <service-name>", file=sys.stderr)
        return 1

    service = sys.argv[1].strip()
    if not valid_name(service):
        print("Service name must be lowercase DNS-1123 format, for example: orders-api", file=sys.stderr)
        return 1

    app = ROOT / "apps" / service
    base = ROOT / "k8s" / "services" / service / "base"
    overlays = ROOT / "k8s" / "services" / service / "overlays"

    write(app / "Dockerfile", f'''
        FROM python:3.12-alpine

        WORKDIR /app
        COPY src/server.py /app/server.py

        ENV SERVICE_NAME={service}
        ENV PORT=8080

        EXPOSE 8080

        CMD ["python", "/app/server.py"]
    ''')

    write(app / "src" / "server.py", f'''
        import json
        import os
        from http.server import BaseHTTPRequestHandler, HTTPServer

        SERVICE_NAME = os.getenv("SERVICE_NAME", "{service}")
        PORT = int(os.getenv("PORT", "8080"))


        class Handler(BaseHTTPRequestHandler):
            def _send_json(self, status_code, payload):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.path == "/health":
                    self._send_json(200, {{"status": "ok", "service": SERVICE_NAME}})
                    return

                self._send_json(200, {{"service": SERVICE_NAME, "message": "running"}})


        if __name__ == "__main__":
            server = HTTPServer(("0.0.0.0", PORT), Handler)
            print(f"{{SERVICE_NAME}} listening on port {{PORT}}", flush=True)
            server.serve_forever()
    ''')

    write(base / "kustomization.yaml", f'''
        apiVersion: kustomize.config.k8s.io/v1beta1
        kind: Kustomization

        resources:
          - serviceaccount.yaml
          - deployment.yaml
          - service.yaml
          - hpa.yaml
          - pdb.yaml
          - destinationrule.yaml
          - sidecar.yaml

        commonLabels:
          app.kubernetes.io/name: {service}
          app.kubernetes.io/part-of: cloud-agnostic-platform
    ''')

    write(base / "serviceaccount.yaml", f'''
        apiVersion: v1
        kind: ServiceAccount
        metadata:
          name: {service}
          namespace: apps
    ''')

    write(base / "deployment.yaml", f'''
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: {service}
          namespace: apps
        spec:
          replicas: 2
          selector:
            matchLabels:
              app.kubernetes.io/name: {service}
          template:
            metadata:
              labels:
                app.kubernetes.io/name: {service}
                app.kubernetes.io/part-of: cloud-agnostic-platform
            spec:
              serviceAccountName: {service}
              containers:
                - name: {service}
                  image: {service}-image
                  imagePullPolicy: IfNotPresent
                  ports:
                    - name: http
                      containerPort: 8080
                  envFrom:
                    - configMapRef:
                        name: {service}-config
                        optional: true
                  readinessProbe:
                    httpGet:
                      path: /health
                      port: http
                    initialDelaySeconds: 10
                    periodSeconds: 10
                  livenessProbe:
                    httpGet:
                      path: /health
                      port: http
                    initialDelaySeconds: 30
                    periodSeconds: 20
                  resources:
                    requests:
                      cpu: 100m
                      memory: 128Mi
                    limits:
                      cpu: 500m
                      memory: 512Mi
    ''')

    write(base / "service.yaml", f'''
        apiVersion: v1
        kind: Service
        metadata:
          name: {service}
          namespace: apps
        spec:
          type: ClusterIP
          selector:
            app.kubernetes.io/name: {service}
          ports:
            - name: http
              port: 80
              targetPort: http
    ''')

    write(base / "hpa.yaml", f'''
        apiVersion: autoscaling/v2
        kind: HorizontalPodAutoscaler
        metadata:
          name: {service}
          namespace: apps
        spec:
          scaleTargetRef:
            apiVersion: apps/v1
            kind: Deployment
            name: {service}
          minReplicas: 2
          maxReplicas: 10
          metrics:
            - type: Resource
              resource:
                name: cpu
                target:
                  type: Utilization
                  averageUtilization: 70
    ''')

    write(base / "pdb.yaml", f'''
        apiVersion: policy/v1
        kind: PodDisruptionBudget
        metadata:
          name: {service}
          namespace: apps
        spec:
          minAvailable: 1
          selector:
            matchLabels:
              app.kubernetes.io/name: {service}
    ''')

    write(base / "destinationrule.yaml", f'''
        apiVersion: networking.istio.io/v1
        kind: DestinationRule
        metadata:
          name: {service}
          namespace: apps
        spec:
          host: {service}.apps.svc.cluster.local
          trafficPolicy:
            tls:
              mode: ISTIO_MUTUAL
            outlierDetection:
              consecutive5xxErrors: 5
              interval: 30s
              baseEjectionTime: 30s
              maxEjectionPercent: 50
    ''')

    write(base / "sidecar.yaml", f'''
        apiVersion: networking.istio.io/v1
        kind: Sidecar
        metadata:
          name: {service}
          namespace: apps
        spec:
          workloadSelector:
            labels:
              app.kubernetes.io/name: {service}
          egress:
            - hosts:
                - "./*"
                - "istio-system/*"
    ''')

    for cloud in ("gcp", "aws", "azure"):
        cloud_dir = overlays / cloud
        if cloud == "gcp":
            write(cloud_dir / "kustomization.yaml", f'''
                apiVersion: kustomize.config.k8s.io/v1beta1
                kind: Kustomization

                resources:
                  - ../../base

                generatorOptions:
                  disableNameSuffixHash: true

                images:
                  - name: {service}-image
                    newName: europe-west1-docker.pkg.dev/PROJECT_ID/apps/{service}
                    newTag: v1.0.0

                configMapGenerator:
                  - name: {service}-config
                    namespace: apps
                    literals:
                      - CLOUD_PROVIDER=gcp
                      - SERVICE_NAME={service}

                patches:
                  - path: serviceaccount-patch.yaml
            ''')
            write(cloud_dir / "serviceaccount-patch.yaml", f'''
                apiVersion: v1
                kind: ServiceAccount
                metadata:
                  name: {service}
                  namespace: apps
                  annotations:
                    iam.gke.io/gcp-service-account: {service}@PROJECT_ID.iam.gserviceaccount.com
            ''')
        elif cloud == "aws":
            write(cloud_dir / "kustomization.yaml", f'''
                apiVersion: kustomize.config.k8s.io/v1beta1
                kind: Kustomization

                resources:
                  - ../../base

                generatorOptions:
                  disableNameSuffixHash: true

                images:
                  - name: {service}-image
                    newName: ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/{service}
                    newTag: v1.0.0

                configMapGenerator:
                  - name: {service}-config
                    namespace: apps
                    literals:
                      - CLOUD_PROVIDER=aws
                      - SERVICE_NAME={service}

                patches:
                  - path: serviceaccount-patch.yaml
            ''')
            write(cloud_dir / "serviceaccount-patch.yaml", f'''
                apiVersion: v1
                kind: ServiceAccount
                metadata:
                  name: {service}
                  namespace: apps
                  annotations:
                    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/{service}-role
            ''')
        else:
            write(cloud_dir / "kustomization.yaml", f'''
                apiVersion: kustomize.config.k8s.io/v1beta1
                kind: Kustomization

                resources:
                  - ../../base

                generatorOptions:
                  disableNameSuffixHash: true

                images:
                  - name: {service}-image
                    newName: ACR_NAME.azurecr.io/{service}
                    newTag: v1.0.0

                configMapGenerator:
                  - name: {service}-config
                    namespace: apps
                    literals:
                      - CLOUD_PROVIDER=azure
                      - SERVICE_NAME={service}

                patches:
                  - path: serviceaccount-patch.yaml
                  - path: deployment-patch.yaml
            ''')
            write(cloud_dir / "serviceaccount-patch.yaml", f'''
                apiVersion: v1
                kind: ServiceAccount
                metadata:
                  name: {service}
                  namespace: apps
                  annotations:
                    azure.workload.identity/client-id: AZURE_MANAGED_IDENTITY_CLIENT_ID
            ''')
            write(cloud_dir / "deployment-patch.yaml", f'''
                apiVersion: apps/v1
                kind: Deployment
                metadata:
                  name: {service}
                  namespace: apps
                spec:
                  template:
                    metadata:
                      labels:
                        azure.workload.identity/use: "true"
            ''')

    services_file = ROOT / "services.txt"
    existing = set()
    if services_file.exists():
        existing = {line.strip() for line in services_file.read_text().splitlines() if line.strip()}
    if service not in existing:
        with services_file.open("a", encoding="utf-8") as f:
            f.write(f"{service}\n")

    print(f"Created service scaffold: {service}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
