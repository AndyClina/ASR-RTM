"""
转录模式菜单模块
负责创建和管理转录模式相关的菜单项
"""
import traceback
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup
from PyQt5.QtCore import pyqtSignal

from src.utils.logger import get_logger
from src.core.plugins import PluginManager

logger = get_logger(__name__)

class TranscriptionMenu(QMenu):
    """转录模式菜单类"""

    model_selected = pyqtSignal(str)  # 模型ID
    rtm_model_selected = pyqtSignal(str)  # RTM模型ID

    def __init__(self, parent=None):
        """
        初始化转录模式菜单

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setTitle("转录模式(&T)")  # 设置菜单标题，带有快捷键

        # 初始化插件管理器
        self.plugin_manager = PluginManager()

        # 创建菜单项
        self.actions = {}
        self._create_language_mode_submenu()
        self._create_asr_model_submenu()
        self._create_rtm_model_submenu()
        self._create_audio_mode_submenu()
        self._create_file_mode_submenu()
        self._create_control_actions()

    def _create_language_mode_submenu(self):
        """创建语言模式子菜单"""
        self.language_mode_menu = QMenu("语言模式(&L)", self)
        self.addMenu(self.language_mode_menu)

        # 创建语言选择动作组
        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)

        # 创建语言选择动作
        self.actions['en_rec'] = QAction("英文识别(&E)", self, checkable=True)
        self.actions['cn_rec'] = QAction("中文识别(&C)", self, checkable=True)
        self.actions['auto_rec'] = QAction("自动识别(&A)", self, checkable=True)

        # 将动作添加到组
        self.lang_group.addAction(self.actions['en_rec'])
        self.lang_group.addAction(self.actions['cn_rec'])
        self.lang_group.addAction(self.actions['auto_rec'])

        # 将动作添加到菜单
        self.language_mode_menu.addAction(self.actions['en_rec'])
        self.language_mode_menu.addAction(self.actions['cn_rec'])
        self.language_mode_menu.addAction(self.actions['auto_rec'])

        # 设置默认选中项
        self.actions['en_rec'].setChecked(True)

    def _create_asr_model_submenu(self):
        """创建ASR语音识别模型子菜单"""
        self.asr_model_menu = QMenu("ASR语音识别模型(&A)", self)
        self.addMenu(self.asr_model_menu)

        # 创建ASR模型选择动作组
        self.asr_group = QActionGroup(self)
        self.asr_group.setExclusive(True)

        # 创建Vosk系列子菜单
        self.vosk_menu = QMenu("vosk系列(&V)", self)
        self.asr_model_menu.addMenu(self.vosk_menu)

        # 创建Vosk模型选择动作
        self.actions['vosk_small'] = QAction("vosk_small(&S)", self, checkable=True)
        self.actions['vosk_medium'] = QAction("vosk_medium(&M)", self, checkable=True)
        self.actions['vosk_large'] = QAction("vosk_large(&L)", self, checkable=True)

        # 将Vosk动作添加到组
        self.asr_group.addAction(self.actions['vosk_small'])
        self.asr_group.addAction(self.actions['vosk_medium'])
        self.asr_group.addAction(self.actions['vosk_large'])

        # 将Vosk动作添加到菜单
        self.vosk_menu.addAction(self.actions['vosk_small'])
        self.vosk_menu.addAction(self.actions['vosk_medium'])
        self.vosk_menu.addAction(self.actions['vosk_large'])

        # 创建Sherpa-ONNX系列子菜单
        self.sherpa_menu = QMenu("sherpa_onnx系列(&S)", self)
        self.asr_model_menu.addMenu(self.sherpa_menu)

        # 创建Sherpa-ONNX 0220子菜单
        self.sherpa_0220_menu = QMenu("sherpa_0220(&2)", self)
        self.sherpa_menu.addMenu(self.sherpa_0220_menu)

        # 创建Sherpa-ONNX 0220模型选择动作
        self.actions['sherpa_0220_int8'] = QAction("sherpa_0220_int8(&I)", self, checkable=True)
        self.actions['sherpa_0220_std'] = QAction("sherpa_0220_std(&S)", self, checkable=True)

        # 将Sherpa-ONNX 0220动作添加到组
        self.asr_group.addAction(self.actions['sherpa_0220_int8'])
        self.asr_group.addAction(self.actions['sherpa_0220_std'])

        # 将Sherpa-ONNX 0220动作添加到菜单
        self.sherpa_0220_menu.addAction(self.actions['sherpa_0220_int8'])
        self.sherpa_0220_menu.addAction(self.actions['sherpa_0220_std'])

        # 创建Sherpa-ONNX 0621子菜单
        self.sherpa_0621_menu = QMenu("sherpa_0621(&6)", self)
        self.sherpa_menu.addMenu(self.sherpa_0621_menu)

        # 创建Sherpa-ONNX 0621模型选择动作
        self.actions['sherpa_0621_int8'] = QAction("sherpa_0621_int8(&I)", self, checkable=True)
        self.actions['sherpa_0621_std'] = QAction("sherpa_0621_std(&S)", self, checkable=True)

        # 将Sherpa-ONNX 0621动作添加到组
        self.asr_group.addAction(self.actions['sherpa_0621_int8'])
        self.asr_group.addAction(self.actions['sherpa_0621_std'])

        # 将Sherpa-ONNX 0621动作添加到菜单
        self.sherpa_0621_menu.addAction(self.actions['sherpa_0621_int8'])
        self.sherpa_0621_menu.addAction(self.actions['sherpa_0621_std'])

        # 创建Sherpa-ONNX 0626子菜单
        self.sherpa_0626_menu = QMenu("sherpa_0626(&6)", self)
        self.sherpa_menu.addMenu(self.sherpa_0626_menu)

        # 创建Sherpa-ONNX 0626模型选择动作
        self.actions['sherpa_0626_int8'] = QAction("sherpa_0626_int8(&I)", self, checkable=True)
        self.actions['sherpa_0626_std'] = QAction("sherpa_0626_std(&S)", self, checkable=True)

        # 将Sherpa-ONNX 0626动作添加到组
        self.asr_group.addAction(self.actions['sherpa_0626_int8'])
        self.asr_group.addAction(self.actions['sherpa_0626_std'])

        # 将Sherpa-ONNX 0626动作添加到菜单
        self.sherpa_0626_menu.addAction(self.actions['sherpa_0626_int8'])
        self.sherpa_0626_menu.addAction(self.actions['sherpa_0626_std'])

        # 设置默认选中项
        self.actions['vosk_small'].setChecked(True)

        # 连接ASR模型选择信号
        for model_id in ['vosk_small', 'vosk_medium', 'vosk_large',
                         'sherpa_0220_int8', 'sherpa_0220_std',
                         'sherpa_0621_int8', 'sherpa_0621_std',
                         'sherpa_0626_int8', 'sherpa_0626_std']:
            if model_id in self.actions:
                self.actions[model_id].triggered.connect(
                    lambda checked, mid=model_id: self._on_asr_model_selected(mid)
                )

    def _create_rtm_model_submenu(self):
        """创建RTM实时翻译模型子菜单"""
        self.rtm_model_menu = QMenu("RTM实时翻译模型(&R)", self)
        self.addMenu(self.rtm_model_menu)

        # 创建RTM模型选择动作组
        self.rtm_group = QActionGroup(self)
        self.rtm_group.setExclusive(True)

        # 创建RTM模型选择动作
        self.actions['opus'] = QAction("Opus-MT 模型(&O)", self, checkable=True)
        self.actions['argos'] = QAction("ArgosTranslate 模型(&A)", self, checkable=True)

        # 将动作添加到组
        self.rtm_group.addAction(self.actions['opus'])
        self.rtm_group.addAction(self.actions['argos'])

        # 将动作添加到菜单
        self.rtm_model_menu.addAction(self.actions['opus'])
        self.rtm_model_menu.addAction(self.actions['argos'])

        # 设置默认选中项
        self.actions['argos'].setChecked(True)

        # 连接RTM模型选择信号
        for model_id in ['opus', 'argos']:
            if model_id in self.actions:
                self.actions[model_id].triggered.connect(
                    lambda checked, mid=model_id: self._on_rtm_model_selected(mid)
                )

    def _create_audio_mode_submenu(self):
        """创建系统音频模式子菜单"""
        self.actions['system_audio'] = QAction("系统音频模式(&S)", self, checkable=True)
        self.addAction(self.actions['system_audio'])

        # 设置默认选中项
        self.actions['system_audio'].setChecked(True)

    def _create_file_mode_submenu(self):
        """创建文件音频模式子菜单"""
        self.actions['file_audio'] = QAction("文件音频模式(&F)", self, checkable=True)
        self.addAction(self.actions['file_audio'])

        # 创建音频模式选择动作组
        self.audio_mode_group = QActionGroup(self)
        self.audio_mode_group.setExclusive(True)

        # 将动作添加到组
        self.audio_mode_group.addAction(self.actions['system_audio'])
        self.audio_mode_group.addAction(self.actions['file_audio'])

    def _create_control_actions(self):
        """创建控制动作"""
        # 添加分隔线
        self.addSeparator()

        # 注：开始/停止转录功能已移至UI界面按钮，不再在菜单中显示

    def _on_asr_model_selected(self, model_id):
        """ASR模型选择处理"""
        logger.info(f"已选择ASR模型: {model_id}")
        self.model_selected.emit(model_id)

    def _on_rtm_model_selected(self, model_id):
        """RTM模型选择处理"""
        logger.info(f"已选择RTM模型: {model_id}")
        self.rtm_model_selected.emit(model_id)

    def connect_signals(self, main_window):
        """
        连接信号到主窗口槽函数

        Args:
            main_window: 主窗口实例
        """
        try:
            # 语言选择信号
            self.actions['en_rec'].triggered.connect(
                lambda: main_window.set_recognition_language("en")
            )
            self.actions['cn_rec'].triggered.connect(
                lambda: main_window.set_recognition_language("zh")
            )
            self.actions['auto_rec'].triggered.connect(
                lambda: main_window.set_recognition_language("auto")
            )

            # 音频模式选择信号
            self.actions['system_audio'].triggered.connect(
                lambda: main_window.set_audio_mode("system")
            )
            self.actions['file_audio'].triggered.connect(
                lambda: main_window.set_audio_mode("file")
            )

            # 连接ASR模型选择信号
            self.model_selected.connect(main_window.set_asr_model)

            # 连接RTM模型选择信号
            self.rtm_model_selected.connect(main_window.set_rtm_model)

            logger.info("转录模式菜单信号连接完成")
        except Exception as e:
            logger.error(f"连接转录模式菜单信号时出错: {str(e)}")
            logger.error(traceback.format_exc())

    def update_menu_state(self, is_recording=False):
        """
        更新菜单状态

        Args:
            is_recording: 是否正在录音
        """
        try:
            # 在录音时禁用某些动作
            self.actions['en_rec'].setEnabled(not is_recording)
            self.actions['cn_rec'].setEnabled(not is_recording)
            self.actions['auto_rec'].setEnabled(not is_recording)

            # 禁用所有模型选择动作
            for model_id in ['vosk_small', 'vosk_medium', 'vosk_large',
                            'sherpa_0220_int8', 'sherpa_0220_std',
                            'sherpa_0621_int8', 'sherpa_0621_std',
                            'sherpa_0626_int8', 'sherpa_0626_std',
                            'opus', 'argos']:
                if model_id in self.actions:
                    self.actions[model_id].setEnabled(not is_recording)

            # 禁用音频模式选择动作
            self.actions['system_audio'].setEnabled(not is_recording)
            self.actions['file_audio'].setEnabled(not is_recording)

            logger.debug(f"转录模式菜单状态已更新，录音状态: {is_recording}")
        except Exception as e:
            logger.error(f"更新转录模式菜单状态时出错: {str(e)}")
            logger.error(traceback.format_exc())
