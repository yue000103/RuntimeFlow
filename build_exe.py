"""
PyInstaller 打包脚本
生成 Windows 独立可执行文件 runtimeflow.exe

使用方法:
    pip install pyinstaller
    python build_exe.py

生成文件: dist/runtimeflow.exe
"""
import PyInstaller.__main__

PyInstaller.__main__.run([
    'runtimeflow/__main__.py',
    '--name=runtimeflow',
    '--onefile',
    '--console',  # 保留控制台窗口以显示输出
    '--add-data=runtimeflow;runtimeflow',
    '--hidden-import=pynput',
    '--hidden-import=pyautogui',
    '--hidden-import=win32gui',
    '--hidden-import=click',
])
