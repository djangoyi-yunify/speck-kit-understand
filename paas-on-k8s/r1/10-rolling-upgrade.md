---
date: 2025-01-19
topic: "滚动升级"
version: 1.0.0
status: draft
---

# 滚动升级

## 1. 概述

平台支持中间件版本的滚动升级，具备分区升级（金丝雀发布）和回滚能力。

## 2. 滚动升级流程

```
Group Controller 检测 runtimeVersion 变更
        │
        ▼
┌─────────────────────────────────────────────────┐
│  步骤 1：验证新版本兼容性                        │
│  • 检查 Plugin 是否支持新版本                   │
│  • 验证镜像可访问                               │
│  • 检查存储兼容性                               │
└────────────────────┬────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  步骤 2：准备滚动升级                            │
│  • 更新 Group status.phase = Upgrading          │
│  • 记录检查点                                   │
│  • 暂停调度（如果需要）                         │
└────────────────────┬────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  步骤 3：逐个/分批更新 Pod                       │
│                                                 │
│  For each pod (按索引顺序):                      │
│  ├── 触发主动故障转移（如需）                    │
│  ├── 停止旧 Pod                                 │
│  ├── 创建新 Pod (新镜像)                         │
│  ├── 等待新 Pod Ready                            │
│  ├── 执行 postUpgradeVerify                      │
│  ├── 验证成功 → 继续下一个                       │
│  └── 验证失败 → 触发回滚                         │
└────────────────────┬────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  步骤 4：完成                                    │
│  • 更新 Group status.phase = Running             │
│  • 更新 runtime.currentVersion                   │
│  • 清理旧资源                                   │
```

## 3. 滚动升级配置

### 3.1 完整配置示例

```yaml
spec:
  rollingUpdate:
    maxSurge: 1                        # 最大超额 Pod 数
    maxUnavailable: 0                  # 最大不可用 Pod 数
    partition: 0                       # 分区升级索引
    timeout: 300s                      # 单个 Pod 升级超时
  
  # 升级前检查
  preUpgradeCheck:
    enabled: true
    type: health-check                 # 检查类型
    timeout: 30s
  
  # 升级后验证
  postUpgradeVerify:
    enabled: true
    type: exec
    command: redis-cli ping            # 验证命令
    expected: PONG                     # 期望输出
  
  # 回滚策略
  rollback:
    enabled: true                      # 启用回滚
    onFailure: true                    # 失败时自动回滚
    limit: 3                           # 最大回滚次数
```

### 3.2 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `maxSurge` | integer | 1 | 滚动更新时允许超过期望的 Pod 数量 |
| `maxUnavailable` | integer | 0 | 滚动更新时允许不可用的 Pod 数量 |
| `partition` | integer | 0 | 分区升级索引，只升级索引 >= partition 的 Pod |
| `timeout` | string | 300s | 单个 Pod 升级超时时间 |

## 4. 分区升级（金丝雀发布）

### 4.1 分区升级说明

分区升级允许您逐步升级 Pod，先升级少量实例验证后再升级全部。

```yaml
# 示例：3 个副本，只升级索引 2 之后的 Pod
rollingUpdate:
  partition: 2  # 只升级索引 2, 3, 4... 的 Pod
```

### 4.2 分区升级流程

```
原始状态：Pod 0, Pod 1, Pod 2 (partition=2)
                  │
                  ▼
┌─────────────────────────────────────────┐
│  第一阶段：升级索引 >= 2 的 Pod          │
│  升级 Pod 2                              │
│  验证成功后继续                           │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│  第二阶段：降低 partition 值             │
│  partition = 0                          │
│  升级剩余 Pod                            │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│  完成：所有 Pod 升级到新版本              │
└─────────────────────────────────────────┘
```

### 4.3 金丝雀发布示例

```yaml
# 金丝雀发布：先升级 1 个实例
rollingUpdate:
  maxSurge: 1
  maxUnavailable: 0
  partition: 2  # 假设副本数为 3，从第 3 个开始升级
```

## 5. 升级前检查

### 5.1 健康检查

```yaml
preUpgradeCheck:
  enabled: true
  type: health-check
  timeout: 30s
```

### 5.2 自定义检查

```yaml
preUpgradeCheck:
  enabled: true
  type: custom
  command: |
    # 自定义检查命令
    redis-cli INFO replication | grep master_link_status
  expected: up
  timeout: 30s
```

## 6. 升级后验证

### 6.1 命令执行验证

```yaml
postUpgradeVerify:
  enabled: true
  type: exec
  command: redis-cli ping
  expected: PONG
  timeout: 30s
```

### 6.2 指标验证

```yaml
postUpgradeVerify:
  enabled: true
  type: metrics
  metrics:
    - name: redis_up
      expected: 1
    - name: redis_connected_clients
      expected: ">0"
```

### 6.3 HTTP 验证

```yaml
postUpgradeVerify:
  enabled: true
  type: http
  endpoint: /health
  expectedStatus: 200
  timeout: 10s
```

## 7. 回滚机制

### 7.1 回滚配置

```yaml
rollback:
  enabled: true              # 启用回滚
  onFailure: true            # 失败时自动回滚
  limit: 3                   # 最大回滚次数
```

### 7.2 回滚流程

```
升级失败
        │
        ▼
┌─────────────────────────────────────┐
│  检查回滚条件                        │
│  • rollback.enabled == true         │
│  • rollback.onFailure == true       │
│  • 当前回滚次数 < rollback.limit     │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  执行回滚                            │
│  • 更新镜像为旧版本                  │
│  • 重新创建 Pod                      │
│  • 更新 Group status                 │
│  • 发送告警通知                      │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  验证回滚结果                        │
│  • 所有 Pod 就绪                     │
│  • 验证通过 → 回滚完成               │
│  • 验证失败 → 继续回滚或标记失败     │
└─────────────────────────────────────┘
```

### 7.3 回滚限制

```
回滚次数计数逻辑：
├── 每次失败升级触发回滚计数 +1
├── 成功升级后重置计数
└── 达到 limit 后停止自动回滚
```

## 8. 升级状态追踪

### 8.1 Group Status 中的升级状态

```yaml
status:
  phase: Upgrading
  currentVersion: "7.4"
  targetVersion: "7.4.1"
  
  upgradeStatus:
    phase: InProgress
    fromVersion: "7.4"
    toVersion: "7.4.1"
    startedAt: "2025-01-19T10:00:00Z"
    completedAt: null
    updatedReplicas: 2
    totalReplicas: 4
    currentIndex: 2  # 当前正在升级的 Pod 索引
    
    failures:
      - index: 1
        error: "镜像拉取失败"
        timestamp: "2025-01-19T10:05:00Z"
        recovered: true  # 是否已恢复
```

## 9. 最佳实践

| 场景 | 推荐配置 |
|-----|---------|
| **零停机升级** | maxUnavailable: 0, maxSurge: 1 |
| **最小资源占用** | maxUnavailable: 1, maxSurge: 0 |
| **金丝雀发布** | partition: replicas - 1 |
| **生产环境** | 启用 preUpgradeCheck 和 postUpgradeVerify |
| **关键数据** | 启用 rollback.onFailure |

## 10. 文档导航

- 上一章：[备份恢复](./09-backup-restore.md)
- 下一章：[数据流](./11-data-flow.md)
- 相关文档：[Agent 设计](./06-agent-design.md)、[高可用设计](./07-high-availability.md)
