---
date: 2025-01-19
topic: "故障排查"
version: 1.0.0
status: draft
---

# 故障排查

## 1. 概述

本文档收集常见问题和故障排查方法，帮助用户诊断和解决问题。

## 2. 常见问题

### 2.1 Pod 无法启动

**症状**：Pod 一直处于 Pending 或 CrashLoopBackOff 状态

**排查步骤**：

```bash
# 1. 查看 Pod 状态
kubectl get pod <pod-name> -o wide

# 2. 查看 Pod 事件
kubectl describe pod <pod-name>

# 3. 查看 Pod 日志
kubectl logs <pod-name> -c agent1
kubectl logs <pod-name> -c agent2
```

**常见原因**：

| 原因 | 解决方案 |
|-----|---------|
| 资源不足 | 增加节点或减少资源请求 |
| 镜像拉取失败 | 检查镜像仓库和凭证 |
| PVC 绑定失败 | 检查存储类是否可用 |
| 节点选择器不匹配 | 检查节点标签和选择器 |

### 2.2 中间件无法连接

**症状**：应用无法连接到中间件

**排查步骤**：

```bash
# 1. 检查 Service
kubectl get svc <service-name>

# 2. 检查 Endpoint
kubectl get endpoints <service-name>

# 3. 测试连接
kubectl exec -it <pod-name> -- redis-cli -h <service-name> ping
```

### 2.3 Agent gRPC 调用失败

**症状**：Controller 无法调用 Agent gRPC

**排查步骤**：

```bash
# 1. 检查 Agent 端口
kubectl exec <pod-name> -c agent1 -- netstat -tlnp | grep 50051
kubectl exec <pod-name> -c agent2 -- netstat -tlnp | grep 50052

# 2. 测试 gRPC 连接
kubectl exec <pod-name> -c agent2 -- grpc_health_probe -addr=localhost:50052

# 3. 查看 Agent 日志
kubectl logs <pod-name> -c agent1
kubectl logs <pod-name> -c agent2
```

### 2.4 故障转移失败

**症状**：故障转移命令执行失败

**排查步骤**：

```bash
# 1. 检查故障转移脚本
kubectl exec <pod-name> -c agent2 -- cat /scripts/failover.sh

# 2. 手动执行故障转移脚本
kubectl exec <pod-name> -c agent2 -- /scripts/failover.sh --timeout 30s

# 3. 查看相关日志
kubectl logs <pod-name> -c agent2 | grep -i failover
```

## 3. 诊断命令

### 3.1 资源状态检查

```bash
# 检查所有 App
kubectl get app -A

# 检查 App 详情
kubectl describe app <app-name>

# 检查所有 Component
kubectl get component -A

# 检查所有 Group
kubectl get group -A

# 检查 Group 详情
kubectl describe group <group-name>
```

### 3.2 日志收集

```bash
# 收集 Controller 日志
kubectl logs -n middleware-system -l app=middleware-operator --tail=1000 > controller.log

# 收集特定 Pod 日志
kubectl logs <pod-name> --tail=1000 > pod.log

# 收集所有 Pod 日志（命名空间）
kubectl logs -n <namespace> --all-containers=true --tail=1000 > all-pods.log
```

### 3.3 事件检查

```bash
# 查看命名空间事件
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# 查看资源相关事件
kubectl get events --field-selector involvedObject.name=<resource-name>

# 查看警告事件
kubectl get events --field-selector type=Warning
```

## 4. 调试模式

### 4.1 启用 Controller 调试日志

```bash
# 使用 Helm
helm upgrade middleware-operator middleware-operator/middleware-operator \
  --namespace middleware-system \
  --set logLevel=debug

# 或修改部署
kubectl set env deployment/middleware-operator-manager -n middleware-system LOG_LEVEL=debug
```

### 4.2 启用 Agent 调试日志

```yaml
# 在 Group values 中配置
values:
  agentConfig:
    logLevel: debug
    grpcLogLevel: verbose
```

## 5. 性能问题

### 5.1 响应慢排查

```bash
# 检查 Controller 资源使用
kubectl top pods -n middleware-system

# 检查 Group 资源使用
kubectl top pods -n <namespace>

# 查看资源限制
kubectl describe pod <pod-name> | grep -A 5 "Limits"
```

### 5.2 gRPC 调用延迟高

```bash
# 检查网络延迟
kubectl exec <pod-name> -c agent2 -- curl -v localhost:50052/health

# 检查 Agent 负载
kubectl exec <pod-name> -c agent2 -- ps aux | grep agent
```

## 6. 备份恢复问题

### 6.1 备份失败

```bash
# 检查备份 Job
kubectl get job -n <namespace>

# 查看备份日志
kubectl logs -n <namespace> <backup-job-pod>

# 检查存储凭证
kubectl get secret backup-credentials -n middleware-system
```

### 6.2 恢复失败

```bash
# 检查恢复 Job
kubectl logs -n <namespace> <restore-job-pod>

# 验证备份文件
kubectl exec -n <namespace> <restore-job-pod> -- ls -la /backup/

# 检查密钥
kubectl get secret backup-encryption-key -n middleware-system -o yaml
```

## 7. 监控问题

### 7.1 指标不更新

```bash
# 检查 ServiceMonitor
kubectl get servicemonitor <app-name> -n monitoring

# 检查 Endpoint
kubectl get endpoints <app-name> -n <namespace>

# 测试指标端点
kubectl exec -it <pod-name> -c agent1 -- curl localhost:9090/metrics
```

### 7.2 告警未触发

```bash
# 检查 PrometheusRule
kubectl get prometheusrule -n monitoring

# 检查告警规则
kubectl describe prometheusrule <rule-name> -n monitoring

# 手动查询指标
kubectl exec -n monitoring <prometheus-pod> -- \
  promql -- query='redis_up'
```

## 8. 常见错误码

| 错误码 | 说明 | 解决方案 |
|-------|-----|---------|
| `ERR_APP_NOT_FOUND` | App 资源不存在 | 检查 App 名称和命名空间 |
| `ERR_PLUGIN_NOT_FOUND` | Plugin 不存在 | 安装对应的 Plugin |
| `ERR_IMAGE_NOT_FOUND` | 镜像不存在 | 检查镜像配置和仓库 |
| `ERR_STORAGE_CLASS` | 存储类不存在 | 配置有效的存储类 |
| `ERR_INSUFFICIENT_RESOURCES` | 资源不足 | 增加节点或减少请求 |
| `ERR_GPRC_TIMEOUT` | gRPC 超时 | 检查网络和 Agent 状态 |

## 9. 联系支持

如果以上方法无法解决问题，请收集以下信息并联系支持团队：

```bash
# 收集诊断信息
kubectl cluster-info dump > cluster-info.txt
kubectl get all -A > all-resources.txt
kubectl get events -A --sort-by='.lastTimestamp' > events.txt

# 打包日志
tar -czf diagnostic.tar.gz *.txt *.log
```

## 10. 文档导航

- 上一章：[部署指南](./12-deployment-guide.md)
- 相关文档：[监控设计](./08-monitoring.md)、[备份恢复](./09-backup-restore.md)
