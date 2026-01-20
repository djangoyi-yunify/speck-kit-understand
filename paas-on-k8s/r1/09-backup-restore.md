---
date: 2025-01-19
topic: "备份恢复"
version: 1.0.0
status: draft
---

# 备份恢复

## 1. 概述

平台提供统一的备份恢复框架，支持多种存储后端和加密策略。

## 2. 备份流程

```
用户提交 Backup CR
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  准备工作                                                │
│  ├── 执行热备份命令（如 redis-cli BGSAVE）              │
│  └── (可选) 冻结写入                                    │
└────────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  启动备份 Pod                                            │
│  ├── 使用相同 PVC，只读挂载                              │
│  └── 挂载对象存储凭证                                    │
└────────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  执行备份                                                │
│  ├── 打包数据（tar.gz）                                  │
│  ├── 生成校验和（SHA256）                                │
│  ├── 加密（可选，用户配置）                              │
│  └── 上传到对象存储                                      │
└────────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  清理工作                                                │
│  ├── 恢复中间件状态                                      │
│  └── 删除临时 Pod                                        │
└─────────────────────────────────────────────────────────┘
```

## 3. 恢复流程

```
用户提交 Restore CR
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  下载备份                                                │
│  ├── 从对象存储下载备份文件                              │
│  └── 验证校验和                                          │
└────────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  解密（如已加密）                                        │
│  └── 使用密钥解密                                        │
└────────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  恢复数据                                                │
│  ├── 清空目标数据目录                                    │
│  ├── 解压备份文件                                        │
│  └── 修复权限                                            │
└────────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│  验证和启动                                              │
│  └── 验证数据完整性，启动中间件                          │
```

## 4. 备份配置

### 4.1 完整配置示例

```yaml
backup:
  enabled: true                                    # 是否启用备份
  storage:
    provider: s3                                   # 存储提供商
    bucket: middleware-backups                     # 存储桶名称
    region: us-east-1                              # 区域
    endpoint: https://s3.amazonaws.com             # 端点（可选）
    secretRef:
      name: backup-credentials                     # 密钥名称
      namespace: middleware-system                 # 密钥命名空间
  settings:
    volumeAccess:
      method: shared-pvc                           # 访问方法
      readOnly: true                               # 是否只读挂载
    consistency:
      enabled: true                                # 是否启用一致性检查
      command: redis-cli BGSAVE                    # 一致性检查命令
      waitForCompletion: true                      # 是否等待命令完成
      timeout: 30s                                 # 超时时间
    archive:
      format: tar.gz                               # 归档格式
      compressionLevel: 6                          # 压缩级别（1-9）
    checksum:
      algorithm: sha256                            # 校验和算法
    encryption:
      enabled: true                                # 是否启用加密
      algorithm: aes256-gcm                        # 加密算法
      keySecretRef:
        name: backup-encryption-key                # 密钥名称
        namespace: middleware-system               # 密钥命名空间
        keyField: key                              # 密钥字段
      keyRotation:
        enabled: true                              # 是否启用密钥轮换
        interval: 90d                              # 轮换间隔
        keepOldKeys: true                          # 是否保留旧密钥
        oldKeysRetention: 7d                       # 旧密钥保留时间
  retention:
    remoteRetention: 30d                           # 远程保留时间
    keepCount: 7                                   # 保留备份数量
  schedule:
    enabled: false                                 # 是否启用计划备份
    cron: "0 2 * * *"                              # Cron 表达式
```

### 4.2 存储提供商配置

| 后端 | provider | 配置项 |
|-----|---------|-------|
| **S3** | s3 | bucket, region, [endpoint] |
| **GCS** | gcs | bucket, project |
| **Azure** | azure | container, account |
| **MinIO** | minio | bucket, endpoint |

```yaml
# S3 配置
storage:
  provider: s3
  bucket: middleware-backups
  region: us-east-1
  secretRef:
    name: aws-credentials
    namespace: middleware-system

# GCS 配置
storage:
  provider: gcs
  bucket: middleware-backups
  project: my-project
  secretRef:
    name: gcp-credentials
    namespace: middleware-system

# Azure 配置
storage:
  provider: azure
  container: middleware-backups
  account: myaccount
  secretRef:
    name: azure-credentials
    namespace: middleware-system

# MinIO 配置
storage:
  provider: minio
  bucket: middleware-backups
  endpoint: https://minio.example.com
  secretRef:
    name: minio-credentials
    namespace: middleware-system
```

## 5. 加密策略

### 5.1 支持的加密算法

| 算法 | 说明 | 密钥长度 |
|-----|-----|---------|
| `aes256-gcm` | AES-256-GCM（推荐） | 32 字节 |
| `aes256-cbc` | AES-256-CBC | 32 字节 |
| `gpg` | GPG 对称加密 | 32 字节 |

### 5.2 加密配置

```yaml
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
```

### 5.3 自动生成密钥

```yaml
encryption:
  enabled: true
  algorithm: aes256-gcm
  autoGenerated:
    enabled: true
    secretRef:
      name: auto-backup-key
      namespace: middleware-system
```

## 6. 备份保留策略

### 6.1 保留配置

```yaml
retention:
  remoteRetention: 30d           # 远程存储保留时间
  keepCount: 7                   # 保留的备份数量
```

### 6.2 保留策略逻辑

```
保留策略检查逻辑：
├── 如果保留数量 < keepCount
│   └── 保留所有备份
└── 如果保留数量 >= keepCount
    ├── 保留最近 keepCount 个备份
    └── 删除超出时间 remoteRetention 的旧备份
```

## 7. 备份命令模板

### 7.1 Redis 备份示例

```yaml
backup:
  commands:
    backup: |
      # 执行热备份
      redis-cli BGSAVE
      
      # 等待备份完成
      while [ $(redis-cli LASTSAVE) -eq $(redis-cli LASTSAVE) ]; do
        sleep 1
      done
      
      # 打包数据
      tar -czf /backup/backup.tar.gz -C {{ .Values.dataPath }} .
      
      # 生成校验和
      sha256sum /backup/backup.tar.gz > /backup/backup.tar.gz.sha256
    
    restore: |
      # 停止中间件
      redis-cli SHUTDOWN NOSAVE || true
      
      # 清空数据目录
      rm -rf {{ .Values.dataPath }}/*
      
      # 解压备份
      tar -xzf /backup/backup.tar.gz -C {{ .Values.dataPath }}
      
      # 修复权限
      chown -R redis:redis {{ .Values.dataPath }}
      
      # 启动中间件
      redis-server /etc/redis/redis.conf
```

## 8. 文档导航

- 上一章：[监控设计](./08-monitoring.md)
- 下一章：[滚动升级](./10-rolling-upgrade.md)
- 相关文档：[插件系统](./05-plugin-system.md)
