# ADL NESA MZ Decoder

Adds a **decoder** to the [ADL FTP Plugin](https://github.com/wmo-raf/adl-ftp-plugin)
for the record files that the **NESA** automatic weather stations of
Mozambique's INAM (Instituto Nacional de Meteorologia) deliver over FTP — one
line per record, framed by `S,` and `#`, with the timestamp split across six
fields followed by `sensor id, channel id, value` triplets. With this package
installed, an ADL FTP/SFTP connection can select **NESAMZ FTP Decoder -
Mozambique** as its decoder and collect those files like any other FTP source.
It provides a decoder only: no connection or station-link model of its own.

**Operator guide:** [docs/guide.md](docs/guide.md) — prerequisites,
installation, the file format, every connection and station-link field, the
variable mappings, collection behaviour, diagnostics and troubleshooting. The
guide is also published on the central ADL documentation site.

## Development setup

The plugin runs inside the ADL core image, alongside the ADL FTP Plugin. Build
the `adl:latest` image from the [ADL core repository](https://github.com/wmo-raf/adl)
first, then:

```bash
git clone https://github.com/inam-mz/adl-mz-nesa-decoder.git
cd adl-mz-nesa-decoder
cp .env.sample .env        # set PLUGIN_BUILD_UID=$(id -u), PLUGIN_BUILD_GID=$(id -g), ADL_DB_PASSWORD
docker compose build
docker compose up
docker compose exec adl adl createsuperuser
```

The admin is served on `PORT` (default 8080). The plugin source is
bind-mounted, so code changes reload the dev server. If the build fails with
`pull access denied` for `adl:latest`, prefix the build with
`DOCKER_BUILDKIT=0`.

Lint and format from `plugins/adl_mz_nesa_decoder/` with `make lint` and
`make format`. See [CONTRIBUTING.md](CONTRIBUTING.md) — a change to the file
format, the record keys or the units must update the guide in the same PR.
