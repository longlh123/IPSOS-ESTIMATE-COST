from PySide6.QtCore import QObject, QEvent
from PySide6.QtCore import Qt

"""

Chặn sự kiện wheel cho QSpinBox và QComboBox khi không có focus

"""
class WheelBlocker(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            if not obj.hasFocus():
                return True  # Block wheel scroll
        elif event.type() == QEvent.Enter:
            # Tắt focus khi chuột chỉ hover vào
            if not obj.hasFocus():
                obj.setFocusPolicy(Qt.ClickFocus)  # Chỉ focus khi click
        return super().eventFilter(obj, event)