# 能力契约

每条学习分析保存为 JSON；参考 schemas/analysis.schema.json。核心存储有结构校验。kind 分 skill/pattern/implementation/preference。

skill、pattern、implementation 都包含 title/summary/capabilities/design/implementation/dependencies/inputs/outputs/evidence/verification/provenance/overlaps/conflicts/related_ids。

- design：purpose（必填），适用条件、阶段和不适用条件。
- implementation：strategy=direct/adapt/own/knowledge-only；engines（列表）、details、limitations（列表）。不是不同框架同名参数的简单翻译。
- dependencies：type=executable/path/manual；name；可选value、note。系统检查本地路径与可执行文件存在。manual 用于账号、插件版本、服务访问等不能凭存在判断的条件，默认 unknown；真实检查后可附check，包含path/sha256/checked_at/expires_at，只有证据未变且在有效时间内才标available。时间为带时区ISO格式，不能存凭据；不因旧日志就假定永久可用。
- inputs/outputs：语义输入输出词表。inputs 是必须项，screenshots/copy/audio等按实际任务填写；可选项写在design或limitations。outputs 包括 mp4/design/html/source等；只返回提示词不标 mp4。
- role：primary 或 specialist。一个工程只选一个 primary。
- evidence：source 和 observation，视频可含 time_range、inference、confidence。不能写虚构时间码。
- verification：level=read/runnable/reproduced/reusable；非read需要本地证据文件 path/sha256/result，内容与结果仍由Codex核验，文件存在不证明审美质量。
- provenance：license 与 copy_permission，未知写 unknown/not-established。自有或复制模块必须 original/permitted。保留原作者、版本、链接；许可未明确时只学机制，不搬代码。
- overlaps：已有记录ID或明确重叠说明；conflicts：已知冲突记录ID（路由互斥）以及文字说明（人工判断）；related_ids：参考、移植、复现间关联。

source 由系统绑定真实文件或 Skill 内容哈希，不能由 analysis 覆写；record_id稳定，候选版本独立。新Skill来源采用规范化路径区分同名安装副本；语义重复只提示，不静默合并或删除。

preference 特例只需 kind/title/summary/action/value；action=like/avoid/favorite/reject-pattern。favorite、reject-pattern的value为已有已确认记录ID。需要撤销偏好时撤销该preference记录，不改默认种子或其他项目。
