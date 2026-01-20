---
date: 2025-01-19
topic: "控制器设计"
version: 2.0.0
status: validated
---

# 控制器设计

## 1. 概述

控制器层是平台的核心引擎，包含三个协作的控制器：App Controller、Component Controller 和 Group Controller。它们通过 Kubernetes 的调和模式（Reconcile Pattern）管理中间件资源的完整生命周期。

本文档描述控制器的核心设计，包括职责划分、调和逻辑、任务编排机制、错误处理等。

## 2. 控制器架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      控制器层架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Server                           │   │
│  └──────────────────────────┬──────────────────────────────┘   │
│                             │                                   │
│              ┌──────────────┼──────────────┐                   │
│              │              │              │                   │
│              ▼              ▼              ▼                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │  App Controller │ │ Component Ctrl  │ │ Group Controller│  │
│  │  (编排中心)      │ │ (组编排)        │ │ (执行层)        │  │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘  │
│           │                   │                   │            │
│           │ 修改 Component    │ 修改 Group        │            │
│           │ Spec              │ Spec              │            │
│           ▼                   ▼                   ▼            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Middleware Metadata (ConfigMap)            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 三层控制器的职责定位

| 控制器 | 职责定位 | 核心能力 |
|-------|---------|---------|
| **App Controller** | 编排中心 | 任务生成、任务调度、依赖管理、并发控制 |
| **Component Controller** | 组编排 | 变更分析、Group 编排、顺序获取、状态汇总 |
| **Group Controller** | 执行层 | 模板渲染、资源操作、Pod 管理、状态上报 |

### 2.2 控制流

```
用户修改 App
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                   App Controller                             │
│                                                              │
│   1. 检测 Spec 变化                                          │
│   2. 生成任务列表（按优先级排序）                             │
│   3. 按顺序触发 Component Spec 更新                          │
│   4. 等待任务完成                                            │
│   5. 处理失败/超时/取消                                      │
│                                                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Component Controller                          │
│                                                              │
│   1. 检测 Component Spec 变化                                │
│   2. 分析变更类型，确定编排策略                               │
│   3. 通过 gRPC 从 Agent2 获取 Group 执行顺序                 │
│   4. 按顺序触发 Group Spec 更新                              │
│   5. 收集状态上报                                            │
│                                                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Group Controller                             │
│                                                              │
│   1. 检测 Group Spec 变化                                    │
│   2. 通过 gRPC 从 Agent2 获取 Pod 处理顺序                   │
│   3. 按顺序执行资源操作                                      │
│   4. 上报状态                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 3. App Controller

### 3.1 核心职责

App Controller 是顶层控制器，作为编排中心负责整体任务的调度和协调。

```
App Controller 职责：
┌─────────────────────────────────────────────────────────────┐
│  1. 任务编排                                                  │
│     ├── 检测 App Spec 变化                                   │
│     ├── 生成变更任务列表                                     │
│     ├── 按优先级排序任务                                     │
│     └── 按依赖关系调度任务                                   │
│                                                              │
│  2. 任务执行                                                  │
│     ├── 修改 Component Spec 触发下游编排                     │
│     ├── 轮询 Component 状态等待任务完成                      │
│     └── 按顺序执行下一个任务                                 │
│                                                              │
│  3. 失败处理                                                  │
│     ├── 检测任务失败                                         │
│     ├── 按策略重试（可配置次数）                             │
│     └── 支持通过 Annotation 手动重试                         │
│                                                              │
│  4. 任务取消                                                  │
│     ├── 支持取消 pending 状态的任务                          │
│     ├── 支持取消 running 状态的任务（如支持）                │
│     └── 取消后停止执行后续任务                               │
│                                                              │
│  5. 超时处理                                                  │
│     ├── 为每个任务设置超时时间                               │
│     ├── 超时后标记失败，停止后续任务                         │
│     └── 支持通过 Annotation 手动重试                         │
│                                                              │
│  6. 并发变更处理                                              │
│     ├── 检测执行中的新 Spec 变更                             │
│     ├── 记录待处理变更，提示用户                             │
│     ├── 等待当前任务完成后处理                               │
│     └── 支持用户取消当前任务立即处理新变更                   │
│                                                              │
│  7. 并发控制                                                  │
│     ├── 从插件获取 orders 定义                               │
│     ├── 按定义顺序或并发执行任务                             │
│     └── 支持多场景（provision/stop/update/upgrade）          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 调和逻辑

```go
func (r *AppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    // 1. 获取 App 资源
    app := &middlewarev1.App{}
    if err := r.Get(ctx, req.NamespacedName, app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 2. 处理用户操作（取消/重试）
    if err := r.processUserActions(app); err != nil {
        return ctrl.Result{}, err
    }

    // 3. 检测 Spec 变化，生成任务
    specChange := r.detectSpecChange(app)
    if specChange != nil {
        if err := r.handleSpecChange(app, specChange); err != nil {
            return ctrl.Result{}, err
        }
    }

    // 4. 执行任务队列
    result, err := r.executeTaskQueue(app)
    if result != nil {
        return *result, err
    }
    if err != nil {
        return ctrl.Result{}, err
    }

    // 5. 更新 App 状态
    r.updateAppStatus(app)

    return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
}
```

### 3.3 任务编排机制

#### 3.3.1 任务类型

| 任务类型 | 说明 | 优先级 |
|---------|------|-------|
| K8s 资源变更 | 副本数、资源限制、亲和性等 | P3 |
| 中间件配置变更 | 参数配置、热更新/冷更新 | P2 |
| 存储卷变更 | PVC 扩容、存储类变更 | P1 |
| 版本升级 | 中间件版本升级 | P0 |

#### 3.3.2 任务结构

任务列表存储在 App 的 Annotation 中：

```yaml
metadata:
  annotations:
    middleware.io/tasks: |
      [
        {
          "taskId": "task-001",
          "type": "storage_volume",
          "description": "扩容 PVC 从 50Gi 到 100Gi",
          "priority": 10,
          "targetComponent": "redis-nodes",
          "desiredSpec": {
            "storage": {"size": "100Gi"}
          },
          "dependencies": [],
          "status": "in_progress",
          "retryCount": 0,
          "maxRetries": 3,
          "timeout": "300s",
          "startedAt": "2025-01-19T10:00:00Z",
          "completedAt": null,
          "error": null
        }
      ]
```

#### 3.3.3 任务生成

```go
// 变更检测与任务生成
func (r *AppReconciler) detectSpecChange(app *middlewarev1.App) *SpecChange {
    // 获取上一次处理的 Spec
    lastSpec := r.getLastProcessedSpec(app)
    if lastSpec == nil {
        return nil
    }

    // 对比 Spec
    if reflect.DeepEqual(lastSpec, app.Spec) {
        return nil
    }

    // 分析变更类型
    change := &SpecChange{
        OldSpec:   lastSpec,
        NewSpec:   app.Spec.DeepCopy(),
        Timestamp: time.Now(),
    }
    change.ChangeTypes = r.identifyChangeTypes(change)

    return change
}

// 生成任务列表
func (r *AppReconciler) generateTasks(app *middlewarev1.App, change *SpecChange) []ChangeTask {
    var tasks []ChangeTask

    // 按优先级从低到高排序（P0 最高优先级，最后执行）
    priorityMap := map[ChangeType]int{
        ChangeTypeK8sResources:      30, // P3
        ChangeTypeMiddlewareConfig:   20, // P2
        ChangeTypeStorageVolume:      10, // P1
        ChangeTypeVersionUpgrade:      0, // P0
    }

    // 为每种变更类型生成任务
    for _, ct := range change.ChangeTypes {
        task := ChangeTask{
            TaskID:        generateTaskID(),
            Type:          ct.Type,
            Description:   ct.Description,
            Priority:      priorityMap[ct.Type],
            TargetComponent: ct.Component,
            DesiredSpec:   ct.DesiredSpec,
            Timeout:       r.getDefaultTimeout(ct.Type),
            MaxRetries:    r.getDefaultMaxRetries(ct.Type),
            Dependencies:  r.calculateDependencies(tasks, ct),
        }
        tasks = append(tasks, task)
    }

    // 按优先级排序（高优先级在前）
    sort.Slice(tasks, func(i, j int) bool {
        return tasks[i].Priority < tasks[j].Priority
    })

    return tasks
}
```

#### 3.3.4 任务执行

```go
// 任务队列执行
func (r *AppReconciler) executeTaskQueue(app *middlewarev1.App) (*ctrl.Result, error) {
    tasks := r.getTasks(app)

    // 获取正在执行的任务
    activeTask := r.getActiveTask(app)

    // 1. 处理进行中的任务
    if activeTask != nil {
        if r.isTaskTimedOut(activeTask) {
            // 任务超时
            r.handleTaskTimeout(app, activeTask)
            return nil, r.Update(ctx, app)
        }

        // 检查任务是否完成
        if r.isTaskCompleted(app, activeTask) {
            r.markTaskCompleted(app, activeTask)
            if err := r.Update(ctx, app); err != nil {
                return nil, err
            }
        }

        // 任务仍在进行中，等待完成
        return ptr.To(ctrl.Result{RequeueAfter: 10 * time.Second}), nil
    }

    // 2. 找到下一个可执行的任务
    nextTask := r.findNextExecutableTask(app)
    if nextTask == nil {
        return nil, nil // 无待执行任务
    }

    // 3. 触发任务执行：修改 Component Spec
    if err := r.triggerTaskExecution(app, nextTask); err != nil {
        return nil, err
    }

    // 4. 标记任务为执行中
    r.markTaskInProgress(app, nextTask.TaskID)
    return nil, r.Update(ctx, app)
}
```

### 3.4 失败处理与重试

#### 3.4.1 任务状态流转

```
pending ──► in_progress ──► done
   │              │              │
   │              │              │
   │              ├─► failed ────┼─► retry_pending (手动重试)
   │              │              │
   │              │              └─► skipped (后续任务)
   │              │
   │              └─► timeout ──► failed
```

#### 3.4.2 自动重试

```go
// 任务失败处理
func (r *AppReconciler) handleTaskFailure(app *middlewarev1.App, task *ChangeTask, err error) {
    task.RetryCount++
    task.LastError = err.Error()

    if task.RetryCount >= task.MaxRetries {
        // 重试次数用尽，标记为失败
        task.Status = TaskStatusFailed
        // 跳过后续依赖任务
        r.skipDependentTasks(app, task)
    } else {
        // 安排重试（指数退避）
        backoff := time.Duration(math.Pow(2, float64(task.RetryCount-1))) * time.Second
        task.RetryAt = time.Now().Add(backoff)
        task.Status = TaskStatusRetryPending
    }
}
```

#### 3.4.3 手动重试

用户可通过 Annotation 手动触发重试：

```yaml
metadata:
  annotations:
    middleware.io/retry-control: |
      {
        "retryTaskIds": ["task-001"],
        "resetDependencies": false
      }
```

```go
// 处理手动重试
func (r *AppReconciler) processManualRetry(app *middlewarev1.App, retryTaskIds []string) {
    for _, taskID := range retryTaskIds {
        task := r.findTask(app, taskID)
        if task == nil || (task.Status != TaskStatusFailed && task.Status != TaskStatusSkipped) {
            continue
        }

        // 重置任务状态
        task.Status = TaskStatusPending
        task.Error = nil
        task.StartedAt = nil
        task.CompletedAt = nil
        task.RetryCount = 0

        r.recordRetry(app, task)
    }
}
```

### 3.5 任务取消

#### 3.5.1 取消规则

| 任务状态 | 是否支持取消 | 说明 |
|---------|-------------|------|
| pending | 是 | 直接标记为 cancelled |
| in_progress | 视情况 | 支持则中断，不支持则等待完成 |
| done | 否 | 已完成，无法取消 |
| failed | 否 | 已失败，无需取消 |

#### 3.5.2 用户操作

```yaml
metadata:
  annotations:
    middleware.io/cancel-control: |
      {
        "cancelTaskIds": ["task-002", "task-003"]
      }
```

```go
// 处理取消请求
func (r *AppReconciler) processCancellation(app *middlewarev1.App, cancelTaskIds []string) {
    for _, taskID := range cancelTaskIds {
        task := r.findTask(app, taskID)
        if task == nil {
            continue
        }

        switch task.Status {
        case TaskStatusPending:
            task.Status = TaskStatusCancelled

        case TaskStatusInProgress:
            task.CancelRequested = true
            // 等待 Component Controller 处理取消
        }
    }
}
```

### 3.6 超时处理

#### 3.6.1 超时配置

```yaml
metadata:
  annotations:
    middleware.io/tasks: |
      [
        {
          "taskId": "task-001",
          "type": "storage_volume",
          "timeout": "300s",
          "status": "in_progress",
          "startedAt": "2025-01-19T10:00:00Z"
        }
      ]
```

#### 3.6.2 超时检测与处理

```go
// 检测任务是否超时
func (r *AppReconciler) isTaskTimedOut(task *ChangeTask) bool {
    if task.StartedAt == nil || task.Timeout == "" {
        return false
    }

    timeout, _ := time.ParseDuration(task.Timeout)
    elapsed := time.Since(*task.StartedAt)
    return elapsed > timeout
}

// 处理任务超时
func (r *AppReconciler) handleTaskTimeout(app *middlewarev1.App, task *ChangeTask) {
    task.Status = TaskStatusFailed
    task.Error = fmt.Sprintf("任务执行超时（%s）", task.Timeout)
    task.CompletedAt = ptr.To(time.Now())

    // 标记所有依赖此任务的后续任务为跳过
    r.skipDependentTasks(app, task)
}
```

### 3.7 并发变更处理

当任务执行过程中用户修改了 App Spec，采用以下策略：

```
用户修改 App Spec
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  检测到新变更                                       │
│                                                    │
│  ┌─────────────────────────────────────────────┐  │
│  │  是否有任务正在执行？                          │  │
│  └────────────────────┬────────────────────────┘  │
│                       │                          │
│            ┌──────────┴──────────┐               │
│            │                     │               │
│            ▼                     ▼               │
│     无任务正在执行          有任务正在执行        │
│            │                     │               │
│            ▼                     ▼               │
│     直接生成新任务           记录待处理变更       │
│     开始执行                 提示用户选择         │
│                                         ┌────────┴────────┐
│                                         │                 │
│                                         ▼                 ▼
│                                   等待完成           用户取消
│                                         │                 │
│                                         ▼                 ▼
│                                   当前任务完成         取消并处理新变更
│                                         │                 │
│                                         ▼                 │
│                                   处理待处理变更        │
└─────────────────────────────────────────────────────────┘
```

```go
// 处理 Spec 变更
func (r *AppReconciler) handleSpecChange(app *middlewarev1.App, change *SpecChange) error {
    // 检查是否有任务正在执行
    activeTask := r.getActiveTask(app)

    if activeTask != nil {
        // 有任务正在执行：记录待处理变更，提示用户
        r.queuePendingChange(app, change)
        r.promptUserChoice(app)
        return nil
    }

    // 无任务执行：直接处理新变更
    tasks := r.generateTasks(app, change)
    r.updateTasks(app, tasks)
    return nil
}

// 提示用户选择
func (r *AppReconciler) promptUserChoice(app *middlewarev1.App) {
    app.Annotations["middleware.io/pending-change-detected"] = "true"
    // 用户可通过以下方式操作：
    // - 等待当前任务完成（系统自动处理）
    // - 取消当前任务：kubectl annotate app <name> middleware.io/cancel-control='{"cancelTaskIds": ["task-xxx"]}'
}
```

### 3.8 并发控制

通过插件的 orders 字段定义 Component 的执行顺序。

#### 3.8.1 插件 orders 定义

```yaml
# Plugin ConfigMap 中的 orders 字段
spec:
  orders:
    provision: [storage, compute]     # storage 先于 compute 部署
    stop: [compute, storage]          # compute 先于 storage 停止
    update: [storage, compute]        # storage 先更新
    upgrade: [storage, compute]       # 升级时 storage 先准备
```

#### 3.8.2 订单格式

```yaml
# 数组顺序即执行顺序
orders:
  provision: [a, b, c]    # 顺序执行：a → b → c
  stop: [c, b, a]         # 顺序执行：c → b → a

# 不定义或空数组表示并发
orders:
  provision: null         # 所有 Component 并发执行
  # 或
  provision: []           # 所有 Component 并发执行
```

#### 3.8.3 获取执行顺序

```go
// 根据场景获取执行顺序
func (r *AppReconciler) getExecutionOrder(plugin *middlewarev1.Plugin, scenario string) []string {
    orders := plugin.Spec.Orders
    if orders == nil || len(orders) == 0 {
        return nil // 并发执行
    }

    order, ok := orders[scenario]
    if !ok {
        return nil // 场景未定义，并发执行
    }

    return order
}
```

### 3.9 配置验证

```go
func (r *AppReconciler) validateApp(app *middlewarev1.App) error {
    // 1. 验证插件引用
    plugin, err := r.getPlugin(app.Spec.Plugin.Name, app.Spec.Plugin.Version)
    if err != nil {
        return fmt.Errorf("plugin not found: %w", err)
    }

    // 2. 验证运行时版本
    if !plugin.SupportsRuntime(app.Spec.Runtime.Name, app.Spec.Runtime.Version) {
        return fmt.Errorf("runtime version %s/%s not supported by plugin",
            app.Spec.Runtime.Name, app.Spec.Runtime.Version)
    }

    // 3. 验证监控配置
    if app.Spec.Monitoring != nil {
        if err := r.validateMonitoringConfig(app.Spec.Monitoring); err != nil {
            return fmt.Errorf("invalid monitoring config: %w", err)
        }
    }

    // 4. 验证备份配置
    if app.Spec.Backup != nil {
        if err := r.validateBackupConfig(app.Spec.Backup); err != nil {
            return fmt.Errorf("invalid backup config: %w", err)
        }
    }

    return nil
}
```

### 3.10 元数据更新

```go
func (r *AppReconciler) updateMetadata(app *middlewarev1.App) error {
    metadata := &corev1.ConfigMap{}
    metadataKey := types.NamespacedName{
        Name:      "middleware-metadata",
        Namespace: "middleware-system",
    }

    if err := r.Get(ctx, metadataKey, metadata); err != nil {
        return err
    }

    metadata.Data[app.Name] = r.generateAppMetadata(app)

    if metadata.ResourceVersion != "" {
        if err := r.Update(ctx, metadata); err != nil {
            return fmt.Errorf("metadata update conflict: %w", err)
        }
    }

    return nil
}
```

## 4. Component Controller

### 4.1 核心职责

Component Controller 负责管理 Component 资源，是 App 和 Group 之间的桥梁。

```
Component Controller 职责：
┌─────────────────────────────────────────────────────────────┐
│  1. Spec 变更检测                                            │
│     ├── 对比 Component Spec 变化                             │
│     ├── 识别变更类型（K8s资源/配置/存储/版本）                │
│     └── 确定编排场景                                         │
│                                                              │
│  2. Group 编排                                               │
│     ├── 从 Agent2 获取 Group 执行顺序（gRPC）                │
│     ├── 按顺序触发 Group Spec 更新                           │
│     └── 等待 Group 完成                                      │
│                                                              │
│  3. 任务取消处理                                             │
│     ├── 接收 App Controller 的取消请求                       │
│     ├── 尝试取消当前操作                                     │
│     └── 上报取消结果                                         │
│                                                              │
│  4. 状态上报                                                 │
│     ├── 收集 Group 执行结果                                  │
│     └── 上报到 App Controller                                │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 调和逻辑

```go
func (r *ComponentReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    component := &middlewarev1.Component{}
    if err := r.Get(ctx, req.NamespacedName, component); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 1. 处理取消请求
    if r.hasCancelRequest(component) {
        result := r.processCancellation(component)
        if result.Action == CancelActionCompleted {
            component.Status.MarkCancelled()
            return ctrl.Result{}, r.Status().Update(ctx, component)
        }
    }

    // 2. 检测 Spec 变化
    changes := r.detectSpecChanges(component)
    if len(changes) == 0 {
        return r.syncStatus(component)
    }

    // 3. 分析变更，确定场景
    scenario := r.detectScenario(changes)

    // 4. 获取 Group 执行顺序
    order, concurrent := r.getGroupExecutionOrder(component, scenario)

    // 5. 触发 Group 执行
    if concurrent {
        // 并发执行
        for _, groupName := range order {
            r.triggerGroupExecution(component, groupName, changes)
        }
    } else {
        // 顺序执行
        for i, groupName := range order {
            if i > 0 {
                if !r.isGroupCompleted(component, order[i-1]) {
                    return ctrl.Result{RequeueAfter: 10 * time.Second}, nil
                }
            }
            r.triggerGroupExecution(component, groupName, changes)
        }
    }

    // 6. 标记状态
    component.Status.MarkOperationInProgress(scenario)
    return ctrl.Result{RequeueAfter: 10 * time.Second}, nil
}
```

### 4.3 Group 顺序获取（gRPC）

Component Controller 通过 gRPC 调用 Agent2 的 `GetGroupOrder` 接口获取 Group 的执行顺序。

```go
// 从 Agent2 获取 Group 执行顺序
func (r *ComponentReconciler) getGroupExecutionOrder(
    component *middlewarev1.Component,
    scenario string,
) ([]string, bool) {
    groups := r.listComponentGroups(component)

    // 调用 Agent2 gRPC
    pod := r.selectAnyPod(component)
    if pod == nil {
        return groups, true // 无法获取顺序时并发执行
    }

    conn, err := r.dialAgent2(pod)
    if err != nil {
        return groups, true
    }
    defer conn.Close()

    client := agent2.NewAgent2Client(conn)

    resp, err := client.GetGroupOrder(ctx, &agent2.GetGroupOrderRequest{
        ComponentName: component.Name,
        Scenario:      scenario,
        Groups:        groups,
    })

    if err != nil {
        return groups, true
    }

    if resp.Concurrent || len(resp.Order) == 0 {
        return groups, true
    }

    return resp.Order, false
}
```

### 4.4 Group 配置生成

```go
func (r *ComponentReconciler) createGroup(
    component *middlewarev1.Component,
    plugin *middlewarev1.Plugin,
    groupSpec middlewarev1.GroupSpec,
) error {
    group := &middlewarev1.Group{
        ObjectMeta: metav1.ObjectMeta{
            Name:      component.Name + "-" + groupSpec.Name,
            Namespace: component.Namespace,
            Labels: map[string]string{
                "middleware.io/app":       component.Spec.AppRef.Name,
                "middleware.io/component": component.Name,
                "middleware.io/plugin":    plugin.Name,
            },
        },
        Spec: middlewarev1.GroupSpec{
            ComponentRef: middlewarev1.ComponentRef{
                Name:      component.Name,
                Namespace: component.Namespace,
            },
            PluginRef: middlewarev1.PluginRef{
                Name:      plugin.Name + "-v" + plugin.Version,
                Namespace: "middleware-system",
            },
            Replicas:  groupSpec.Replicas,
            Resources: groupSpec.Resources,
            Values:    r.mergeValues(component, groupSpec, plugin),
        },
    }

    return r.Create(ctx, group)
}
```

## 5. Group Controller

### 5.1 核心职责

Group Controller 是最接近 Pod 层的控制器，负责资源配置、模板渲染和 Pod 管理。

```
Group Controller 职责：
┌─────────────────────────────────────────────────────────────┐
│  1. Spec 变更检测                                            │
│     ├── 对比 Group Spec 变化                                 │
│     └── 识别需要执行的操作                                   │
│                                                              │
│  2. Pod 顺序获取                                             │
│     ├── 从 Agent2 获取 Pod 处理顺序（gRPC）                  │
│     └── 按顺序执行操作                                       │
│                                                              │
│  3. 模板渲染与资源操作                                       │
│     ├── 渲染 Deployment、Service、ConfigMap、PVC            │
│     └── 创建/更新 Kubernetes 资源                            │
│                                                              │
│  4. 任务取消处理                                             │
│     ├── 接收 Component Controller 的取消请求                 │
│     ├── 尝试取消当前操作                                     │
│     └── 上报取消结果                                         │
│                                                              │
│  5. 状态上报                                                 │
│     ├── 收集 Pod 状态                                        │
│     └── 上报到 Component Controller                          │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 调和逻辑

```go
func (r *GroupReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    group := &middlewarev1.Group{}
    if err := r.Get(ctx, req.NamespacedName, group); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 1. 处理取消请求
    if group.Annotations["middleware.io/cancel-request"] == "true" {
        result := r.processCancellation(group)
        if result.Action == CancelActionCompleted {
            r.rollbackGroup(group)
            group.Annotations["middleware.io/cancel-request"] = ""
            group.Status.MarkCancelled()
            return ctrl.Result{}, r.Status().Update(ctx, group)
        }
    }

    // 2. 检测 Spec 变化
    changes := r.detectSpecChanges(group)
    if len(changes) == 0 {
        return r.syncStatus(group)
    }

    // 3. 分析变更，确定场景
    scenario := r.detectScenario(changes)

    // 4. 获取 Pod 处理顺序
    order, concurrent := r.getPodExecutionOrder(group, scenario)

    // 5. 按顺序执行操作
    if concurrent {
        for _, podName := range order {
            r.executePodOperation(group, podName, changes)
        }
    } else {
        for i, podName := range order {
            if i > 0 {
                if !r.isPodCompleted(group, order[i-1]) {
                    return ctrl.Result{RequeueAfter: 5 * time.Second}, nil
                }
            }
            r.executePodOperation(group, podName, changes)
        }
    }

    // 6. 标记状态
    group.Status.MarkOperationInProgress(scenario)
    return ctrl.Result{RequeueAfter: 5 * time.Second}, nil
}
```

### 5.3 Pod 顺序获取（gRPC）

Group Controller 通过 gRPC 调用 Agent2 的 `GetPodOrder` 接口获取 Pod 的处理顺序。

```go
// 从 Agent2 获取 Pod 处理顺序
func (r *GroupReconciler) getPodExecutionOrder(
    group *middlewarev1.Group,
    scenario string,
) ([]string, bool) {
    pods := r.listGroupPods(group)

    // 调用 Agent2 gRPC
    pod := r.selectAnyPod(group)
    if pod == nil {
        return pods, true // 无法获取顺序时并发执行
    }

    conn, err := r.dialAgent2(pod)
    if err != nil {
        return pods, true
    }
    defer conn.Close()

    client := agent2.NewAgent2Client(conn)

    resp, err := client.GetPodOrder(ctx, &agent2.GetPodOrderRequest{
        GroupName: group.Name,
        Scenario:  scenario,
        Pods:      pods,
    })

    if err != nil {
        return pods, true
    }

    if resp.Concurrent || len(resp.Order) == 0 {
        return pods, true
    }

    return resp.Order, false
}
```

### 5.4 模板渲染

```go
func (r *GroupReconciler) renderDeployment(group *middlewarev1.Group, plugin *middlewarev1.Plugin) (*appsv1.Deployment, error) {
    // 获取模板
    templateConfigMap, err := r.getTemplateConfigMap(plugin, "deployment")
    if err != nil {
        return nil, err
    }

    // 准备模板数据
    values := r.prepareTemplateValues(group, plugin)

    // 渲染模板
    tmpl := template.Must(
        template.New("deployment").Parse(templateConfigMap.Data["template"]),
    )

    var buf bytes.Buffer
    if err := tmpl.Execute(&buf, values); err != nil {
        return nil, fmt.Errorf("template render error: %w", err)
    }

    // 解析为 Deployment
    deployment := &appsv1.Deployment{}
    if err := yaml.Unmarshal(buf.Bytes(), deployment); err != nil {
        return nil, fmt.Errorf("deployment parse error: %w", err)
    }

    return deployment, nil
}

func (r *GroupReconciler) prepareTemplateValues(group *middlewarev1.Group, plugin *middlewarev1.Plugin) TemplateValues {
    return TemplateValues{
        Name:      group.Name,
        Namespace: group.Namespace,
        Component: group.Labels["middleware.io/component"],
        Group:     group.Name,
        Replicas:  group.Spec.Replicas,
        Runtime: RuntimeInfo{
            Name:    group.Spec.Runtime.Name,
            Version: group.Spec.Runtime.Version,
        },
        Images: plugin.Spec.Images,
        Plugin: PluginInfo{
            Name:    plugin.Name,
            Version: plugin.Version,
        },
        Resources: group.Spec.Resources,
        Config:    group.Spec.Values,
        Storage:   group.Spec.Storage,
        Affinity:  group.Spec.Affinity,
        Labels:    r.generateLabels(group),
        SelectorLabels: r.generateSelectorLabels(group),
    }
}
```

### 5.5 gRPC 状态更新

```go
func (r *GroupReconciler) updateNodeStatus(group *middlewarev1.Group, podStatus PodStatus) error {
    pods, err := r.listPods(group)
    if err != nil {
        return err
    }

    for _, pod := range pods {
        conn, err := r.dialAgent2(pod)
        if err != nil {
            continue
        }
        defer conn.Close()

        client := toolinvoker.NewToolInvokerClient(conn)

        roleResp, err := client.GetRole(ctx, &toolinvoker.GetRoleRequest{})
        if err != nil {
            r.Logger.Error(err, "failed to get role", "pod", pod.Name)
            continue
        }

        if err := r.reportNodeStatus(group, pod, roleResp); err != nil {
            r.Logger.Error(err, "failed to report node status", "pod", pod.Name)
        }
    }

    return nil
}
```

## 6. 控制器交互

### 6.1 状态上报流

```
Pod                      Group Controller              App Controller
  │                            │                            │
  │── Pod Status ─────────────►│                            │
  │                            │                            │
  │                            │── Node Status ────────────►│
  │                            │                            │
  │                            │                            │── Update Metadata
```

### 6.2 配置下发流

```
App Controller              Component Controller          Group Controller
      │                            │                            │
      │── Modify Spec ────────────►│                            │
      │                            │── Modify Spec ────────────►│
      │                            │                            │
      │                            │                            │── Render & Apply
```

### 6.3 任务编排流

```
用户修改 App
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ App Controller                                                │
│  - 检测 Spec 变更                                             │
│  - 生成任务列表                                               │
│  - 修改 Component Spec                                        │
│  - 轮询状态等待完成                                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Component Controller                                          │
│  - 检测 Spec 变更                                             │
│  - gRPC 获取 Group 顺序                                       │
│  - 按顺序修改 Group Spec                                      │
│  - 轮询状态等待完成                                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Group Controller                                              │
│  - 检测 Spec 变更                                             │
│  - gRPC 获取 Pod 顺序                                         │
│  - 按顺序执行资源操作                                         │
│  - 上报状态                                                   │
└─────────────────────────────────────────────────────────────┘
```

## 7. 控制器配置

### 7.1 全局配置

```yaml
# controllers.yaml
controllers:
  # App Controller 配置
  app:
    workers: 5                       # 并发 worker 数
    resyncPeriod: 30s                # 重新同步周期
    metadataCacheTTL: 60s            # 元数据缓存 TTL
    maxRetries: 3                    # 默认最大重试次数
    retryBackoff: 1s                 # 重试退避时间
    defaultTaskTimeout: "300s"       # 默认任务超时时间
    enableManualRetry: true          # 是否允许手动重试
    enableManualCancel: true         # 是否允许手动取消

  # Component Controller 配置
  component:
    workers: 10
    resyncPeriod: 15s
    cacheTTL: 30s
    grpcTimeout: 30s                 # gRPC 调用超时

  # Group Controller 配置
  group:
    workers: 20
    resyncPeriod: 10s
    grpcTimeout: 30s
    maxConcurrentReconciles: 10
    rollingUpdate:
      batchSize: 1
      interval: 10s
```

### 7.2 控制器部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middleware-controller-manager
  namespace: middleware-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: middleware-controller-manager
  template:
    spec:
      containers:
      - name: manager
        image: middleware/controller:v1.0.0
        args:
        - --controllers=all
        - --metrics-addr=:8080
        - --enable-leader-election
        env:
        - name: WATCH_NAMESPACE
          value: ""
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
```

## 8. 错误处理

### 8.1 错误分类与处理

| 错误类型 | 处理方式 | 是否重试 |
|---------|---------|---------|
| 配置错误 | 返回错误，不重试 | 否 |
| 资源不存在 | 创建资源 | 是 |
| 资源冲突 | 乐观锁重试 | 是 |
| 网络超时 | 重试 | 是 |
| 权限不足 | 返回错误 | 否 |
| 资源不足 | 返回错误 | 否 |
| 任务超时 | 标记失败，跳过后续 | 否 |

### 8.2 可重试错误判断

```go
func IsRetryableError(err error) bool {
    if _, ok := err.(*reconcile.Error); ok {
        return true
    }
    if strings.Contains(err.Error(), "connection refused") {
        return true
    }
    if kerrors.IsNotFound(err) {
        return false
    }
    return true
}
```

## 9. 文档导航

- 上一章：[架构概览](./01-architecture-overview.md)
- 下一章：[App CRD 规范](./02-crd-app.md)
- 相关文档：[Agent 设计](./06-agent-design.md)、[滚动升级](./10-rolling-upgrade.md)、[插件系统](./05-plugin-system.md)

## 10. 版本历史

| 版本 | 日期 | 修改内容 |
|-----|------|---------|
| 2.0.0 | 2025-01-19 | 大幅增强控制器设计，新增任务编排机制、失败重试、任务取消、超时处理、并发变更处理、并发控制、gRPC 顺序获取等内容 |
| 1.0.0 | 2025-01-19 | 初始版本 |
