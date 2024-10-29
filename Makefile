python=python3
SUPPORTED_PLATFORMS_URL="https://raw.githubusercontent.com/smswithoutborders/SMSWithoutBorders-Publisher/main/resources/platforms.json"

define log_message
	@echo "[$(shell date +'%Y-%m-%d %H:%M:%S')] - $1"
endef

start-rest-api:
	@(\
		echo "[$(shell date +'%Y-%m-%d %H:%M:%S')] - INFO - Starting REST API with TLS ..." && \
		gunicorn -w 4 -b 0.0.0.0:'${SSL_PORT}' \
			--log-level=info \
			--access-logfile=- \
			--certfile='${SSL_CERTIFICATE}' \
			--keyfile='${SSL_KEY}' \
			--preload \
			--timeout 30 \
			server:app; \
	)

migrate:
	$(call log_message,INFO - Starting migration ...)
	@$(python) migrationHelper.py
	@echo ""
	$(call log_message,INFO - Migration completed successfully.)

grpc-compile:
	$(call log_message,INFO - Compiling gRPC protos ...)
	@$(python) -m grpc_tools.protoc \
		-I./protos/v1 \
		--python_out=. \
		--pyi_out=. \
		--grpc_python_out=. \
		./protos/v1/*.proto
	$(call log_message,INFO - gRPC Compilation complete!)

grpc-server-start:
	$(call log_message,INFO - Starting gRPC server ...)
	@$(python) -u grpc_server.py
	$(call log_message,INFO - gRPC server started successfully.)

grpc-internal-server-start:
	$(call log_message,INFO - Starting gRPC internal server ...)
	@$(python) -u grpc_internal_server.py
	$(call log_message,INFO - gRPC internal server started successfully.)

download-platforms:
	$(call log_message,INFO - Starting download of platforms JSON file ...)
	@curl -o platforms.json -L "${SUPPORTED_PLATFORMS_URL}"
	$(call log_message,INFO - Platforms JSON file downloaded successfully.)

create-dummy-user:
	$(call log_message,INFO - Creating dummy user ...)
	@$(python) -m scripts.cli create -n +237123456789
	@echo ""
	$(call log_message,INFO - Dummy user created successfully.)

grpc-server-setup: create-dummy-user download-platforms grpc-compile grpc-server-start
	$(call log_message,INFO - gRPC server setup completed.)
