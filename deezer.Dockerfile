FROM        python:3.14.4-alpine@sha256:dd4d2bd5b53d9b25a51da13addf2be586beebd5387e289e798e4083d94ca837a

# renovate: datasource=repology depName=alpine_3_23/gcc versioning=loose
ARG         GCC_VERSION="15.2.0-r2"
# renovate: datasource=repology depName=alpine_3_23/build-base versioning=loose
ARG         BUILD_BASE_VERSION="0.5-r3"
# renovate: datasource=repology depName=alpine_3_23/libffi-dev versioning=loose
ARG         LIBFFI_VERSION="3.5.2-r0"
# renovate: datasource=repology depName=alpine_3_23/libretls-dev versioning=loose
ARG         LIBRETLS_VERSION="3.8.1-r0"
# renovate: datasource=repology depName=alpine_3_23/cargo versioning=loose
ARG         CARGO_VERSION="1.91.1-r1"
# renovate: datasource=repology depName=alpine_3_23/cmake versioning=loose
ARG         CMAKE_VERSION="4.1.3-r0"

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
              cmake=${CMAKE_VERSION} \
            && \
            pip install -r requirements.txt && \
            apk del .build-deps && \
            chown -R nobody:nogroup /app

COPY        --chown=nobody:nogroup . .
COPY        --chown=nobody:nogroup config.example.yml config.yml

USER        nobody

ENTRYPOINT  [ "python", "deezer.py" ]
