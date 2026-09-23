# 人类飞行器发射行动档案

中文检索界面，保存旧站的 GCAT 1.8.8 历史快照：75,968 条行动记录，覆盖 1942–2026 共 85 个年份。详情按 24 个年份分片保存，另有 8 个全库检索分片。

## 使用

选择年份浏览，或点击“全库检索”载入全部索引。支持多关键词、行动类型、结果筛选、40 条分页、飞行与运载器参数、来源引文和原始记录。

数据使用 gzip 压缩并按年份区间分片，浏览器按需解压。需要支持 DecompressionStream 的现代浏览器。全库索引首次下载约 4 MB。专有名称与原始引文保留原文；常见运载器名称支持中文查询。

## 来源和范围

来源：Jonathan C. McDowell, General Catalog of Artificial Space Objects (GCAT), 1.8.8；https://planet4589.org/space/gcat/ 。来源更新时间按 manifest.json 记录为 2026 Sep 13 2310:51 UTC。部分任务包含 The Space Devs Launch Library 2 扩展资料。

数据库截止时间为 2026-09-14 07:10:51（UTC+8），不表示数据已更新至当前日期，也不表示已逐条重新核验。档案包含轨道、亚轨道、导弹及探空等行动，不等于所有记录都是卫星发射。详情保留 GCAT 原始 UTC 时间和精度；列表时间统一按固定 UTC+08:00 推导。源快照中质量为零的值在界面显示为“未记录／不适用”，原始记录保持不变。

## 2026-09-23 数据修正

- 修正 2,002 条曾受上海历史时区或夏令时影响、误显示为 UTC+9 的派生时间，并同步全库检索索引；GCAT 原始 UTC 和其他事实字段未改动。
- 用实际的完整档案字段替换过时的演示版 JSON Schema，并移除未被主站使用的 20 条演示数据。
- 为全部 32 个 gzip 分片写入字节数和 SHA-256，部署前自动核验记录唯一性、年份数量、截止时间、坐标、UTC+8 时间及检索索引一致性。

## 文件

- archive/manifest.json：覆盖范围、各年份数量、分片清单和 SHA-256。
- archive/years-*.json.gz：24 个年份详情分片；保留源事实字段，并修正派生的 UTC+8 显示时间。
- archive/search-N.json.gz：全库检索索引。
- data/schema.json：详情记录的 JSON Schema。
- index.html、app.js、styles.css：无需构建的静态网站。
- scripts/repair_archive_content.py：可重复运行的时间与索引修正脚本。
- scripts/validate_archive.py：全库一致性与完整性校验。
- .github/workflows/pages.yml：代码校验与 GitHub Pages 部署。

## 部署

仓库 Settings → Pages → Source 选择 GitHub Actions。推送 main 后自动部署。

本地预览：运行 `python -m http.server 8765`，访问 http://localhost:8765 。不要直接以 file:// 打开页面。
