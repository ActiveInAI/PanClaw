# AGENTS.md · PanClaw

默认使用简体中文协作。

PanClaw 是 OpenClaw 与 Hermes-style Agent 编排的融合项目,定位是本地优先、可审计、可审批、可私有化部署的 Skills/Tools 控制层。

## 强约束

1. 不把任何模型、消息平台、云厂商或第三方库作为不可替换核心。
2. 所有外部能力必须通过 Skill Registry + ToolRouter + 审批 + 审计。
3. 高风险动作默认 dry-run: 桌面控制、网页登录、下单、支付、发消息、创建云资源、医疗/金融/法律建议、军事情报分析。
4. 个人微信不得使用逆向、hook、非官方 Web 协议或规避平台条款的方式接入。只允许官方/合规通道。
5. GPL/AGPL/SSPL/BUSL/Commons Clause 依赖不得进入分发边界; 只能作为外部进程、Sidecar、HTTP 服务或人工安装的授权适配器。
6. 医疗、健康、金融、法律、建筑、军事等领域输出只能是经验建议或资料整理,不得直接标为诊断、投资建议、法律意见、合规结论、施工/报审/验收就绪。
7. Registry 优先于硬编码 enum; 新 Skill 必须登记输入输出、权限、风险、许可证边界和审批策略。
8. 保留 OpenClaw/Hermes 上游边界: PanClaw 只做适配与编排,不复制上游代码。

