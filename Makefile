PYPI_REPO=https://upload.pypi.org/legacy/
define DOCKERFILE
FROM python:3.9-alpine
RUN python -m pip install twine==4.0.2
endef
export DOCKERFILE
MOPIDY_IMG=mopidy-webm3u
BUILD_IMG=mopidy-webm3u-build
DOCKER_OPTS=--rm -u `id -u`:`id -g` \
                -v "`pwd`:/work" -w /work \
                --entrypoint sh $(BUILD_IMG) -c

.PHONY: wheel
wheel: clean python-container
	docker run $(DOCKER_OPTS) 'python3 setup.py bdist_wheel'

.PHONY: test
test: mopidy-container
	# Run unit tests
	mkdir -p data
	@docker run --rm -u `id -u`:`id -g` -w /extension \
                -v "`pwd`:/extension" \
                -v "`pwd`/data:/var/lib/mopidy" \
		--entrypoint sh $(MOPIDY_IMG) -c \
		'set -x; python -m unittest discover ./tests'

.PHONY: test-e2e
test-e2e: mopidy-container
	# Run e2e tests
	mkdir -p data
	@docker run --rm -u `id -u`:`id -g` -w /extension \
                -v "`pwd`:/extension" \
		-v "`pwd`/data:/var/lib/mopidy" \
                --entrypoint sh $(MOPIDY_IMG) -c \
		'set -x; bats -T tests/e2e'

.PHONY: run
run: mopidy-container
	mkdir -p data
	docker run -ti --rm -u `id -u`:`id -g` --network=host \
		-v "`pwd`:/extension" \
		-e MOPIDY_NO_CHMOD=true \
		-v "`pwd`/data:/var/lib/mopidy" \
		-v /run:/host/run \
		-e PULSE_SERVER=unix:/host/run/user/`id -u`/pulse/native \
		--mount "type=bind,src=$$HOME/.config/pulse,dst=/var/lib/mopidy/.config/pulse" \
		-e HOME=/var/lib/mopidy \
		-e MOPIDY_SUBIDY_ENABLED=true \
		-e MOPIDY_SUBIDY_URL=http://localhost:8337/subsonic \
		-e MOPIDY_OPTS= \
		$(MOPIDY_IMG) $*

.PHONY: mopidy-container
mopidy-container: wheel
	docker build --rm -t $(MOPIDY_IMG) .

.PHONY: release
release: clean wheel
	docker run -e PYPI_USER -e PYPI_PASS -e PYPI_REPO=$(PYPI_REPO) \
		$(DOCKER_OPTS) \
		'python3 -m twine upload --repository-url "$$PYPI_REPO" -u "$$PYPI_USER" -p "$$PYPI_PASS" dist/*'

.PHONY: clean
clean:
	rm -rf build dist *.egg-info
	find . -name __pycache__ -exec rm -rf {} \; || true

.PHONY: clean-data
clean-data: clean
	docker run -ti --rm -v "`pwd`:/src" alpine:3.19 rm -rf /src/data

.PHONY: python-container
python-container:
	echo "$$DOCKERFILE" | docker build --rm -f - -t $(BUILD_IMG) .

