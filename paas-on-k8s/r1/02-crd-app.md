---
date: 2025-01-19
topic: "CRD 规范 - App"
version: 1.0.0
status: draft
---

# CRD 规范 - App

## 1. 概述

App 是中间件实例的顶层资源，代表一个完整的中间件部署。每个 App 绑定一个插件版本，指定运行时版本，并可包含多个 Component。

## 2. App CRD 完整规范

### 2.1 Schema

```yaml
apiVersion: middleware.io/v1alpha1
kind: App
metadata:
  name: string                          # App 名称
  namespace: string                     # 命名空间
  labels:
    middleware.io/app: string           # 中间件类型标签
spec:
  # 插件绑定（必需）
  plugin:
    name: string                        # 插件名称
    version: string                     # 插件版本
  
  # 运行时版本（必需）
  runtime:
    name: string                        # 运行时名称（如 redis, kafka）
    version: string                     # 运行时版本（如 7.4, 3.2）
  
  # 中间件配置（可选）
  config:
    [key]: [value]                     # 任意配置项
  
  # 监控配置（可选）
  monitoring:
    enabled: boolean                    # 是否启用监控（默认: true）
    settings:
      interval: string                  # 采集间隔（默认: 30s）
      serviceMonitor:
        enabled: boolean                # 是否创建 ServiceMonitor
        namespace: string               # ServiceMonitor 命名空间
        labels: map[string]string       # 自定义标签
      alerts:
        enabled: boolean                # 是否启用告警
        useBuiltin: boolean             # 是否使用内置规则
        disabledRules: []string         # 禁用的告警规则列表
      dashboard:
        enabled: boolean                # 是否创建仪表板
        useBuiltin: boolean             # 是否使用内置仪表板
      notification:
        enabled: boolean                # 是否启用通知
        channels:
          - name: string                # 渠道名称
            type: string                # 渠道类型（email, webhook, slack）
            settings: map[string]any   # 渠道配置
      retention:
        enabled: boolean                # 是否启用保留策略
        remote:
          enabled: boolean              # 是否启用远程存储
          storage:
            type: string                # 存储类型（thanos, prometheus）
            config: map[string]string  # 存储配置
  
  # 备份配置（可选）
  backup:
    enabled: boolean                    # 是否启用备份（默认: false）
    storage:
      provider: string                  # 存储提供商（s3, gcs, azure, minio）
      bucket: string                    # 存储桶名称
      region: string                    # 区域
      secretRef:
        name: string                    # 密钥名称
        namespace: string               # 密钥命名空间
    settings:
      volumeAccess:
        method: string                  # 访问方法（shared-pvc, exclusive-pvc）
        readOnly: boolean               # 是否只读挂载
      consistency:
        enabled: boolean                # 是否启用一致性检查
        command: string                 # 一致性检查命令
        waitForCompletion: boolean      # 是否等待命令完成
        timeout: string                 # 超时时间
      archive:
        format: string                  # 归档格式（tar.gz）
        compressionLevel: integer       # 压缩级别（1-9）
      checksum:
        algorithm: string               # 校验和算法（sha256, sha512）
      encryption:
        enabled: boolean                # 是否启用加密
        algorithm: string               # 加密算法（aes256-gcm, aes256-cbc）
        keySecretRef:
          name: string                  # 密钥名称
          namespace: string             # 密钥命名空间
          keyField: string              # 密钥字段
        keyRotation:
          enabled: boolean              # 是否启用密钥轮换
          interval: string              # 轮换间隔
          keepOldKeys: boolean          # 是否保留旧密钥
          oldKeysRetention: string      # 旧密钥保留时间
    retention:
      remoteRetention: string           # 远程保留时间
      keepCount: integer                # 保留备份数量
    schedule:
      enabled: boolean                  # 是否启用计划备份
      cron: string                      # Cron 表达式
status:
  phase: string                         # 状态（Pending, Running, Failed）
  components: []ComponentStatus         # Component 状态列表
```

### 2.2 ComponentStatus

```yaml
ComponentStatus:
  - name: string                        # Component 名称
    ready: boolean                      # 是否就绪
```

## 3. 配置示例

### 3.1 Redis App 配置示例

```yaml
apiVersion: middleware.io/v1alpha1
kind: App
metadata:
  name: production-redis
  namespace: default
  labels:
    middleware.io/app: redis
spec:
  # 插件绑定
  plugin:
    name: redis
    version: "2.0.0"
  
  # 运行时版本
  runtime:
    name: redis
    version: "7.4"
  
  # 中间件配置
  config:
    redisConfig:
      maxmemory: "2gb"
      appendonly: "yes"
  
  # 监控配置
  monitoring:
    enabled: true
    settings:
      interval: 30s
      serviceMonitor:
        enabled: true
        namespace: monitoring
        labels:
          release: prometheus
      alerts:
        enabled: true
        useBuiltin: true
        disabledRules:
          - RedisHighMemory
      dashboard:
        enabled: true
        useBuiltin: true
      notification:
        enabled: true
        channels:
          - name: email
            type: email
            settings:
              to: "ops@example.com"
          - name: webhook
            type: webhook
            settings:
              url: "https://alerts.example.com/webhook"
      retention:
        enabled: true
        remote:
          enabled: true
          storage:
            type: thanos
            config:
              bucket: "middleware-metrics"
  
  # 备份配置
  backup:
    enabled: true
    storage:
      provider: s3
      bucket: middleware-backups
      region: us-east-1
      secretRef:
        name: backup-credentials
        namespace: middleware-system
    settings:
      volumeAccess:
        method: shared-pvc
        readOnly: true
      consistency:
        enabled: true
        command: redis-cli BGSAVE
        waitForCompletion: true
        timeout: 30s
      archive:
        format: tar.gz
        compressionLevel: 6
      checksum:
        algorithm: sha256
      encryption:
        enabled: true
        algorithm: aes256-gcm
        keySecretRef:
          name: backup-encryption-key
          namespace: middleware-system
          keyField: key
        keyRotation:
          enabled: true
          interval: 90d
          keepOldKeys: true
          oldKeysRetention: 7d
    retention:
      remoteRetention: 30d
      keepCount: 7
    schedule:
      enabled: false
      cron: "0 2 * * *"

status:
  phase: Running
  components:
    - name: redis-nodes
      ready: true
```

## 4. 文档导航

- 上一章：[架构概览](./01-architecture-overview.md)
- 下一章：[Component CRD 规范](./03-crd-component.md)
- 相关文档：[备份恢复](./09-backup-restore.md)、[监控设计](./08-monitoring.md)
