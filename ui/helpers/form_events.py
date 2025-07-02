from PySide6.QtWidgets import QMessageBox

def bind_input_handler(target, field_name: str, validator=None, update_func=None):
    """
    Tự động xử lý sự kiện khi input text thay đổi:
    - Validate
    - Hiển thị warning
    - Gọi update_func nếu hợp lệ
    """
    field_widget = getattr(target, f"{field_name}_input", None)
    warning_label = getattr(target, f"{field_name}_warning", None)

    if field_widget is None:
        raise ValueError(f"Không tìm thấy field '{field_name}' trong {target}")
    
    def on_text_changed(value: str):
        is_valid, error_msg = validator.validate(field_name, value) if validator else (True, "")

        if warning_label:
            if not is_valid:
                warning_label.setText(error_msg)
                warning_label.show()
            else:
                warning_label.hide()

        if is_valid and update_func:
            update_func(field_name, value)
        
    field_widget.textChanged.connect(on_text_changed)

def bind_textedit_handler(target, field_name: str, validator=None, update_func=None):
    """
    Tự động xử lý sự kiện khi input text thay đổi:
    - Validate
    - Hiển thị warning
    - Gọi update_func nếu hợp lệ
    """
    field_widget = getattr(target, f"{field_name}_textedit", None)
    warning_label = getattr(target, f"{field_name}_warning", None)

    if field_widget is None:
        raise ValueError(f"Không tìm thấy field '{field_name}' trong {target}")
    
    def on_text_changed():
        value = field_widget.toPlainText()
        is_valid, error_msg = validator.validate(field_name, value) if validator else (True, "")

        if warning_label:
            if not is_valid:
                warning_label.setText(error_msg)
                warning_label.show()
            else:
                warning_label.hide()

        if is_valid and update_func:
            update_func(field_name, value)
        
    field_widget.textChanged.connect(on_text_changed)

def bind_combobox_handler(target, field_name: str, validator=None, update_func=None):
    """
    Tự động xử lý sự kiện khi input text thay đổi:
    - Validate
    - Hiển thị warning
    - Gọi update_func nếu hợp lệ
    """
    field_widget = getattr(target, f"{field_name}_combobox", None)
    warning_label = getattr(target, f"{field_name}_warning", None)

    if field_widget is None:
        raise ValueError(f"Không tìm thấy field '{field_name}' trong {target}")
    
    def on_current_text_changed(value: str):
        is_valid, error_msg = validator.validate(field_name, value) if validator else (True, "")

        if warning_label:
            if not is_valid:
                warning_label.setText(error_msg)
                warning_label.show()
            else:
                warning_label.hide()

        if is_valid and update_func:
            update_func(field_name, value)
    
    field_widget.currentTextChanged.connect(on_current_text_changed)

def bind_multiselection_handler(target, field_name: str, validator=None, update_func=None):
    """
    Tự động xử lý sự kiện khi input text thay đổi:
    - Validate
    - Hiển thị warning
    - Gọi update_func nếu hợp lệ
    """
    field_widget = getattr(target, f"{field_name}_multiselecttion", None)
    warning_label = getattr(target, f"{field_name}_warning", None)

    if field_widget is None:
        raise ValueError(f"Không tìm thấy field '{field_name}' trong {target}")
    
    def on_selection_changed(items: list):
        is_valid, error_msg = validator.validate(field_name, items) if validator else (True, "")

        if warning_label:
            if not is_valid:
                warning_label.setText(error_msg)
                warning_label.show()
            else:
                warning_label.hide()

        if is_valid and update_func:
            update_func(field_name, items)
    
    field_widget.selectionChanged.connect(on_selection_changed)

def bind_radiogroup_handler(target, field_name: str, update_func=None):
    field_widget = getattr(target, f"{field_name}_radiogroup", None)

    def on_button_clicked(button):
        if update_func:
            value = button.text()
            update_func(field_name, value)

    field_widget.buttonClicked.connect(on_button_clicked)

def bind_spinbox_handler(target, field_name: str, validator=None, update_func=None):
    """
    Tự động xử lý sự kiện khi input text thay đổi:
    - Validate
    - Hiển thị warning
    - Gọi update_func nếu hợp lệ
    """
    field_widget = getattr(target, f"{field_name}_spinbox", None)
    warning_label = getattr(target, f"{field_name}_warning", None)

    if field_widget is None:
        raise ValueError(f"Không tìm thấy field '{field_name}' trong {target}")
    
    def on_value_changed(value: str):
        is_valid, error_msg = validator.validate(field_name, value)

        if warning_label:
            if not is_valid:
                warning_label.setText(error_msg)
                warning_label.show()
            else:
                warning_label.hide()

        if is_valid and update_func:
            update_func(field_name, value)
        
    field_widget.valueChanged.connect(on_value_changed)