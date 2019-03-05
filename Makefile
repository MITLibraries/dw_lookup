S3_BUCKET=deploy-mitlib-stage
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

deps: lib/libaio.so.1 lib/libclntsh.so

dist: deps ## Create stage deploy package locally
	pipenv run zappa package stage

stage: deps ## Deploy staging build
	pipenv run zappa update stage
	pipenv run zappa certify --yes stage

prod: deps ## Deploy production build
	pipenv run zappa update prod
	pipenv run zappa certify --yes prod

clean: ## Remove build artifacts
	find . -name "*.pyc" -print0 | xargs -0 rm -f
	find . -name '__pycache__' -print0 | xargs -0 rm -rf
	rm -rf .coverage .tox *.egg-info .eggs build/
	rm -f author-lookup-stage-*.zip

distclean: clean ## Remove build artifacts and vendor libs
	rm -rf lib/
