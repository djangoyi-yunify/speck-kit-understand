---
date: 2025-01-19
topic: "全局元数据管理"
version: 2.0.0
status: draft
---

# 全局元数据管理

## 1. 概述

全局元数据（Middleware Metadata）是每个 App 实例的私有数据，存储该中间件实例的节点状态和配置信息。

每个 App 对应一个独立的元数据 ConfigMap，记录该 App 的基本信息、节点状态和中间件配置。

## 2. 存储设计

### 2.1 存储载体

每个 App 对应一个独立的 ConfigMap，与 App 同命名空间。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: production-redis-metadata
  namespace: default
  ownerReferences:
    - apiVersion: middleware.io/v1alpha1
      kind: App
      name: production-redis
      uid: <uid>
  labels:
    middleware.io/app: production-redis
    middleware.io/metadata: "true"
data:
  metadata.yaml: |
    # 元数据内容
```

### 2.2 命名规则

| 规则 | 说明 |
|-----|------|
| 名称 | `<app-name>-metadata` |
| 命名空间 | 与 App 同命名空间 |
| 标签 | `middleware.io/app: <app-name>` |

### 2.3 数据结构

```yaml
# 全局信息
metadata:
  name: production-redis              # App 名称
  namespace: default                  # 命名空间
  plugin: redis                       # 插件名称
  pluginVersion: "2.0.0"              # 插件版本
  runtime:
    name: redis                       # 运行时名称
    version: "7.4"                    # 运行时版本
  version: "2025-01-19T10:30:00Z"     # 元数据版本（乐观锁）
  createdAt: "2025-01-19T08:00:00Z"   # 创建时间
  updatedAt: "2025-01-19T10:30:00Z"   # 更新时间

# 节点状态
nodes:
  normal:                             # 正在运行的节点
    - component: redis-nodes
      group: master-group
      pods:
        - redis-0
        - redis-1
    
    - component: redis-nodes
      group: slave-group
      pods:
        - redis-2
        - redis-3
        - redis-4
  
  adding:                             # 需要加入的节点
    - component: redis-nodes
      group: slave-group
      pods:
        - redis-new-0
  
  deleting:                           # 需要删除的节点
    - component: redis-nodes
      group: slave-group
      pods:
        - redis-old-0

# 中间件配置
appconfig:
  - component: redis-nodes
    groups:
      - name: master-group
        config:
          maxmemory: "3gb"
          appendonly: "yes"
          port: 6379
      
      - name: slave-group
        config:
          maxmemory: "1gb"
          appendonly: "yes"
          replicaof: "redis-0:6379"
  
  - component: redis-sentinel
    groups:
      - name: sentinel-group
        config:
          down-after-milliseconds: 30000
          failover-timeout: 180000
```

### 2.4 metadata 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| name | string | App 名称 |
| namespace | string | 命名空间 |
| plugin | string | 插件名称 |
| pluginVersion | string | 插件版本 |
| runtime.name | string | 运行时名称 |
| runtime.version | string | 运行时版本 |
| version | string | 元数据版本（乐观锁） |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

### 2.5 nodes 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| normal | []NodeGroup | 正在运行的节点 |
| adding | []NodeGroup | 需要加入的节点 |
| deleting | []NodeGroup | 需要删除的节点 |

### 2.6 NodeGroup 结构

```yaml
- component: string    # Component 名称
  group: string        # Group 名称
  pods: []string       # Pod 名称列表
```

### 2.7 appconfig 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| component | string | Component 名称 |
| groups | []GroupConfig | Group 配置列表 |

### 2.8 GroupConfig 结构

```yaml
- name: string              # Group 名称
  config: map[string]any    # 中间件配置参数
```

## 3. 生命周期管理

### 3.1 创建时机

App Controller 创建 App 时，同时创建元数据 ConfigMap。

### 3.2 更新时机

| 触发条件 | 更新内容 |
|---------|---------|
| App 创建时 | 创建元数据 ConfigMap |
| 增加 Pod 时 | 更新 nodes.normal |
| 删除 Pod 时 | 更新 nodes.normal |
| 配置变更时 | 更新 appconfig |
| App 删除时 | 删除元数据 ConfigMap |

### 3.3 删除机制

通过 OwnerReferences 实现级联删除，App 删除时元数据 ConfigMap 自动删除。

### 3.4 写入模式

写入模式为全量覆盖，每次更新写入完整的元数据内容。

## 4. 权限管理

### 4.1 写入权限

| 组件 | 写入权限 |
|-----|:-------:|
| App Controller | ✓ |
| Group Controller | ✗ |
| Component Controller | ✗ |
| Agent | ✗ |

**说明**：Agent 上报状态给 App Controller，由 App Controller 统一更新元数据 ConfigMap。

### 4.2 读取权限

| 组件 | 读取权限 | 用途 |
|-----|:-------:|------|
| App Controller | ✓ | 汇总决策、版本控制 |
| Group Controller | ✓ | 查询节点状态 |
| 监控系统 | ✓ | 抓取健康指标 |
| 用户/CLI | ✓ | 查询中间件状态 |

## 5. App.status 与元数据的关系

| 字段 | 存储位置 | 存储内容 | 维护者 |
|-----|---------|---------|-------|
| App.status | App 资源 | Controller 生成的状态（Created、Reconciling、Ready） | App Controller |
| App.metadata ConfigMap | 独立 ConfigMap | 节点状态、中间件配置 | App Controller |

**说明**：App.status 只保留 Controller 生成的状态，元数据存储在独立 ConfigMap 中。

## 6. 元数据与拓扑关系

Component/Group 结构已反映拓扑关系，元数据无需额外存储拓扑信息。

```
App (production-redis)
└── Component (redis-nodes)
    ├── Group (master-group) → 主节点
    └── Group (slave-group) → 从节点
```

## 7. 与原设计的差异

本文档是对原设计的重大修订，主要差异如下：

| 原设计 | 修订后 |
|-------|-------|
| 全局汇总 ConfigMap（middleware-system 命名空间） | 按 App 隔离的独立 ConfigMap（与 App 同命名空间） |
| 包含健康状态（healthy/degraded/critical） | 不包含 |
| 包含拓扑关系（master-slave/cluster/sentinel） | 不需要（Component/Group 已反映） |
| 包含历史记录 | 不包含 |
| Agent 直接上报心跳（5s 间隔） | Agent 上报给 App Controller，由 Controller 更新 |
| 实时节点状态（online/offline/degraded） | 节点状态由 Controller 根据 K8s API 更新 |
| 节点级别的详细信息（IP、端口、资源） | 简化为 Component/Group/Pod 名称列表 |

## 8. 设计要点总结

| 决策项 | 内容 |
|-------|------|
| **存储载体** | 每个 App 一个独立 ConfigMap |
| **命名规则** | `<app-name>-metadata` |
| **生命周期** | App Controller 管理，OwnerReferences 关联 |
| **写入权限** | 只有 App Controller |
| **写入模式** | 全量覆盖 |
| **读取权限** | App Controller、Group Controller、监控系统、用户 |
| **更新时机** | App 创建/删除、Pod 增加/删除、配置变更 |

## 9. 文档导航

- 上一章：[架构概览](./01-architecture-overview.md)
- 下一章：[控制器设计](./14-controller-design.md)
- 相关文档：[App CRD 规范](./02-crd-app.md)、[Component CRD 规范](./03-crd-component.md)、[Group CRD 规范](./04-crd-group.md)

## 10. 版本历史

| 版本 | 日期 | 修改内容 |
|-----|------|---------|
| 1.0.0 | 2025-01-19 | 初始版本 |
| 2.0.0 | 2025-01-19 | 重大修订：按 App 隔离元数据、移除健康状态和历史记录 |
