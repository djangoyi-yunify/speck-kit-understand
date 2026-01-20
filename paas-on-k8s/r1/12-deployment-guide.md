---
date: 2025-01-19
topic: "部署指南"
version: 1.0.0
status: draft
---

# 部署指南

## 1. 概述

本文档描述中间件 Operator 平台的部署步骤和配置要求。

## 2. 前置要求

### 2.1 Kubernetes 版本

| 要求 | 值 |
|-----|-----|
| 最低版本 | 1.20 |
| 推荐版本 | 1.26+ |

### 2.2 资源要求

| 组件 | CPU | 内存 |
|-----|-----|------|
| Controller Manager | 500m | 512Mi |
| Webhook | 200m | 256Mi |
| Plugin Watcher | 200m | 256Mi |

### 2.3 RBAC 权限

Controller 需要以下 RBAC 权限：

```yaml
# 核心资源
- apiGroups: [""]
  resources: ["configmaps", "services", "pods", "persistentvolumeclaims"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# 自定义资源
- apiGroups: ["middleware.io"]
  resources: ["apps", "components", "groups"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# 其他
- apiGroups: ["monitoring.coreos.com"]
  resources: ["servicemonitors"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

## 3. 部署步骤

### 3.1 创建命名空间

```bash
kubectl create namespace middleware-system
```

### 3.2 安装 CRD

```bash
kubectl apply -f https://raw.githubusercontent.com/middleware-operator/crds/v1.0.0/crds.yaml
```

### 3.3 部署 Controller

#### 使用 Helm（推荐）

```bash
helm repo add middleware-operator https://charts.middleware.io
helm install middleware-operator middleware-operator/middleware-operator \
  --namespace middleware-system \
  --version 1.0.0
```

#### 使用 YAML 文件

```bash
kubectl apply -f https://raw.githubusercontent.com/middleware-operator/operator/v1.0.0/deploy.yaml
```

### 3.4 验证安装

```bash
# 检查 Controller 运行状态
kubectl get deployment -n middleware-system
kubectl get pods -n middleware-system

# 检查 CRD
kubectl get crd | grep middleware.io
```

## 4. 配置

### 4.1 配置项说明

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| `replicas` | 1 | Controller 副本数 |
| `image.repository` | middleware/operator | 镜像仓库 |
| `image.tag` | latest | 镜像标签 |
| `resources.limits.cpu` | 500m | CPU 限制 |
| `resources.limits.memory` | 512Mi | 内存限制 |
| `watchNamespace` | "" | 监控的命名空间（空表示所有） |

### 4.2 自定义配置（Helm）

```yaml
# values.yaml
replicas: 3
image:
  repository: my-registry/middleware-operator
  tag: v1.0.0
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi
watchNamespace: "default,production"
```

### 4.3 高可用部署

```bash
helm install middleware-operator middleware-operator/middleware-operator \
  --namespace middleware-system \
  --set replicas=3 \
  --set podDisruptionBudget.enabled=true \
  --set affinity.nodeAffinity Required \
    --set affinity.podAntiAffinity Preferred \
    --set "affinity.podAntiAffinity.topologyKey=kubernetes.io/hostname"
```

## 5. 插件部署

### 5.1 部署 Redis 插件

```bash
kubectl apply -f https://raw.githubusercontent.com/middleware-operator/plugins/redis/v2.0.0/plugin.yaml
```

### 5.2 部署 Kafka 插件

```bash
kubectl apply -f https://raw.githubusercontent.com/middleware-operator/plugins/kafka/v1.0.0/plugin.yaml
```

### 5.3 验证插件

```bash
# 查看已安装的插件
kubectl get configmap -n middleware-system -l middleware.io/plugin!=

# 查看特定插件
kubectl get configmap -n middleware-system -l middleware.io/plugin=redis
```

## 6. 监控配置

### 6.1 安装 Prometheus Operator

```bash
helm install prometheus-operator stable/prometheus-operator \
  --namespace monitoring \
  --create-namespace
```

### 6.2 创建 ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: middleware-operator
  namespace: monitoring
spec:
  namespaceSelector:
    matchNames:
      - middleware-system
  selector:
    matchLabels:
      app: middleware-operator
  endpoints:
    - port: http
      path: /metrics
```

## 7. 升级

### 7.1 升级 Operator

```bash
helm upgrade middleware-operator middleware-operator/middleware-operator \
  --namespace middleware-system \
  --version 1.1.0
```

### 7.2 升级插件

```bash
kubectl apply -f https://raw.githubusercontent.com/middleware-operator/plugins/redis/v2.1.0/plugin.yaml
```

## 8. 卸载

### 8.1 卸载 Operator

```bash
helm uninstall middleware-operator -n middleware-system
```

### 8.2 卸载 CRD

```bash
kubectl delete crd apps.middleware.io \
  components.middleware.io \
  groups.middleware.io
```

### 8.3 清理命名空间

```bash
kubectl delete namespace middleware-system
```

## 9. 故障排查

### 9.1 Controller 未启动

```bash
# 查看 Pod 日志
kubectl logs -n middleware-system deployment/middleware-operator-manager

# 查看事件
kubectl get events -n middleware-system --sort-by='.lastTimestamp'
```

### 9.2 CRD 安装失败

```bash
# 检查 API 冲突
kubectl get crd

# 查看详细错误
kubectl apply -f crds.yaml --validate=true -v=9
```

### 9.3 Webhook 失败

```bash
# 检查 Webhook 配置
kubectl get validatingwebhookconfiguration
kubectl get mutatingwebhookconfiguration

# 检查证书
kubectl get secret -n middleware-system | grep webhook
```

## 10. 文档导航

- 上一章：[数据流](./11-data-flow.md)
- 下一章：[故障排查](./13-troubleshooting.md)
- 相关文档：[架构概览](./01-architecture-overview.md)
