FROM        python:3.14.1-alpine@sha256:eb37f58646a901dc7727cf448cae36daaefaba79de33b5058dab79aa4c04aefb

# renovate: datasource=repology depName=alpine_3_22/gcc versioning=loose
ARG         GCC_VERSION="14.2.0-r6"
# renovate: datasource=repology depName=alpine_3_22/build-base versioning=loose
ARG         BUILD_BASE_VERSION="0.5-r3"
# renovate: datasource=repology depName=alpine_3_22/libffi-dev versioning=loose
ARG         LIBFFI_VERSION="3.4.8-r0"
# renovate: datasource=repology depName=alpine_3_22/libretls-dev versioning=loose
ARG         LIBRETLS_VERSION="3.7.0-r2"
# renovate: datasource=repology depName=alpine_3_22/cargo versioning=loose
ARG         CARGO_VERSION="1.87.0-r0"

ARG         TARGETPLATFORM

WORKDIR     /app

ADD         requirements.txt .

RUN         --mount=type=cache,sharing=locked,target=/root/.cache,id=home-cache-$TARGETPLATFORM \
            --mount=type=cache,sharing=locked,target=/root/.cargo,id=home-cargo-$TARGETPLATFORM \
            apk add --no-cache \
              libgcc=${GCC_VERSION} \
            && \
            apk add --no-cache --virtual .build-deps \
              gcc=${GCC_VERSION} \
              build-base=${BUILD_BASE_VERSION} \
              libffi-dev=${LIBFFI_VERSION} \
              libretls-dev=${LIBRETLS_VERSION} \
              cargo=${CARGO_VERSION} \
            && \
            pip install -r requirements.txt && \
            apk del .build-deps && \
            chown -R nobody:nogroup /app

COPY        --chown=nobody:nogroup . .
COPY        --chown=nobody:nogroup config.example.yml config.yml

USER        nobody

ENTRYPOINT  [ "python", "deezer.py" ]
