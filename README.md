# 人类飞行器发射行动档案

中文检索界面，保存旧站的 GCAT 1.8.8 历史快照：75,968 条行动记录，1942–2026 年，85 个年份文件。

## 使用

选择年份浏览，或点击“全库检索”载入全部索引。支持多关键词、行动类型、结果筛选、40 条分页、飞行与运载器参数、来源引文和原始记录。

数据使用 gzip 压缩并按五年一组分片，浏览器按需解压。需要支持 DecompressionStream 的现代浏览器。全库索引首次下载约 4 MB。专有名称与原始引文保留原文；常见运载器名称支持中文查询。

## 来源和范围

来源：Jonathan C. McDowell, General Catalog of Artificial Space Objects (GCAT), 1.8.8；https://planet4589.org/space/gcat/ 。来源更新时间按 manifest.json 记录为 2026 Sep 13 2310:51 UTC。部分任务包含 The Space Devs Launch Library 2 扩展资料。

这是原快照无损迁移，不表示数据已更新至当前日期，也不表示已逐条重新核验。档案包含轨道、亚轨道、导弹及探空等行动，不等于所有记录都是卫星发射。缺失数值不等于零。详情保留原始 UTC 时间和精度，列表采用原快照中的 UTC+8 显示值。

## 文件

- archive/manifest.json：覆盖范围、各年份数量和索引清单。
- archive/years-*.json.gz：五年一组的年份详情；记录内容与旧站原年份 JSON 完全一致。
- archive/search-N.json.gz：全库检索索引。
- index.html、app.js、styles.css：无需构建的静态网站。
- data/launches.json：早期 20 条演示数据，不是完整库，也不再供主页面使用。
- .github/workflows/pages.yml：代码校验与 GitHub Pages 部署。

## 部署

仓库 Settings → Pages → Source 选择 GitHub Actions。推送 main 后自动部署。

本地预览：运行 `python -m http.server 8765`，访问 http://localhost:8765 。不要直接以 file:// 打开页面。
