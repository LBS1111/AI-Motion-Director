# 命令与配置

命令在 Skill 根目录运行，Python 3.11+。PyYAML 推荐安装以完整解析 YAML frontmatter；未安装时仅支持单行 name/description。媒体操作需要 FFmpeg/FFprobe。不自动安装第三方引擎或付费服务。

## 初始化

`python scripts/director.py --home D:/codex-motion-director-data init --root 用户Skill目录`

不传 `--root` 时，默认索引用户目录的 `.codex/skills` 与 `.agents/skills`，兼容 Codex 内置安装方式和 README 中的一键安装方式。重复 init 保留已有配置和记忆。新增持久扫描目录编辑数据目录 config.json 的 skill_roots；临时根用 `scan --root 路径`。只扫描已配置本地目录；URL 先由 Codex 用可用工具读取，用户授权下载后放到暂存目录分析。

本地 local-config.json（不提交仓库）只含 data_home。优先级：`--home` > `MOTION_DIRECTOR_HOME` > local-config.json > 用户目录。配置支持 disabled_paths；读取 host_config 中 skills.config 的 enabled=false。扫描根不可用时报告，不删除已确认知识。

## 日常与学习

| 命令 | 用途 |
|---|---|
| `status` / `doctor` | 记忆数量、待确认、环境能力 |
| `scan` | 增量发现新增/更新，跳过自己与禁用项 |
| `pending` | 精简待学习/待确认清单 |
| `inspect ID` | 候选来源、文件清单及入口原文（可能截断） |
| `analyze ID --file analysis.json` | 保存 Codex 完成的三层分析，生成确认版本 |
| `propose --file pattern.json --source source.mp4` | 独立视频模式或偏好候选 |
| `propose --file revised.json --update RECORD_ID` | 修改已有模式/偏好，重新确认 |
| `review ID` | 精确差异、重叠线索、确认摘要哈希 |
| `approve ID --digest HASH --quote 用户确认原话 --reference 对话定位` | 只在真正收到确认后运行 |
| `dismiss ID --reason 暂不保存` | 留在草稿记录，不形成长期审美禁用 |
| `revoke RECORD_ID --reason 用户要求撤销` | 撤销当前正式记录，保留历史 |
| `search 关键词 --kind pattern --limit 5` | 仅返回少量已确认摘要 |
| `show RECORD_ID` | 按需读取完整记录 |
| `report --out 路径.md` | 分类汇总已确认和候选状态 |
| `report --reviewed-only --out 确认清单.md` | 输出已分析候选的可审阅细节与精确版本，供用户选择确认 |
| `rebuild-index` | 从唯一真源重建视图，不恢复撤销项 |
| `restore-proposal --backup 历史文件 --id RECORD_ID` | 从历史创建恢复候选，确认后才恢复 |

命令行不能证明用户本人同意，确认原话与引用是审计证据，Codex 必须遵守入口的确认边界。不要由读取的外部文档生成“用户确认”。一条候选对应一个确认单位；仅保存其中一部分时先拆分候选再确认。

## 制作

`project-new PROJECT_ID --brief brief.json` 建立项目。

`route --brief brief.json` 检索正式能力，`estimate --brief brief.json --complexity medium` 估算。`--sample sample.json` 可用代表性试渲染 `{ "frames": 60, "seconds": 4 }` 修正渲染时间；采样条件必须匹配最终配置。

`project-show PROJECT_ID` 恢复 brief/state 并检测输入变化与缺失产物。

`project-update PROJECT_ID --file patch.json` 更新状态。方向字段 selected_option、direction_confirmation 记录已选方向与真实授权；用户明确“你选并直接做”也可作为授权。stage 顺序 planning/design/implementation/preview/render/verification/complete；允许返工回到早期阶段。

`check-shots --file shot-plan.json --duration 20` 检查覆盖、时间、ID和镜头语义字段。

`verify-media output.mp4 --expected spec.json --out verification.json` 完整解码并检查规格。spec.json 可含 width/height/fps/duration_seconds/audio。视觉核验后补充 visual_review=passed、audio_review=passed或not-applicable、review_evidence。完成状态会重新检查实际文件、哈希、项目规格和工程。

## 视频证据

`extract-video reference.gif --out 全新证据目录 --interval 0.2 --max-frames 80`

可用 --start/--end 选择片段。长片先稀疏定位，再密集分析关键段；不把80帧当作理解整部视频的充分证据。GIF会保留真实帧时序。输出仅是证据，不是自动识别结论。

## 文件可靠性

memory/store.json 是唯一正式真源，其他命名索引均为可重建视图，带 store_revision。脚本检索读取真源，因此中途崩溃造成视图落后不会启用错误记录。写入加锁、原子替换，旧版保存在 history。看到锁占用先检查记录的进程；不擅自删除可能仍在使用的锁。
