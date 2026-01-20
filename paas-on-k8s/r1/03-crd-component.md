---
date: 2025-01-19
topic: "CRD 规范 - Component"
version: 1.0.0
status: draft
---

# CRD 规范 - Component

## 1. 概述

Component 是运行时分组的中间资源，同一个 Component 下的 Group 运行相同的中间件进程。Component 由 App Controller 自动创建，用户通常不需要直接操作。

## 2. Component CRD 完整规范

### 2.1 Schema

```yaml
apiVersion: middleware.io/v1alpha1
kind: Component
metadata:
  name: string                          # Component 名称
  namespace: string                     # 命名空间
  labels:
    middleware.io/app: string           # 引用的 App 名称
    middleware.io/runtime: string       # 运行时类型
spec:
  # App 引用（必需）
  appRef:
    name: string                        # 关联的 App 名称
    namespace: string                   # App 所在命名空间
  
  # 运行时配置（必需）
  runtime:
    name: string                        # 运行时名称
    version: string                     # 运行时版本
  
  # Group 列表（必需）
  groups:
    - name: string                      # Group 名称
      replicas: integer                 # 副本数
      resources:
        requests:
          cpu: string                   # CPU 请求
          memory: string               # 内存请求
        limits:
          cpu: string                   # CPU 限制
          memory: string               # 内存限制
status:
  phase: string                         # 状态（Pending, Running, Failed）
  readyReplicas: integer               # 就绪副本数
  replicas: integer                    # 总副本数
```

## 3. 配置示例

### 3.1 Redis Component 配置示例

```yaml
apiVersion: middleware.io/v1alpha1
kind: Component
metadata:
  name: redis-nodes
  namespace: default
  labels:
    middleware.io/app: production-redis
    middleware.io/runtime: redis
spec:
  appRef:
    name: production-redis
    namespace: default
  runtime:
    name: redis
    version: "7.4"
  groups:
    - name: master-group
      replicas: 1
      resources:
        requests:
          cpu: "1"
          memory: "2Gi"
        limits:
          cpu: "2"
          memory: "4Gi"
    - name: slave-group
      replicas: 3
      resources:
        requests:
          cpu: "500m"
          memory: "1Gi"
        limits:
          cpu: "1"
          memory: "2Gi"

status:
  phase: Running
  readyReplicas: 4
  replicas: 4
```

### 3.2 Kafka + Zookeeper Component 配置示例

```yaml
apiVersion: middleware.io/v1alpha1
kind: Component
metadata:
  name: kafka-nodes
  namespace: default
  labels:
    middleware.io/app: production-kafka
    middleware.io/runtime: kafka
spec:
  appRef:
    name: production-kafka
    namespace: default
  runtime:
    name: kafka
    version: "3.4"
  groups:
    - name: broker-group
      replicas: 3
      resources:
        requests:
          cpu: "2"
          memory: "8Gi"
        limits:
          cpu: "4"
          memory: "16Gi"

---
apiVersion: middleware.io/v1alpha1
kind: Component
metadata:
  name: zookeeper-nodes
  namespace: default
  labels:
    middleware.io/app: production-kafka
    middleware.io/runtime: zookeeper
spec:
  appRef:
    name: production-kafka
    namespace: default
  runtime:
    name: zookeeper
    version: "3.8"
  groups:
    - name: zookeeper-group
      replicas: 3
      resources:
        requests:
          cpu: "500m"
          memory: "1Gi"
        limits:
          cpu: "1"
          memory: "2Gi"

status:
  phase: Running
  readyReplicas: 3
  replicas: 3
```

## 4. 设计说明

### 4.1 Component 的作用

1. **逻辑分组**：将运行相同中间件进程的 Pod 分组
2. **资源共享**：同一 Component 下的 Group 共享配置
3. **状态聚合**：聚合下属所有 Group 的状态

### 4.2 与 App 和 Group 的关系

```
App (production-redis)
└── Component (redis-nodes)
    ├── Group (master-group) → 1 Pod, 4C8G
    └── Group (slave-group) → 3 Pods, 2C4G
```

## 5. 文档导航

- 上一章：[App CRD 规范](./02-crd-app.md)
- 下一章：[Group CRD 规范](./04-crd-group.md)
- 相关文档：[高可用设计](./07-high-availability.md)、[滚动升级](./10-rolling-upgrade.md)
