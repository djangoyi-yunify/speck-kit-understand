---
date: 2025-01-19
topic: "CRD 规范 - Group"
version: 1.0.0
status: draft
---

# CRD 规范 - Group

## 1. 概述

Group 是资源配置分组的底层资源，同一个 Group 下的所有 Pod 具有相同的规格和配置。Group 由 Component Controller 自动创建，用户通常不需要直接操作。

## 2. Group CRD 完整规范

### 2.1 Schema

```yaml
apiVersion: middleware.io/v1alpha1
kind: Group
metadata:
  name: string                          # Group 名称
  namespace: string                     # 命名空间
  labels:
    middleware.io/app: string           # App 名称
    middleware.io/component: string     # Component 名称
    middleware.io/plugin: string        # 插件名称
    middleware.io/plugin-version: string # 插件版本
spec:
  # Component 引用（必需）
  componentRef:
    name: string                        # 关联的 Component 名称
    namespace: string                   # Component 所在命名空间
  
  # Plugin 引用（必需）
  pluginRef:
    name: string                        # Plugin ConfigMap 名称
    namespace: string                   # Plugin 所在命名空间
  
  # 副本配置（必需）
  replicas: integer                     # Pod 副本数
  
  # 资源规格（必需）
  resources:
    requests:
      cpu: string                       # CPU 请求
      memory: string                   # 内存请求
    limits:
      cpu: string                       # CPU 限制
      memory: string                   # 内存限制
  
  # 滚动升级策略（可选）
  rollingUpdate:
    maxSurge: integer                   # 最大超额 Pod 数
    maxUnavailable: integer             # 最大不可用 Pod 数
    partition: integer                  # 分区升级索引
    timeout: string                     # 超时时间
  
  # 升级前检查（可选）
  preUpgradeCheck:
    enabled: boolean                    # 是否启用
    type: string                       # 检查类型（health-check）
    timeout: string                     # 超时时间
  
  # 升级后验证（可选）
  postUpgradeVerify:
    enabled: boolean                    # 是否启用
    type: string                       # 验证类型（exec）
    command: string                    # 验证命令
    expected: string                   # 期望输出
  
  # 运行时配置（可选）
  values:
    [key]: [value]                     # 任意运行时配置
  
  # 回滚策略（可选）
  rollback:
    enabled: boolean                    # 是否启用回滚
    onFailure: boolean                 # 失败时自动回滚
    limit: integer                     # 最大回滚次数
  
  # 高可用配置（可选）
  highAvailability:
    enabled: boolean                    # 是否启用高可用
    passive:
      enabled: boolean                  # 是否启用被动高可用
      roleDetection:
        type: string                   # 检测类型（exec）
        command: string                # 检测命令
        parsePattern: string           # 解析正则
        interval: string               # 检测间隔
    active:
      enabled: boolean                  # 是否启用主动故障转移
      failoverCommand:
        type: string                   # 命令类型（exec）
        command: string                # 命令
        args: []string                # 命令参数
      preFailoverCheck:
        enabled: boolean               # 是否启用故障转移前检查
        type: string                  # 检查类型（health）
        timeout: string               # 超时时间
      postFailoverVerify:
        enabled: boolean               # 是否启用故障转移后验证
        type: string                  # 验证类型（exec）
        command: string               # 验证命令
        expectedRole: string          # 期望角色
        timeout: string               # 超时时间
status:
  phase: string                         # 状态
  readyReplicas: integer               # 就绪副本数
  currentVersion: string               # 当前版本
  targetVersion: string                # 目标版本
  
  # 角色信息
  roleInfo:
    currentRole: string                # 当前角色
    lastRoleChange: string             # 上次角色变更时间
  
  # 升级状态
  upgradeStatus:
    phase: string                      # 升级阶段
    fromVersion: string                # 源版本
    toVersion: string                  # 目标版本
    updatedReplicas: integer           # 已更新副本数
    totalReplicas: integer             # 总副本数
```

## 3. 配置示例

### 3.1 Redis Group 配置示例

```yaml
apiVersion: middleware.io/v1alpha1
kind: Group
metadata:
  name: master-group
  namespace: default
  labels:
    middleware.io/app: production-redis
    middleware.io/component: redis-nodes
    middleware.io/plugin: redis
    middleware.io/plugin-version: "2.0.0"
spec:
  componentRef:
    name: redis-nodes
    namespace: default
  pluginRef:
    name: redis-plugin-v2.0
    namespace: middleware-system
  replicas: 1
  resources:
    requests:
      cpu: "1"
      memory: "2Gi"
    limits:
      cpu: "2"
      memory: "4Gi"
  
  # 滚动升级策略
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
    partition: 0
    timeout: 300s
  
  # 升级前检查
  preUpgradeCheck:
    enabled: true
    type: health-check
    timeout: 30s
  
  # 升级后验证
  postUpgradeVerify:
    enabled: true
    type: exec
    command: redis-cli ping
    expected: PONG
  
  # 运行时配置
  values:
    redisConfig:
      maxmemory: "2gb"
      appendfsync: "everysec"
  
  # 回滚策略
  rollback:
    enabled: true
    onFailure: true
    limit: 3
  
  # 高可用配置
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
        command: redis-cli role
        expectedRole: "master"
        timeout: 30s

status:
  phase: Running
  readyReplicas: 1
  currentVersion: "7.4"
  targetVersion: "7.4"
  
  roleInfo:
    currentRole: master
    lastRoleChange: "2025-01-19T10:30:00Z"
  
  upgradeStatus:
    phase: Completed
    fromVersion: "7.4"
    toVersion: "7.4"
    updatedReplicas: 1
    totalReplicas: 1
```

### 3.2 Slave Group 配置示例（无高可用）

```yaml
apiVersion: middleware.io/v1alpha1
kind: Group
metadata:
  name: slave-group
  namespace: default
  labels:
    middleware.io/app: production-redis
    middleware.io/component: redis-nodes
    middleware.io/plugin: redis
    middleware.io/plugin-version: "2.0.0"
spec:
  componentRef:
    name: redis-nodes
    namespace: default
  pluginRef:
    name: redis-plugin-v2.0
    namespace: middleware-system
  replicas: 3
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "1"
      memory: "2Gi"
  
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 1
    partition: 0
  
  values:
    redisConfig:
      maxmemory: "1gb"
      readonly: "yes"
  
  # Slave 不需要故障转移
  highAvailability:
    enabled: false

status:
  phase: Running
  readyReplicas: 3
  currentVersion: "7.4"
  targetVersion: "7.4"
```

## 4. 文档导航

- 上一章：[Component CRD 规范](./03-crd-component.md)
- 下一章：[插件系统](./05-plugin-system.md)
- 相关文档：[高可用设计](./07-high-availability.md)、[滚动升级](./10-rolling-upgrade.md)
