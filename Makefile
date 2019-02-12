S3_BUCKET=carbon-deploy
ORACLE_ZIP=instantclient-basiclite-linux.x64-18.3.0.0.0dbru.zip
LIBAIO=libaio.so.1.0.1

help: ## Print this message
	@awk 'BEGIN { FS = ":.*##"; print "Usage:  make <target>\n\nTargets:" } \
				/^[-_[:alpha:]]+:.?*##/ { printf "  %-15s%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

lib/libaio.so.1:
	aws s3 cp s3://$(S3_BUCKET)/$(LIBAIO) lib/libaio.so.1

lib/libclntsh.so:
	aws s3 cp s3://$(S3_BUCKET)/$(ORACLE_ZIP) lib/$(ORACLE_ZIP) && \
  	unzip -j lib/$(ORACLE_ZIP) -d lib/ 'instantclient_18_3/*' && \
  	rm -f lib/$(ORACLE_ZIP)

stage: lib/libclntsh.so lib/libaio.so.1 ## Deploy staging build
	pipenv run zappa update stage

prod: lib/libclntsh.so lib/libaio.so.1 ## Deploy production build
	pipenv run zappa update prod

clean: ## Remove build artifacts
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	find . -name '__pycache__' -print0 | xargs -0 rm -rf
	rm -rf .coverage .tox *.egg-info .eggs build/

distclean: clean ## Remove build artifacts and vendor libs
	rm -rf lib/
