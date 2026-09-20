# GitHub 主页图片自动更新

`update-stars.py` 使用 GitHub REST API 读取账号名下的全部公开仓库，汇总收到的 Star，并生成浅色、深色两张 SVG。包括账号名下的 fork 仓库；不统计私有仓库，也不是账号收藏他人项目的数量。右侧展示 Star 最多的两个项目，条形长度按 Star 数量成比例绘制。

本地刷新（Python 3.9+，无第三方依赖）：

```sh
python3 scripts/update-stars.py --username DLYZZT
```

可以通过环境变量 `GITHUB_TOKEN` 提高 API 请求额度；不要把令牌写入文件。

`.github/workflows/update-stars.yml` 每天 UTC 00:23（北京时间 08:23）同时刷新 Star 统计卡和贪吃蛇动画，也支持在 Actions 页面手动运行。工作流使用仓库自带的 `GITHUB_TOKEN`，仅提交这四张生成的 SVG。首次把该工作流推送到 `main` 也会触发生成。

贪吃蛇使用固定版本的 [Platane/snk SVG Action](https://github.com/Platane/snk)，读取仓库所有者的最新贡献图，生成 `assets/github-snake.svg` 和 `assets/github-snake-dark.svg`，保留当前蓝紫配色。任一步生成失败时，工作流不会提交本轮图片。

当前本地生成结果是预览快照。自动更新必须在工作流提交到 GitHub 默认分支后才会启用；本地预览不会自己定时刷新。GitHub 的定时执行可能有延迟，公开仓库长期没有活动时也可能暂停定时工作流，详见 [GitHub 定时工作流文档](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。
