IMAGE ?= ssh-audit-eda:latest

.PHONY: lint build run check

lint:
	# Локальные линтеры могут отсутствовать — этап продублирован в CI
	@echo "Skipping local lint (handled in CI)"

build:
	docker build -t $(IMAGE) -f docker/Dockerfile .

run:
	mkdir -p logs && \
	docker run --rm \
	  -v $(PWD)/example:/example:ro \
	  -v $(PWD)/logs:/var/log \
	  $(IMAGE)

check:
	@jq -e . ./logs/ansible-ssh-audit.log > /dev/null || \
	  (echo "Invalid JSON log" && exit 1)

