---
date: 2025-01-19
topic: "监控设计"
version: 1.0.0
status: draft
---

# 监控设计

## 1. 概述

平台提供完整的监控集成能力，包括指标采集、告警规则、仪表板和通知渠道。

## 2. 监控架构

```
┌─────────────────────────────────────────────────────────────┐
│                    监控需求分层                              │
├─────────────────────────────────────────────────────────────┤
│  告警层 → 可视化层 → 采集层 → 暴露层                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Agent Exporter (端口 9090)                             │   │
│  │  ├── Agent 自身指标                                      │   │
│  │  └── 中间件业务指标                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
```

## 3. 指标分类

| 分类 | 示例 | 说明 |
|-----|-----|------|
| **中间件业务指标** | redis_connected_clients, redis_used_memory_bytes, redis_ops_per_second | 中间件特定的业务指标 |
| **Agent 指标** | agent_up, agent_restart_count, agent_gRPC_requests_total | Agent 自身的运行指标 |
| **平台指标** | middleware_component_ready, middleware_group_replicas | 平台级别的状态指标 |

### 3.1 Agent 核心指标

| 指标 | 类型 | 说明 |
|-----|-----|------|
| `agent_up` | Gauge | Agent 是否运行 |
| `agent_restart_count` | Counter | Agent 重启次数 |
| `agent_gRPC_requests_total` | Counter | gRPC 请求总数 |
| `agent_gRPC_request_duration_seconds` | Histogram | gRPC 请求延迟 |
| `agent_process_uptime_seconds` | Gauge | 中间件进程运行时间 |

### 3.2 中间件业务指标（Redis 示例）

| 指标 | 类型 | 说明 |
|-----|-----|------|
| `redis_connected_clients` | Gauge | 客户端连接数 |
| `redis_used_memory_bytes` | Gauge | 已使用内存 |
| `redis_max_memory_bytes` | Gauge | 最大内存限制 |
| `redis_ops_per_second` | Counter | 每秒操作数 |
| `redis_keyspace_hits_total` | Counter | 键空间命中数 |
| `redis_keyspace_misses_total` | Counter | 键空间未命中数 |
| `redis_master_link_status` | Gauge | 主从连接状态 |
| `redis_role` | Gauge | 节点角色 (0=slave, 1=master) |

## 4. 监控配置

### 4.1 完整配置示例

```yaml
monitoring:
  enabled: true                          # 是否启用监控
  settings:
    interval: 30s                        # 采集间隔
    scrapeTimeout: 10s                   # 采集超时
    path: /metrics                       # 指标路径
    port: 9090                           # 采集端口
    
    serviceMonitor:
      enabled: true                      # 是否创建 ServiceMonitor
      namespace: monitoring              # ServiceMonitor 命名空间
      labels:
        release: prometheus              # Prometheus 实例标签
    
    alerts:
      enabled: true                      # 是否启用告警
      useBuiltin: true                   # 是否使用内置告警规则
      disabledRules:                     # 禁用的告警规则
        - RedisHighMemory
    
    dashboard:
      enabled: true                      # 是否创建仪表板
      useBuiltin: true                   # 是否使用内置仪表板
    
    notification:
      enabled: true                      # 是否启用通知
      channels:                          # 通知渠道
        - name: email
          type: email
          settings:
            to: "ops@example.com"
        - name: webhook
          type: webhook
          settings:
            url: "https://alerts.example.com/webhook"
        - name: slack
          type: slack
          settings:
            channel: "#alerts"
            webhookUrl: "https://hooks.slack.com/..."
    
    retention:
      enabled: true                      # 是否启用指标保留策略
      remote:
        enabled: true                    # 是否启用远程存储
        storage:
          type: thanos                   # 存储类型
          config:
            bucket: "middleware-metrics"
```

### 4.2 ServiceMonitor 示例

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: production-redis
  namespace: monitoring
  labels:
    release: prometheus
spec:
  namespaceSelector:
    matchNames:
      - default
  selector:
    matchLabels:
      middleware.io/app: production-redis
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
      scheme: http
```

## 5. 告警规则

### 5.1 内置告警规则（Redis 示例）

```yaml
monitoring:
  alerts:
    - name: RedisDown
      expr: agent_up == 0
      for: 1m
      severity: critical
      annotations:
        summary: "Redis instance is down"
        description: "Redis instance {{ $labels.pod }} has been down for more than 1 minute"
      
    - name: RedisHighMemory
      expr: redis_used_memory_bytes / redis_max_memory > 0.85
      for: 5m
      severity: warning
      annotations:
        summary: "Redis high memory usage"
        description: "Redis memory usage is above 85%: {{ $value | humanize1024 }}"
      
    - name: RedisReplicationLag
      expr: redis_master_link_status == 0
      for: 2m
      severity: critical
      annotations:
        summary: "Redis replication lag"
        description: "Redis replication link is down for {{ $labels.pod }}"
      
    - name: RedisTooManyConnections
      expr: redis_connected_clients > 2000
      for: 5m
      severity: warning
      annotations:
        summary: "Redis too many connections"
        description: "Redis has too many connections: {{ $value }}"
```

### 5.2 自定义告警规则

```yaml
monitoring:
  alerts:
    enabled: true
    useBuiltin: true  # 保留内置规则
    
    customRules:      # 添加自定义规则
      - name: RedisHighLatency
        expr: redis_latency_ms > 100
        for: 2m
        severity: warning
        annotations:
          summary: "Redis high latency"
```

## 6. 仪表板配置

### 6.1 内置仪表板

平台提供以下内置仪表板：

| 仪表板 | 中间件 | 说明 |
|-------|-------|------|
| Redis Overview | Redis | Redis 整体状态概览 |
| Redis Performance | Redis | 性能指标详细视图 |
| Redis Replication | Redis | 主从复制状态 |
| Kafka Overview | Kafka | Kafka 整体状态 |
| Kafka Performance | Kafka | Kafka 性能指标 |

### 6.2 自定义仪表板

```yaml
monitoring:
  dashboard:
    enabled: true
    useBuiltin: true
    customDashboards:
      - name: "My Custom Dashboard"
        json: |
          {
            "dashboard": {
              "title": "Custom Dashboard",
              "panels": [...]
            }
          }
```

## 7. 通知渠道

### 7.1 支持的渠道类型

| 类型 | 配置项 |
|-----|-------|
| **Email** | to, from, smtp 服务器配置 |
| **Webhook** | url, headers, method |
| **Slack** | channel, webhookUrl |
| **PagerDuty** | serviceKey, routingKey |
| **DingTalk** | accessToken, keyword |

### 7.2 通知配置示例

```yaml
notification:
  enabled: true
  channels:
    - name: email
      type: email
      settings:
        to: "ops@example.com,dev@example.com"
        from: "alerts@example.com"
        smtp:
          host: "smtp.example.com"
          port: 587
          username: "alerts"
          passwordSecretRef:
            name: smtp-credentials
            key: password
    
    - name: webhook
      type: webhook
      settings:
        url: "https://alerts.example.com/webhook"
        method: POST
        headers:
          Authorization: "Bearer ${WEBHOOK_TOKEN}"
    
    - name: slack
      type: slack
      settings:
        channel: "#middleware-alerts"
        webhookUrl: "https://hooks.slack.com/services/xxx/xxx/xxx"
```

## 8. 文档导航

- 上一章：[高可用设计](./07-high-availability.md)
- 下一章：[备份恢复](./09-backup-restore.md)
- 相关文档：[Agent 设计](./06-agent-design.md)
