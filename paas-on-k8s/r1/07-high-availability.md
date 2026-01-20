---
date: 2025-01-19
topic: "高可用设计"
version: 1.0.0
status: draft
---

# 高可用设计

## 1. 概述

平台支持两种高可用模式：被动高可用（依赖中间件自身能力）和主动故障转移（主动触发角色切换）。

## 2. 两种高可用模式对比

| 模式 | 说明 | 触发方式 |
|-----|-----|---------|
| **被动高可用** | 依赖中间件自身的高可用能力 | 自动检测角色变化 |
| **主动故障转移** | 主动调用中间件工具触发故障转移 | Pod 重启、滚动升级 |

## 3. 被动高可用（角色检测）

### 3.1 角色检测机制

```yaml
highAvailability:
  passive:
    enabled: true
    roleDetection:
      type: exec                    # 检测类型：exec
      command: "redis-cli role"     # 检测命令
      parsePattern: "role:([^\\s]+)" # 解析正则
      interval: 10s                 # 检测间隔
```

### 3.2 角色检测流程

```
Agent 2 定期执行角色检测命令
              │
              ▼
┌─────────────────────────────────────┐
│  解析命令输出                        │
│  示例: redis-cli role 输出          │
│  → role:master                      │
│  →  связанных:1                     │
│  → master_link_status:up            │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  更新 Group.status.roleInfo         │
│  • currentRole: master              │
│  • lastRoleChange: <timestamp>      │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  通知 Controller 更新 Service       │
│  (如果配置了 Role-based Service)    │
└─────────────────────────────────────┘
```

### 3.3 支持的中间件角色

| 中间件 | 角色类型 | 检测命令示例 |
|-------|---------|------------|
| Redis | master, slave | `redis-cli role` |
| Kafka | leader, follower | `kafka-run-class.sh ...` |
| Zookeeper | leader, follower | `zkServer.sh status` |
| Etcd | leader, follower | `etcdctl endpoint status` |

## 4. 主动故障转移

### 4.1 故障转移触发场景

| 场景 | 触发条件 | 处理方式 |
|-----|---------|---------|
| **Pod 重启** | Master/Primary Pod 需要重启 | 触发故障转移后再重启 |
| **滚动升级** | 升级 Master/Primary Pod | 触发故障转移后再升级 |
| **手动触发** | 用户手动触发故障转移 | 执行故障转移流程 |
| **健康检查失败** | 主节点健康检查连续失败 | 自动触发故障转移 |

### 4.2 故障转移流程

```
场景 1：Pod 重启
├── 检测到 Pod 需要重启
├── 如果是 Master/Primary 节点
│   └── 触发主动故障转移
│       ├── 调用 Agent 2 gRPC Failover
│       ├── 等待故障转移完成
│       └── 验证新角色
└── 继续 Pod 重启流程

场景 2：滚动升级
├── 准备升级的 Pod
├── 如果 Pod 角色是 Master/Primary
│   └── 触发主动故障转移
└── 继续滚动升级流程
```

### 4.3 故障转移配置

```yaml
highAvailability:
  enabled: true
  passive:
    enabled: true
    roleDetection:
      type: exec
      command: "redis-cli role"
      parsePattern: "role:([^\\s]+)"
      interval: 10s
  active:
    enabled: true
    failoverCommand:
      type: exec
      command: "redis-cli"
      args: ["failover", "--timeout", "30s"]
    preFailoverCheck:
      enabled: true
      type: health
      timeout: 10s
    postFailoverVerify:
      enabled: true
      type: exec
      command: "redis-cli role"
      expectedRole: "master"
      timeout: 30s
```

### 4.4 故障转移时序图

```
Controller                     Agent 2                   中间件
    │                             │                         │
    │── gRPC: Failover() ────────►│                         │
    │                             │── exec: failover ──────►│
    │                             │                         │── 角色切换
    │                             │◄── success ─────────────│
    │                             │                         │
    │                             │── 检测新角色 ──────────►│
    │                             │◄── role: master ───────│
    │                             │                         │
    │◄── FailoverResponse ────────│                         │
    │     success=true            │                         │
    │     newRole=master          │                         │
    │                             │                         │
```

## 5. 回滚策略

### 5.1 配置示例

```yaml
rollback:
  enabled: true              # 启用回滚
  onFailure: true            # 失败时自动回滚
  limit: 3                   # 最大回滚次数
```

### 5.2 回滚流程

```
故障转移失败
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
│  • 调用中间件恢复原角色              │
│  • 更新 Group.status.phase = Failed │
│  • 发送告警通知                      │
└─────────────────────────────────────┘
```

## 6. 高可用配置最佳实践

| 配置项 | 推荐值 | 说明 |
|-------|-------|------|
| `roleDetection.interval` | 10s | 检测间隔，太短会增加负载 |
| `failoverCommand.timeout` | 30s | 故障转移超时时间 |
| `preFailoverCheck.timeout` | 10s | 故障转移前检查超时 |
| `postFailoverVerify.timeout` | 30s | 故障转移后验证超时 |
| `rollback.limit` | 3 | 最大回滚次数 |

## 7. 文档导航

- 上一章：[Agent 设计](./06-agent-design.md)
- 下一章：[监控设计](./08-monitoring.md)
- 相关文档：[滚动升级](./10-rolling-upgrade.md)
