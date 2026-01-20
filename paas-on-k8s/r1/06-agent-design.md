---
date: 2025-01-19
topic: "Agent 设计"
version: 1.1.0
status: draft
---

# Agent 设计

## 1. 概述

Agent 是运行在每个 Pod 中的关键组件，使用2个agent，分别负责进程管理和工具调用。

## 2. 双 Agent 架构

| Agent | 容器 | 职责 | gRPC 端口 | 主要接口 |
|-------|-----|-----|----------|---------|
| **Agent 1** | 主容器 | 进程管理 | 50051 | Start/Stop/Restart/Signal/GetStatus |
| **Agent 2** | 辅助容器 | 工具调用 | 50052 | Failover/GetRole/ReloadConfig/ExecuteCommand |

### 2.1 Agent 1 + 中间件容器（主容器）

```
┌─────────────────────────────────────────────────┐
│  容器 1: Agent 1 + 中间件 (主容器)               │
│                                                  │
│  PID 1: Agent 1                                 │
│  ├── 管理中间件进程生命周期                      │
│  └── 信号转发                                   │
│                                                  │
│  PID N: 中间件进程 (redis-server, kafka-server) │
│                                                  │
│  端口: 6379 (业务), 端口: 50051 (gRPC)          │
└─────────────────────────────────────────────────┘
```

### 2.2 Agent 2 容器（辅助容器）

```
┌─────────────────────────────────────────────────┐
│  容器 2: Agent 2 (辅助容器，关键组件)            │
│                                                  │
│  Agent 2 (工具调用，端口 50052)                  │
│  ├── Stop()        - 优雅停止（供 Pod 删除使用）│
│  ├── Failover()    - 故障转移                  │
│  ├── GetRole()     - 角色检测                  │
│  ├── ReloadConfig()- 配置热更新                │
│  └── ExecuteCommand- 执行命令                  │
│                                                  │
│  依赖: 容器 1 的进程状态                         │
└─────────────────────────────────────────────────┘
```

### 2.3 Agent 2 Stop 接口说明

Stop 接口是专门为 Pod 删除流程设计的，用于优雅停止中间件进程：

| 场景 | 使用者 | 职责划分 |
|-----|-------|---------|
| **Pod 删除** | Group Controller 调用 | Agent 2 负责优雅停止中间件 |
| **故障转移** | Group Controller 调用 | 中间件自行处理（Redis Sentinel、Kafka ISR 等） |
| **进程重启** | Group Controller 调用 Agent 1 | 进程级别的重启（由 Agent 1 管理） |

**关键设计点：**
- Group Controller 在删除 Pod 前调用 Agent 2 Stop
- 中间件进程收到停止信号后执行优雅关闭
- 如果是 Master/Leader 节点，由中间件自行处理故障转移（如 Redis Sentinel 自动选举新 master）
- Agent 2 只负责停止当前节点的进程，不处理故障转移逻辑

### 2.3 共享卷

```
共享卷:
├── /scripts (工具脚本)          # 故障转移脚本、检测脚本
└── /middleware (中间件数据/套接字) # 数据目录、套接字文件
```

## 3. gRPC 服务定义

### 3.1 Agent 1: 进程管理服务

```protobuf
service ProcessManager {
    rpc Start(StartRequest) returns (StartResponse);
    rpc Stop(StopRequest) returns (StopResponse);
    rpc Restart(RestartRequest) returns (RestartResponse);
    rpc Signal(SignalRequest) returns (SignalResponse);
    rpc GetStatus(GetStatusRequest) returns (GetStatusResponse);
    rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}
```

### 3.2 Agent 2: 工具调用服务

```protobuf
service ToolInvoker {
    // Pod 删除时调用：优雅停止中间件进程
    rpc Stop(StopRequest) returns (StopResponse);

    // 故障转移：触发中间件故障转移机制（由中间件自行处理）
    rpc Failover(FailoverRequest) returns (FailoverResponse);

    // 角色检测：获取当前节点角色
    rpc GetRole(GetRoleRequest) returns (GetRoleResponse);

    // 配置热更新：重载配置
    rpc ReloadConfig(ReloadConfigRequest) returns (ReloadConfigResponse);

    // 健康检查：检查 Agent 2 和中间件状态
    rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);

    // 执行命令：执行自定义命令
    rpc ExecuteCommand(ExecuteCommandRequest) returns (ExecuteCommandResponse);

    // ============================================================
    // 控制器顺序获取接口（供 Component/Group Controller 调用）
    // ============================================================

    // 获取 Group 的执行顺序
    // 调用者：Component Controller
    rpc GetGroupOrder(GetGroupOrderRequest) returns (GetGroupOrderResponse);

    // 获取 Pod 的处理顺序
    // 调用者：Group Controller
    rpc GetPodOrder(GetPodOrderRequest) returns (GetPodOrderResponse);
}
```

### 3.3 请求/响应消息

```protobuf
// ============================================================
// 控制器顺序获取接口
// ============================================================

// 获取 Group 执行顺序
message GetGroupOrderRequest {
    string component_name = 1;        // Component 名称
    string scenario = 2;              // 场景（provision/stop/update/upgrade）
    repeated string groups = 3;       // 当前 Component 下的 Group 列表
}

message GetGroupOrderResponse {
    repeated string order = 1;        // Group 执行顺序
    bool concurrent = 2;              // 是否并发执行（true 表示不定义顺序）
}

// 获取 Pod 处理顺序
message GetPodOrderRequest {
    string group_name = 1;            // Group 名称
    string scenario = 2;              // 场景（provision/stop/update/upgrade）
    repeated string pods = 3;         // 当前 Group 下的 Pod 列表
}

message GetPodOrderResponse {
    repeated string order = 1;        // Pod 处理顺序
    bool concurrent = 2;              // 是否并发执行（true 表示不定义顺序）
}
```

### 3.3 基础请求/响应消息

```protobuf
// ============================================================
// Agent 1: 进程管理服务
// ============================================================
message StartRequest {
    map<string, string> env = 1;  // 环境变量
}

message StartResponse {
    bool success = 1;
    string error = 2;
    int32 pid = 3;                // 进程 ID
}

message StopRequest {
    int32 timeout = 1;  // 超时时间（秒）
    bool force = 2;     // 是否强制停止（跳过优雅关闭）
}

message StopResponse {
    bool success = 1;   // 是否成功停止
    string error = 2;   // 错误信息
    int32 exitCode = 3; // 退出码
}

message RestartRequest {
    int32 timeout = 1;       // 超时时间（秒）
    bool force = 2;          // 是否强制重启
}

message RestartResponse {
    bool success = 1;
    string error = 2;
}

message SignalRequest {
    int32 signal = 1;  // 信号编号（如 SIGTERM=15, SIGKILL=9）
}

message SignalResponse {
    bool success = 1;
    string error = 2;
}

message GetStatusRequest {}

message GetStatusResponse {
    bool running = 1;           // 是否运行中
    int32 pid = 2;              // 进程 ID
    int64 uptime = 3;           // 运行时间（秒）
    map[string]string metrics = 4;  // 进程指标
}

message HealthCheckRequest {}

message HealthCheckResponse {
    bool healthy = 1;
    string message = 2;
}

// ============================================================
// Agent 2: 工具调用服务
// ============================================================

// Stop 接口：Pod 删除时优雅停止中间件进程
message StopRequest {
    int32 timeout = 1;          // 超时时间（秒）
    bool force = 2;             // 是否强制停止（跳过优雅关闭）
    string reason = 3;          // 停止原因（如 "pod-delete"）
}

message StopResponse {
    bool success = 1;           // 是否成功停止
    string error = 2;           // 错误信息
    int32 exitCode = 3;         // 退出码
    string message = 4;         // 详细信息
    bool failoverTriggered = 5; // 是否触发了故障转移（中间件自行处理）
}

message GetStatusRequest {}

message GetStatusResponse {
    bool running = 1;
    int32 pid = 2;
    int64 uptime = 3;      // 运行时间（秒）
    map[string]string metrics = 4;  // 进程指标
}

// 工具调用
message FailoverRequest {
    int32 timeout = 1;
}

message FailoverResponse {
    bool success = 1;
    string error = 2;
    string previousRole = 3;
    string currentRole = 4;
}

message GetRoleRequest {}

message GetRoleResponse {
    string role = 1;       // master, slave, leader, follower
    bool isLeader = 2;
    map[string]string extraInfo = 3;
}

message ReloadConfigRequest {
    string configType = 1;  // 配置类型
    string configPath = 2;  // 配置路径
}

message ReloadConfigResponse {
    bool success = 1;
    string error = 2;
    bool requiresRestart = 3;  // 是否需要重启
}

// ============================================================
// 控制器顺序获取接口
// ============================================================

// 获取 Group 执行顺序
message GetGroupOrderRequest {
    string component_name = 1;        // Component 名称
    string scenario = 2;              // 场景（provision/stop/update/upgrade）
    repeated string groups = 3;       // 当前 Component 下的 Group 列表
}

message GetGroupOrderResponse {
    repeated string order = 1;        // Group 执行顺序
    bool concurrent = 2;              // 是否并发执行（true 表示不定义顺序）
}

// 获取 Pod 处理顺序
message GetPodOrderRequest {
    string group_name = 1;            // Group 名称
    string scenario = 2;              // 场景（provision/stop/update/upgrade）
    repeated string pods = 3;         // 当前 Group 下的 Pod 列表
}

message GetPodOrderResponse {
    repeated string order = 1;        // Pod 处理顺序
    bool concurrent = 2;              // 是否并发执行（true 表示不定义顺序）
}
```

## 4. 故障转移脚本示例

```bash
#!/bin/bash
# /scripts/failover.sh
# Redis 故障转移脚本

set -e

TIMEOUT="30"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

echo "Starting failover (timeout: ${TIMEOUT}s)..."

# 执行 Redis 故障转移
redis-cli FAILOVER --timeout $TIMEOUT

# 等待角色切换完成
wait_for_role() {
    local expected_role="$1"
    local timeout="$2"
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        local role=$(redis-cli role | head -1)
        if [ "$role" = "$expected_role" ]; then
            echo "Role changed to $expected_role"
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    echo "Timeout waiting for role change"
    return 1
}

wait_for_role "master" $TIMEOUT

echo "Failover completed successfully"
```

## 5. Agent 启动参数

### 5.1 Agent 1 启动参数

```bash
/usr/local/bin/agent1 \
  --middleware-type=redis \
  --middleware-bin=redis-server \
  --grpc-port=50051 \
  --health-check-type=exec \
  --health-check-cmd="redis-cli ping" \
  --graceful-timeout=30s
```

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `--middleware-type` | 中间件类型 | 必需 |
| `--middleware-bin` | 中间件可执行文件路径 | 必需 |
| `--grpc-port` | gRPC 服务端口 | 50051 |
| `--health-check-type` | 健康检查类型 | exec |
| `--health-check-cmd` | 健康检查命令 | - |
| `--graceful-timeout` | 优雅关闭超时时间 | 30s |

### 5.2 Agent 2 环境变量

```yaml
env:
  - name: TOOL_INVOKER_PORT
    value: "50052"
  - name: AGENT1_ADDRESS
    value: "localhost:50051"
  - name: FAILOVER_SCRIPT
    value: /scripts/failover.sh
  - name: ROLE_DETECTION_CMD
    value: "redis-cli role"
```

## 6. 版本历史

| 版本 | 日期 | 修改内容 |
|-----|------|---------|
| 1.1.0 | 2025-01-19 | 新增 GetGroupOrder 和 GetPodOrder 接口，供控制器获取执行顺序 |
| 1.0.0 | 2025-01-19 | 初始版本 |

## 7. 文档导航

- 上一章：[插件系统](./05-plugin-system.md)
- 下一章：[高可用设计](./07-high-availability.md)
- 相关文档：[滚动升级](./10-rolling-upgrade.md)、[数据流](./11-data-flow.md)
