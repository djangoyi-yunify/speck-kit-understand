---
date: 2025-01-19
topic: "插件系统"
version: 1.1.0
status: draft
---

# 插件系统

## 1. 概述

插件系统是平台的核心抽象机制，通过 ConfigMap 存储插件定义和模板，实现中间件的通用管理能力。新增中间件只需编写插件，无需修改 Controller 代码。

## 2. 插件发现机制

插件通过 K8s ConfigMap 存储，使用标签进行发现：

```bash
# 查看所有 Redis 插件
kubectl get configmap -l middleware.io/plugin=redis

# 查看所有插件
kubectl get configmap -l middleware.io/plugin!=
```

## 3. Plugin ConfigMap 结构

### 3.1 完整规范

```yaml
apiVersion: middleware.io/v1alpha1
kind: Plugin
metadata:
  name: string                          # Plugin ConfigMap 名称
  labels:
    middleware.io/plugin: string        # 插件类型
    middleware.io/version: string       # 插件版本
spec:
  # 基本信息
  name: string                          # 插件名称
  version: string                       # 插件版本
  description: string                   # 插件描述
  
  # 支持的运行时版本
  runtimes:
    - name: string                      # 运行时名称
      versions: []string               # 支持的版本列表
  
  # 镜像映射
  images:
    [version]: string                  # 版本 -> 镜像映射
  
  # 运行时兼容性
  compatibility:
    migrateFrom:
      [version]: []string              # 可从哪些版本升级
  
  # 能力声明
  capabilities:
    - scaling                         # 支持扩缩容
    - failover                       # 支持故障转移
    - backup                         # 支持备份
    - configReload                   # 支持配置热更新

  # Component 执行顺序定义（控制并发）
  # 数组顺序即执行顺序，不定义表示并发执行
  orders:
    provision: []string               # 部署时的执行顺序
    stop: []string                    # 停止时的执行顺序
    update: []string                  # 更新时的执行顺序
    upgrade: []string                 # 升级时的执行顺序
  
  # 默认配置值
  defaultValues:
    replicas: integer                 # 默认副本数
    resources:                        # 默认资源规格
      requests:
        cpu: string
        memory: string
    network:
      port: integer                   # 默认端口
      type: string                   # Service 类型
    storage:
      enabled: boolean
      size: string
      storageClass: string
    [key]: [value]                   # 其他默认配置
  
  # 模板清单
  templates:
    - name: string                    # 模板名称
      configMapRef: string            # Template ConfigMap 引用
      type: string                   # 资源类型
      optional: boolean              # 是否可选
  
  # 监控配置
  monitoring:
    alerts:
      - name: string                 # 告警名称
        expr: string                 # PromQL 表达式
        for: string                 # 持续时间
        severity: string            # 严重级别
        annotations: map[string]string # 注解
  
  # 高可用配置
  highAvailability:
    passive:
      enabled: boolean
      autoRoleSwitch: boolean
      roleDetection:
        type: string
        command: string
        parsePattern: string
        interval: string
    active:
      enabled: boolean
      failoverCommand:
        type: string
        command: string
        args: []string
  
  # 备份配置
  backup:
    providers: []string              # 支持的存储提供商
    commands:
      backup: string                # 备份命令模板
      restore: string               # 恢复命令模板
    uploadCommands:                 # 上传命令
      [provider]: string           # provider -> 命令映射
status:
  phase: string                       # 状态（Ready, Pending）
  lastUpdateTime: string             # 最后更新时间
```

### 3.2 Redis 插件示例

```yaml
apiVersion: middleware.io/v1alpha1
kind: Plugin
metadata:
  name: redis-plugin-v2.0
  labels:
    middleware.io/plugin: redis
    middleware.io/version: v2.0.0
spec:
  # 基本信息
  name: redis
  version: "2.0.0"
  description: "Redis 中间件插件，支持主从和集群模式"
  
  # 支持的运行时版本
  runtimes:
    - name: redis
      versions:
        - "7.2"
        - "7.4"
        - "8.0"
  
  # 镜像映射
  images:
    "7.2": my-registry/redis:7.2-agent
    "7.4": my-registry/redis:7.4-agent
    "8.0": my-registry/redis:8.0-agent
  
  # 运行时兼容性
  compatibility:
    migrateFrom:
      "7.2":
        - "6.2"
      "7.4":
        - "7.2"
  
  # 能力声明
  capabilities:
    - scaling
    - failover
    - backup
    - configReload

  # Component 执行顺序定义（控制并发）
  # 数组顺序即执行顺序，不定义或空数组表示并发执行
  orders:
    provision: [storage, compute]     # storage 先于 compute 部署
    stop: [compute, storage]          # compute 先于 storage 停止
    update: [storage, compute]        # storage 先更新
    upgrade: [storage, compute]       # 升级时 storage 先准备

  # 默认配置值
  defaultValues:
    replicas: 3
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
    network:
      port: 6379
      type: ClusterIP
    storage:
      enabled: true
      size: "10Gi"
      storageClass: "standard"
    redisConfig:
      maxmemory: "1gb"
      maxmemory-policy: "allkeys-lru"
      appendonly: "yes"
      appendfsync: "everysec"
  
  # 模板清单
  templates:
    - name: deployment
      configMapRef: redis-deployment-tpl
      type: Deployment
    - name: service
      configMapRef: redis-service-tpl
      type: Service
    - name: configmap
      configMapRef: redis-config-tpl
      type: ConfigMap
    - name: pvc
      configMapRef: redis-pvc-tpl
      type: PersistentVolumeClaim
      optional: true
  
  # 监控配置
  monitoring:
    alerts:
      - name: RedisDown
        expr: agent_up == 0
        for: 1m
        severity: critical
        annotations:
          summary: "Redis instance is down"
      - name: RedisHighMemory
        expr: redis_used_memory_bytes / redis_max_memory > 0.85
        for: 5m
        severity: warning
        annotations:
          summary: "Redis high memory usage"
      - name: RedisReplicationLag
        expr: redis_master_link_status == 0
        for: 2m
        severity: critical
      - name: RedisTooManyConnections
        expr: redis_connected_clients > 2000
        for: 5m
        severity: warning
  
  # 高可用配置
  highAvailability:
    passive:
      enabled: true
      autoRoleSwitch: true
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
      postFailoverVerify:
        enabled: true
        type: exec
        command: "redis-cli role"
        expectedRole: "master"
  
  # 备份配置
  backup:
    providers:
      - s3
      - gcs
      - azure
      - minio
    commands:
      backup: |
        tar -czf /backup/backup.tar.gz -C {{ .Values.dataPath }} .
        sha256sum /backup/backup.tar.gz > /backup/backup.tar.gz.sha256
      restore: |
        tar -xzf /backup/backup.tar.gz -C {{ .Values.dataPath }}
    uploadCommands:
      s3: |
        aws s3 cp /backup/backup.tar.gz s3://{{ .Values.bucket }}/{{ .Values.appName }}/{{ .Values.date }}/
      gcs: |
        gsutil cp /backup/backup.tar.gz gs://{{ .Values.bucket }}/{{ .Values.appName }}/{{ .Values.date }}/

status:
  phase: Ready
  lastUpdateTime: "2025-01-19T10:00:00Z"
```

## 4. Template ConfigMap

### 4.1 Deployment 模板示例

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-deployment-tpl
  labels:
    middleware.io/template: deployment
    middleware.io/plugin: redis
data:
  template: |
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: {{ .Values.name }}
      namespace: {{ .Values.namespace }}
      labels:
        {{- include "middleware.labels" . | nindent 4 }}
        app.kubernetes.io/component: {{ .Values.component }}
        middleware.io/group: {{ .Values.group }}
    spec:
      replicas: {{ .Values.replicas }}
      selector:
        matchLabels:
          {{- include "middleware.selectorLabels" . | nindent 6 }}
      template:
        metadata:
          labels:
            {{- include "middleware.labels" . | nindent 8 }}
            app.kubernetes.io/component: {{ .Values.component }}
            middleware.io/group: {{ .Values.group }}
        spec:
          {{- with .Values.affinity }}
          affinity:
            {{- toYaml . | nindent 10 }}
          {{- end }}
          containers:
          - name: agent1
            image: {{ index .Values.images .Values.runtime.version }}
            imagePullPolicy: IfNotPresent
            ports:
            - containerPort: {{ .Values.port }}
              name: redis
            - containerPort: 50051
              name: agent1-grpc
            env:
            - name: MIDDLEWARE_BIN
              value: {{ .Values.middlewareBin }}
            - name: PROCESS_MANAGER_PORT
              value: "50051"
            volumeMounts:
            - name: data
              mountPath: /data
            - name: config
              mountPath: /etc/middleware
              subPath: redis.conf
            command:
              - /bin/sh
              - -c
              - |
                {{- if .Values.redisConfig }}
                {{- range $k, $v := .Values.redisConfig }}
                echo "{{ $k }} {{ $v }}" >> /etc/middleware/redis.conf
                {{- end }}
                {{- end }}
                /usr/local/bin/agent1 \
                  --middleware-type={{ .Values.runtime.name }} \
                  --middleware-bin={{ .Values.middlewareBin }} \
                  --grpc-port=50051 \
                  --health-check-type=exec \
                  --health-check-cmd="redis-cli ping" \
                  --graceful-timeout=30s
          - name: agent2
            image: middleware/agent2:latest
            env:
            - name: TOOL_INVOKER_PORT
              value: "50052"
            - name: AGENT1_ADDRESS
              value: "localhost:50051"
            - name: FAILOVER_SCRIPT
              value: /scripts/failover.sh
            - name: ROLE_DETECTION_CMD
              value: "redis-cli role"
            ports:
            - containerPort: 50052
              name: agent2-grpc
            volumeMounts:
            - name: scripts
              mountPath: /scripts
              readOnly: true
          volumes:
          - name: data
            {{- if .Values.storage.enabled }}
            persistentVolumeClaim:
              claimName: {{ .Values.name }}-data
            {{- else }}
            emptyDir: {}
            {{- end }}
          - name: config
            configMap:
              name: {{ .Values.name }}-config
          - name: scripts
            configMap:
              name: redis-tool-scripts
              defaultMode: 0755
```

## 5. 插件版本管理

### 5.1 热升级机制

```
Plugin Watcher 检测变更
        │
        ▼
┌─────────────────────────────────────┐
│  Plugin ConfigMap 变更               │
│  • 内容修改 (template/values)        │
│  • annotations 记录 hash             │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  找出使用此插件的所有 Group          │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  标记 Group 需要重新渲染             │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Group Controller 重新渲染模板       │
```

### 5.2 版本约束

```
redis-plugin-v1.0 ────── 支持 redis:7.2 ──────►
        │                                    │
        │  插件热升级（模板/逻辑变更）        │  插件热升级
        ▼                                    ▼
redis-plugin-v1.1 ────── 支持 redis:7.2 ──────►
        │                                    │
        │  插件大版本升级（新运行时支持）     │  运行时升级
        ▼                                    ▼
redis-plugin-v2.0 ────── 支持 redis:7.4 ──────►
```

## 6. 版本历史

| 版本 | 日期 | 修改内容 |
|-----|------|---------|
| 1.1.0 | 2025-01-19 | 新增 orders 字段，定义 Component 执行顺序 |
| 1.0.0 | 2025-01-19 | 初始版本 |

## 7. 文档导航

- 上一章：[Group CRD 规范](./04-crd-group.md)
- 下一章：[Agent 设计](./06-agent-design.md)
- 相关文档：[滚动升级](./10-rolling-upgrade.md)、[数据流](./11-data-flow.md)
