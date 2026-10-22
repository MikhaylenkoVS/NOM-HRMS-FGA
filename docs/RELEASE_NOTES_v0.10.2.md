# NOM-HRMS FGA v0.10.2

Исправление загрузки опциональной базы CHNOSPHal.

## Причина

`release_manifest.json` ссылался на `releases/latest/download/...`.
После выхода v0.10.1 «latest» стала указывать на релиз без файлов
CHNOSPHal, поэтому загрузка из окна «База формул» получала 404.

## Исправление

Ссылки на файлы баз теперь привязаны к релизу, где они действительно
опубликованы (v0.10.0):

- `chorsphal_1000_v3.fdb`
- `chorsphal_1000_v3.idx`
- `chorsphal_1000_v3.manifest.json`
- `chposp_1000_zstd9_v2.fdb`
- `chposp_1000_zstd9_v2.manifest.json`

Это работает для уже установленных 0.10.0/0.10.1: они получают
обновлённый `release_manifest.json` из latest-релиза.
