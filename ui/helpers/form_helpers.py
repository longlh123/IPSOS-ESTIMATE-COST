from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QHBoxLayout, QLineEdit, QComboBox, QTextEdit, QButtonGroup, QRadioButton, QSpinBox
from ui.widgets.multi_select import MultiSelectWidget
from ui.widgets.generic_editor_widget import GenericEditorWidget

def create_header_label(layout: QGridLayout, title, row=0, col=0, rowspan=1, colspan=1):
    container = QWidget()
    container_layout = QHBoxLayout(container)
    container_layout.setContentsMargins(0, 5, 0, 5)
    container_layout.setSpacing(10)

    label_widget = QLabel(title)
    label_widget.setStyleSheet("font-weight: bold;")

    container_layout.addWidget(label_widget)
    layout.addWidget(container, row, col, rowspan, colspan)

def create_input_field(layout: QGridLayout, target, field_name: str, label: str, row= 0, col= 0, rowspan=1, colspan=1, margins = None):
    if margins is None:
        margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}

    label_widget = QLabel(label)
    label_widget.setStyleSheet("margin-left: 10px;")
    layout.addWidget(label_widget, row, col)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(
        margins["left"], margins["top"], margins["right"], margins["bottom"]
    )

    input_widget = QLineEdit()
    container_layout.addWidget(input_widget)
    
    warning_label = QLabel("")
    warning_label.setStyleSheet("color: red; font-size: 12px;")
    warning_label.setVisible(False)

    container_layout.addWidget(warning_label)

    # Gán warning label thành thuộc tính self
    setattr(target, f"{field_name}_input", input_widget)
    setattr(target, f"{field_name}_warning", warning_label)

    layout.addWidget(container, row, col + 1, rowspan, colspan)

def create_textedit_field(layout: QGridLayout, target, field_name: str, label: str, placeholder="", row=0, col=0, rowspan=1, colspan=1, margins=None):
    if margins is None:
        margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}
    
    label_widget = QLabel(label)
    label_widget.setStyleSheet("margin-left: 10px;")
    layout.addWidget(label_widget, row, col, rowspan, colspan)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(
        margins["left"], margins["top"], margins["right"], margins["bottom"]
    )

    textedit_widget = QTextEdit()
    textedit_widget.setStyleSheet("margin-left: 10px;")
    textedit_widget.setPlaceholderText(placeholder)
    textedit_widget.setAcceptRichText(True)

    container_layout.addWidget(textedit_widget)

    warning_label = QLabel("")
    warning_label.setStyleSheet("color: red; font-size: 12px;")
    warning_label.setVisible(False)

    container_layout.addWidget(warning_label)

    # Gán warning label thành thuộc tính self
    setattr(target, f"{field_name}_textedit", textedit_widget)
    setattr(target, f"{field_name}_warning", warning_label)

    layout.addWidget(container, row + 1, col, rowspan, colspan)

def create_combobox(layout: QGridLayout, target, field_name: str, label: str, items: list, current_index=0, row= 0, col= 0, rowspan=1, colspan=1, margins = None):
    if margins is None:
        margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}

    label_widget = QLabel(label)
    label_widget.setStyleSheet("margin-left: 10px;")
    layout.addWidget(label_widget, row, col)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(
        margins["left"], margins["top"], margins["right"], margins["bottom"]
    )

    combobox_widget = QComboBox()
    combobox_widget.addItem("-- Select --")
    combobox_widget.addItems(items)
    
    # Set item đầu tiên là mặc định
    combobox_widget.setCurrentIndex(current_index)

    # Set item đầu tiên là không thể chọn
    combobox_widget.model().item(0).setEnabled(False)

    container_layout.addWidget(combobox_widget)

    warning_label = QLabel("")
    warning_label.setStyleSheet("color: red; font-size: 12px")
    warning_label.setVisible(False)

    container_layout.addWidget(warning_label)

    # Gán warning label thành thuộc tính self
    setattr(target, f"{field_name}_combobox", combobox_widget)
    setattr(target, f"{field_name}_warning", warning_label)

    layout.addWidget(container, row, col + 1, rowspan, colspan)

def create_multiselected_field(layout: QGridLayout, target, field_name: str, label: str, items: list, allow_adding=False, row=0, col=0, rowspan=1, colspan=1, margins=None):
    if margins is None:
        margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}

    label_widget = QLabel(label)
    label_widget.setStyleSheet("margin-left: 10px;")
    layout.addWidget(label_widget, row, col)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(
        margins["left"], margins["top"], margins["right"], margins["bottom"]
    )

    multiselected_widget = MultiSelectWidget(items, allow_adding=allow_adding)    
    container_layout.addWidget(multiselected_widget)

    warning_label = QLabel("")
    warning_label.setStyleSheet("color: red; font-size: 12px")
    warning_label.setVisible(False)

    container_layout.addWidget(warning_label)

    # Gán warning label thành thuộc tính self
    setattr(target, f"{field_name}_multiselecttion", multiselected_widget)
    setattr(target, f"{field_name}_warning", warning_label)

    layout.addWidget(container, row, col + 1, rowspan, colspan)

def create_generic_editor_field(layout: QGridLayout, target, field_name: str, label: str, title: str, field_config: list, row=0, col=0, rowspan=1, colspan=1, margins=None):
    if margins is None:
        margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}
    
    label_widget = QLabel(label)
    label_widget.setStyleSheet("margin-left: 10px;")
    layout.addWidget(label_widget, row, col)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(
        margins["left"], margins["top"], margins["right"], margins["bottom"]
    )

    generic_editor_widget = GenericEditorWidget(
            title=title,
            field_config = field_config
        )

    container_layout.addWidget(generic_editor_widget)

    warning_label = QLabel("")
    warning_label.setStyleSheet("color: red; font-size: 12px")
    warning_label.setVisible(False)

    container_layout.addWidget(warning_label)

    # Gán warning label thành thuộc tính self
    setattr(target, f"{field_name}_generic_editor", generic_editor_widget)
    setattr(target, f"{field_name}_warning", warning_label)

    layout.addWidget(container, row, col + 1, rowspan, colspan)

def create_radiobuttons_group(layout: QGridLayout, target, field_name: str, label: str, radio_items: list, row=0, col=0, rowspan=1, colspan=1, margins=None):
    """
    radio_items = [
            { 'name': 'ifield', 'label': 'iField', 'checked': True},
            { 'name': 'dimension', 'label': 'Dimension', 'checked': False}
        ]
    """
    if margins is None:
        margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}
    
    label_widget = QLabel(label)
    label_widget.setStyleSheet("margin-left: 10px;")
    layout.addWidget(label_widget, row, col)

    container = QWidget()
    container_layout = QHBoxLayout(container)
    container_layout.setContentsMargins(
        margins.get('left', 0),
        margins.get('top', 0),
        margins.get('right', 0),
        margins.get('bottom', 0)
    )

    radio_group = QButtonGroup(target)
    
    for i, item in enumerate(radio_items):
        radio_item = QRadioButton(item.get('label'))
        radio_group.addButton(radio_item, i)

        radio_item.setChecked(item.get('checked', False))

        container_layout.addWidget(radio_item)

        setattr(target, f"{item.get('name')}_radioitem", radio_item)
    
    container_layout.addStretch()

    setattr(target, f"{field_name}_radiogroup", radio_group)

    layout.addWidget(container, row, col + 1, rowspan, colspan)

def create_spinbox_field(layout: QGridLayout, target, field_name: str, label: str, range=(0, 999), value=None, suffix="", row=0, col=0, rowspan=1, colspan=1, margins=None):
    if margins is None:
        margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}
    
    label_widget = QLabel(label)
    label_widget.setStyleSheet("margin-left: 10px;")
    layout.addWidget(label_widget, row, col)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(
        margins.get('left', 0),
        margins.get('top', 0),
        margins.get('right', 0),
        margins.get('bottom', 0)
    )

    spinbox_widget = QSpinBox()
    spinbox_widget.setRange(range[0], range[1])
    spinbox_widget.setSuffix(suffix)

    if value is not None:
        spinbox_widget.setValue(value)

    container_layout.addWidget(spinbox_widget)

    warning_label = QLabel()
    warning_label.setStyleSheet("color: red; font-size: 12px")
    warning_label.setVisible(False)

    container_layout.addWidget(warning_label)

    setattr(target, f"{field_name}_spinbox", spinbox_widget)
    setattr(target, f"{field_name}_warning", warning_label)

    layout.addWidget(container, row, col + 1, rowspan, colspan)