# 配置文件说明

本文档介绍了实时转录系统的配置文件结构和使用方法。

## 配置文件概述

系统使用以下主要配置文件：

1. **config.json** - 主配置文件，包含应用程序的基本设置
2. **models.json** - 模型配置文件，包含所有ASR和翻译模型的配置
3. **plugins.json** - 插件配置文件，包含所有插件的配置

## config.json

主配置文件包含以下主要部分：

```json
{
    "version": "2.0.0",
    "app": { ... },
    "paths": { ... },
    "transcription": { ... },
    "translation": { ... },
    "window": { ... },
    "ui": { ... },
    "logging": { ... },
    "performance": { ... },
    "plugin_system": { ... }
}
```

### 主要配置项说明

- **version**: 配置文件版本号
- **app**: 应用程序基本信息
  - **name**: 应用程序名称
  - **default_file**: 默认测试文件路径
- **paths**: 重要路径配置
  - **models_base**: 模型基础目录
  - **models_config**: 模型配置文件路径
  - **plugins_config**: 插件配置文件路径
  - **logs_dir**: 日志目录
- **transcription**: 转录相关配置
  - **default_model**: 默认ASR模型
  - **chunk_size**: 音频分块大小（秒）
  - **tail_padding**: 尾部填充（秒）
  - **sample_rate**: 采样率
  - **language**: 语言
  - **asr**: ASR特定配置
    - **enable_endpoint**: 是否启用端点检测
    - **rule1_min_trailing_silence**: 规则1最小尾部静音（秒）
    - **rule2_min_trailing_silence**: 规则2最小尾部静音（秒）
    - **rule3_min_utterance_length**: 规则3最小语音长度（秒）
- **translation**: 翻译相关配置
  - **default_engine**: 默认翻译引擎
  - **performance**: 性能相关配置
- **window**: 窗口相关配置
  - **title**: 窗口标题
  - **pos_x/pos_y**: 窗口位置
  - **width/height**: 窗口大小
  - **opacity**: 窗口透明度
  - **always_on_top**: 是否总是置顶
  - **background_mode**: 背景模式
- **ui**: UI相关配置
  - **theme**: 主题
  - **language**: 界面语言
  - **fonts**: 字体配置
  - **colors**: 颜色配置
- **logging**: 日志配置
- **performance**: 性能配置
- **plugin_system**: 插件系统配置

## models.json

模型配置文件包含所有ASR和翻译模型的详细配置：

```json
{
    "asr": {
        "vosk_small": { ... },
        "sherpa_0220_int8": { ... },
        "sherpa_0220_std": { ... },
        "sherpa_0626_int8": { ... },
        "sherpa_0626_std": { ... }
    },
    "translation": {
        "opus": { ... },
        "argos": { ... }
    }
}
```

### 模型配置项说明

每个模型配置包含以下主要字段：

- **path**: 模型路径（绝对路径）
- **type**: 模型类型
- **enabled**: 是否启用
- **config**: 模型特定配置

## plugins.json

插件配置文件包含所有插件的详细配置：

```json
{
    "version": "1.0.0",
    "plugins": {
        "asr": { ... },
        "translation": { ... }
    },
    "plugin_system": { ... }
}
```

### 插件配置项说明

每个插件配置包含以下主要字段：

- **enabled**: 是否启用
- **type**: 插件类型
- **model_config**: 对应的模型配置
- **plugin_config**: 插件特定配置

## 配置文件使用建议

1. 使用绝对路径引用模型，避免路径问题
2. 修改配置前先备份
3. 遵循JSON格式规范，确保格式正确
4. 修改后重启应用程序使配置生效

## 配置文件位置

所有配置文件位于项目根目录的 `config` 文件夹中。
