CLOUD ?= gcp
SERVICE ?= checkout
TAG ?= v1.0.0

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make tf-init-gcp"
	@echo "  make tf-apply-gcp"
	@echo "  make tf-init-aws"
	@echo "  make tf-apply-aws"
	@echo "  make tf-init-azure"
	@echo "  make tf-apply-azure"
	@echo "  make build CLOUD=gcp SERVICE=checkout TAG=v1.0.0"
	@echo "  make deploy-platform"
	@echo "  make deploy-service CLOUD=gcp SERVICE=checkout"
	@echo "  make deploy-all CLOUD=gcp"

.PHONY: tf-init-gcp tf-apply-gcp
tf-init-gcp:
	terraform -chdir=infra/envs/gcp/dev init

tf-apply-gcp:
	terraform -chdir=infra/envs/gcp/dev apply

.PHONY: tf-init-aws tf-apply-aws
tf-init-aws:
	terraform -chdir=infra/envs/aws/dev init

tf-apply-aws:
	terraform -chdir=infra/envs/aws/dev apply

.PHONY: tf-init-azure tf-apply-azure
tf-init-azure:
	terraform -chdir=infra/envs/azure/dev init

tf-apply-azure:
	terraform -chdir=infra/envs/azure/dev apply

.PHONY: build
build:
	TAG=$(TAG) ./scripts/build-push.sh $(CLOUD) $(SERVICE)

.PHONY: deploy-platform
deploy-platform:
	kubectl apply -k k8s/platform

.PHONY: deploy-service
deploy-service:
	./scripts/deploy-service.sh $(CLOUD) $(SERVICE)

.PHONY: deploy-all
deploy-all:
	./scripts/deploy-all.sh $(CLOUD)
