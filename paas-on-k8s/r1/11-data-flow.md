---
date: 2025-01-19
topic: "数据流"
version: 1.0.0
status: draft
---

# 数据流

## 1. 概述

本文档描述平台中的数据流，包括配置流、控制流和数据流。

## 2. 创建流程数据流

```
用户提交 App YAML
        │
        ▼
┌─────────────────────┐
│  API Server         │
│  (App CRD)          │
└──────────┐──────────┘
           │
           ▼
┌─────────────────────┐
│  App Controller     │
│  • 验证 App         │
│  • 创建 Component   │
└──────────┐──────────┘
           │
           ▼
┌─────────────────────┐
│  Component Controller
│  • 解析配置         │
│  • 创建 Group       │
└──────────┐──────────┘
           │
           ▼
┌─────────────────────┐
│  Group Controller   │
│  • 获取 Plugin      │
│  • 渲染模板         │
│  • 创建 K8s 资源    │
│  • 管理滚动升级     │
│  • 调用 Agent gRPC  │
└──────────┐──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Kubernetes         │────►│  Pod (双容器)       │
│  • Deployment       │     │  • Agent 1 (50051)  │
│  • Service          │     │  • Agent 2 (50052)  │
│  • ConfigMap        │     │  • Middleware       │
│  • PVC              │     └─────────────────────┘
└─────────────────────┘
```

## 3. 配置变更数据流

### 3.1 ConfigMap 变更触发热更新

```
┌─────────────────────┐     ┌─────────────────────┐
│  ConfigMap 变更     │────►│  Group Controller   │
│  (用户更新配置)     │     │  检测变更           │
└─────────────────────┘     └──────────┬──────────┘
                                       │
                                       ▼
                               ┌─────────────────────┐
                               │  调用 Agent gRPC    │
                               │  ReloadConfig/Restart
                               └─────────────────────┘
```

### 3.2 插件热更新

```
┌─────────────────────────────────────┐
│  Plugin ConfigMap 变更               │
│  • 模板修改                          │
│  • 默认值修改                        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Plugin Watcher 检测变更             │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  标记使用此插件的 Group 需要重新渲染  │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Group Controller 重新渲染模板       │
│  • 重新生成 Deployment              │
│  • 更新 Pod (滚动升级)               │
└─────────────────────────────────────┘
```

## 4. 控制流

### 4.1 Agent gRPC 调用

```
Group Controller                          Agent 2 (Pod)
     │                                        │
     │── gRPC: GetRole() ──────────────────►  │
     │                                        │
     │◄── GetRoleResponse ────────────────────│
     │     role: master                       │
     │                                        │
     │── gRPC: Failover() ──────────────────► │
     │                                        │
     │◄── FailoverResponse ───────────────────│
     │     success: true                      │
     │                                        │
     │── gRPC: ReloadConfig() ──────────────► │
     │     configPath: /etc/redis/redis.conf  │
     │                                        │
     │◄── ReloadConfigResponse ───────────────│
     │     requiresRestart: false             │
```

### 4.2 状态上报流程

```
Agent 1/Pod                          Controller
     │                                   │
     │── Watch events ──────────────────►│
     │   • Pod started                   │
     │   • Pod ready                     │
     │   • Pod stopped                   │
     │                                   │
     │◄── gRPC requests ──────────────────│
         • GetStatus
         • HealthCheck
```

## 5. 数据流详情

### 5.1 备份数据流

```
Backup Pod                          对象存储
     │                                │
     │── 打包数据 ──────────────────► │
     │   tar.gz + sha256 + 加密       │
     │                                │
     │◄── 存储确认 ───────────────────│
```

### 5.2 监控数据流

```
┌─────────────────────────────────────────────────────────────┐
│                      监控指标流向                           │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐     ┌─────────────────┐     ┌────────────┐  │
│   │  Agent      │────►│  Prometheus     │────►│  Alertmanager│ │
│   │  Exporter   │     │  Server         │     │            │  │
│   │  (9090)     │     │                 │     │            │  │
│   └─────────────┘     └────────┬────────┘     └────────────┘  │
│                                │                                │
│                                ▼                                │
│                        ┌─────────────┐                          │
│                        │  Grafana    │                          │
│                        │  Dashboard  │                          │
│                        └─────────────┘                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 6. 资源生命周期

### 6.1 创建顺序

```
App → Component → Group → Deployment/Service/ConfigMap/PVC → Pod
```

### 6.2 删除顺序

```
Pod → Deployment/Service/ConfigMap/PVC → Group → Component → App
```

### 6.3 依赖关系图

```
App
 │
 ├── Component
 │     │
 │     └── Group
 │           │
 │           ├── Deployment ───► Pod
 │           │                        │
 │           ├── Service ◄───────────┘
 │           │
 │           ├── ConfigMap ───► Pod (挂载)
 │           │
 │           └── PVC ──────────► Pod (数据)
 │
 └── (另一个 Component...)
       └── ...
```

## 7. 网络流

### 7.1 Pod 网络

```
外部流量                        Pod 网络
     │                              │
     │                              │
     ▼                              ▼
┌─────────┐                 ┌─────────────────┐
│ Service │ ──────────────► │ Pod             │
│ (VIP)   │                 │ - Agent 1:50051 │
└─────────┘                 │ - Agent 2:50052 │
                            │ - Middleware    │
                            └─────────────────┘
```

### 7.2 Service 类型

| 类型 | 说明 | 适用场景 |
|-----|-----|---------|
| `ClusterIP` | 集群内部访问 | 集群内部访问 |
| `NodePort` | 节点端口暴露 | 开发测试环境 |
| `LoadBalancer` | 云负载均衡器 | 生产环境（公有云） |
| `ExternalName` | 外部服务映射 | 引用外部服务 |

## 8. 待确认问题

| 序号 | 问题 | 说明 |
|-----|-----|-----|
| 1 | **Agent 适配器** | 中间件特定的指标采集和操作逻辑（已设计双 Agent 架构） |
| 2 | **Web UI 设计** | 可视化界面设计（优先级低） |

## 9. 附录

### 9.1 支持的加密算法

| 算法 | 说明 | 密钥长度 |
|-----|-----|---------|
| aes256-gcm | AES-256-GCM（推荐） | 32 字节 |
| aes256-cbc | AES-256-CBC | 32 字节 |
| gpg | GPG 对称加密 | 32 字节 |

### 9.2 支持的存储后端

| 后端 | 配置项 |
|-----|-------|
| S3 | provider: s3, bucket, region |
| GCS | provider: gcs, bucket, project |
| Azure | provider: azure, container, account |
| MinIO | provider: minio, bucket, endpoint |

### 9.3 模板函数

| 函数 | 说明 |
|-----|-----|
| `include "middleware.labels" .` | 生成标准标签 |
| `include "middleware.selectorLabels" .` | 生成选择器标签 |
| `toYaml` | 转换为 YAML |
| `toJson` | 转换为 JSON |
| `default` | 默认值 |

## 10. 文档导航

- 上一章：[滚动升级](./10-rolling-upgrade.md)
- 下一章：[部署指南](./12-deployment-guide.md)
- 相关文档：[插件系统](./05-plugin-system.md)、[Agent 设计](./06-agent-design.md)
