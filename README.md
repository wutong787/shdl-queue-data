# 云端实时排队采集（关机也能记录）

把 Queue-Times 上海迪士尼(park_id=30) 的实时排队数据，用 **GitHub Actions 定时任务**自动抓取，
落进本仓库的 `data/queue_times.jsonl`。你电脑关机、出差都不影响积累。

> 数据归属硬要求（免费使用必须满足）：凡展示这些排队数据的产品/页面，须标注
> **“Powered by Queue-Times.com”** 并链接 https://queue-times.com

## 一、注册 GitHub（免费，约 2 分钟，无需信用卡）
1. 打开 https://github.com/signup
2. 填邮箱 → 设密码 → 起用户名 → 验证邮箱（收一封邮件点链接）
3. 完成。不用绑任何支付方式。

## 二、建一个私有仓库专门存数据
1. 右上角 “+” → New repository
2. Repository name 随便起，例如 `shdl-queue-data`
3. 选 **Private**（私有，数据只有你能看）
4. 勾 “Add a README file” → Create repository

## 三、把本文件夹内容传上去
把 `cloud_recorder/` 里的全部内容复制到新仓库根目录：
- `record.py`
- `queue_times_map.json`
- `.github/workflows/record.yml`
- （`data/` 目录不用提前建，脚本会自动建）

最简单的方式：在仓库页面 “Add file” → Upload files，把这几个文件拖进去提交。
（`.github` 是隐藏文件夹，上传时一并选上即可。）

## 四、开启定时任务
1. 进仓库 → **Settings → Actions → General**
2. Workflow permissions 选 **Read and write permissions**（否则推不回数据）
3. 进 **Actions** 标签页 → 左侧 `record-shanghai-disney-queue` → 第一次可能显示 “disabled”，点 **Enable workflow**
4. 想立刻验证：进 Actions → 该 workflow → **Run workflow** 手动跑一次，看是否生成 `data/queue_times.jsonl`

之后每 5 分钟自动抓一次（营业时段），数据持续追加。

## 五、把数据取回本地给 planner 用
两种方式：
- **git 拉取**：在本地 `git clone` / `git pull` 这个数据仓库，拿到 `data/queue_times.jsonl`
- **让我取**：需要时把仓库里 `data/queue_times.jsonl` 的 raw 链接发我，我用 WebFetch 读取后直接并入
  `detail_10min_overrides.json`（优先补那 4 个缺失项目）或做交叉校验。

## 六、数据格式（每行一条 JSON）
```json
{"snapshot_utc":"2026-08-13T02:35:00Z","project":"创极速光轮","ride_id":2985,"land":"明日世界","wait_time":120,"is_open":1,"last_updated_utc":"2026-08-13T02:27:02.000Z"}
```
字段含义：`snapshot_utc`=本次抓取时间(UTC)、`project`=映射到的本项目名、
`wait_time`=排队分钟(is_open=0 时为 null)、`is_open`=是否开放、`last_updated_utc`=数据源时间戳(UTC)。

## 七、注意
- GitHub Actions 定时为 **best-effort**：高峰可能延迟几分钟，不适合做秒级精确，但 5 分钟粒度足够。
- 私有仓库免费额度内（每月 2000 Actions 分钟），本任务约每天 1–2 分钟，远未触顶。
- 每 5 分钟一次会积累不少 commit；介意可在 `record.yml` 里改成 `--amend` 强推单提交（按需）。
- 本仓库只存数据，不要和 disney-planner 代码混在一起，保持干净。
