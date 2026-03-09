"""
TIK5 GUI i18n - Wrapper around src/languages.py for GUI strings.
"""
import os
import sys
import json

# Ensure TIK root is on path
_tik_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _tik_root not in sys.path:
    sys.path.insert(0, _tik_root)

from src import languages

# Additional GUI-specific strings
GUI_STRINGS = {
    "English": {
        "home": "Home",
        "settings": "Settings",
        "about": "About",
        "unpack": "Unpack",
        "pack": "Pack",
        "plugins": "Plugins",
        "pack_rom": "Pack ROM",
        "tools": "Tools",
        "download": "Download",
        "new_project": "New Project",
        "unpack_rom": "Unpack ROM",
        "download_rom": "Download ROM",
        "delete_project": "Delete Project",
        "project_name": "Project Name",
        "enter_project_name": "Enter Project Name:",
        "confirm_delete": "Are you sure you want to delete",
        "yes": "Yes",
        "no": "No",
        "cancel": "Cancel",
        "ok": "OK",
        "refresh": "Refresh",
        "unpack_selected": "Unpack Selected",
        "unpack_all": "Unpack All",
        "pack_selected": "Pack Selected",
        "pack_all": "Pack All",
        "pack_super": "Pack Super",
        "pack_payload": "Pack Payload",
        "output_format": "Output Format",
        "filesystem": "File System",
        "install_mpk": "Install MPK",
        "uninstall": "Uninstall",
        "run": "Run",
        "magisk_patcher": "Magisk Patcher",
        "disable_avb": "Disable AVB",
        "disable_encryption": "Disable Encryption",
        "console": "Console",
        "clear_console": "Clear",
        "running": "Running...",
        "completed": "Completed",
        "error": "Error",
        "no_projects": "No projects found. Create a new project or unpack a ROM.",
        "drag_drop_hint": "Drag & drop ROM file here or click to browse",
        "packaging_settings": "Packaging Settings",
        "dynamic_partition_settings": "Dynamic Partition Settings",
        "tool_settings": "Tool Settings",
        "brotli_level": "Brotli Level",
        "ext4_size": "EXT4 Size Handle",
        "pack_method": "Packing Method",
        "pack_sparse": "Pack as Sparse",
        "erofs_compression": "EROFS Compression",
        "utc_timestamp": "UTC Timestamp",
        "image_format": "Image Format",
        "erofs_old_kernel": "EROFS Old Kernel",
        "super_group": "Super Group Name",
        "metadata_size": "Metadata Size",
        "block_size": "Block Size",
        "super_block_size": "Super Block Size",
        "physical_name": "Physical Partition Name",
        "force_super": "Force Super Image",
        "slot_suffix": "Slot Suffix",
        "banner_style": "Banner Style",
        "online_mode": "Online Mode",
        "context_patcher": "Context Patcher",
        "language": "Language",
        "check_update": "Check Update",
        "auto": "Auto",
        "origin": "Original",
        "custom": "Custom",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "select_file": "Select File",
        "patch": "Patch",
        "back": "Back",
    },
    "Chinese": {
        "home": "主页",
        "settings": "设置",
        "about": "关于",
        "unpack": "解包",
        "pack": "打包",
        "plugins": "插件",
        "pack_rom": "打包ROM",
        "tools": "工具",
        "download": "下载",
        "new_project": "新建项目",
        "unpack_rom": "解包ROM",
        "download_rom": "下载ROM",
        "delete_project": "删除项目",
        "project_name": "项目名称",
        "enter_project_name": "输入项目名称:",
        "confirm_delete": "确定要删除吗",
        "yes": "是",
        "no": "否",
        "cancel": "取消",
        "ok": "确定",
        "refresh": "刷新",
        "unpack_selected": "解包选中",
        "unpack_all": "全部解包",
        "pack_selected": "打包选中",
        "pack_all": "全部打包",
        "pack_super": "打包Super",
        "pack_payload": "打包Payload",
        "output_format": "输出格式",
        "filesystem": "文件系统",
        "install_mpk": "安装MPK",
        "uninstall": "卸载",
        "run": "运行",
        "magisk_patcher": "Magisk修补",
        "disable_avb": "禁用AVB",
        "disable_encryption": "禁用加密",
        "console": "控制台",
        "clear_console": "清除",
        "running": "运行中...",
        "completed": "完成",
        "error": "错误",
        "no_projects": "未找到项目。创建新项目或解包ROM。",
        "drag_drop_hint": "拖拽ROM文件到此处或点击浏览",
        "packaging_settings": "打包设置",
        "dynamic_partition_settings": "动态分区设置",
        "tool_settings": "工具设置",
        "brotli_level": "Brotli压缩等级",
        "select_file": "选择文件",
        "patch": "修补",
        "back": "返回",
    },
}


class I18n:
    """Internationalization helper for GUI strings."""

    def __init__(self, language="English"):
        self.language = language
        self._gui_dict = {}
        self._cli_dict = {}
        self.set_language(language)

    def set_language(self, language):
        self.language = language
        self._gui_dict = GUI_STRINGS.get(language, GUI_STRINGS["English"])
        if hasattr(languages, language):
            self._cli_dict = getattr(languages, language)
        else:
            self._cli_dict = {}

    def get(self, key, fallback=None):
        """Get a GUI string by key."""
        return self._gui_dict.get(key, fallback or key)

    def translate(self, text):
        """Translate a CLI string using the language dictionary."""
        t = self._cli_dict.get(text, text)
        if t != text:
            return t
        for k, v in self._cli_dict.items():
            if k in text:
                text = text.replace(k, v)
        return text

    @staticmethod
    def available_languages():
        """Get list of available languages."""
        return [
            lang for lang in dir(languages)
            if not lang.startswith("_") and not lang.endswith("_") and lang != "default"
        ]
