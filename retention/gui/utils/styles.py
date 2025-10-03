from __future__ import annotations

"""Centralized Qt style helpers for Summit - AI Learning Accelerator."""

_MAIN_WINDOW_QSS = """
QWidget {
    background-color: transparent;
}

#surface {
    background-color: #ffffff;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
}

#appTitle {
    color: #0f172a;
    font-size: 16px;
    font-weight: 700;
}

#appSubtitle {
    color: #64748b;
    font-size: 11px;
}

#statusHeadline {
    color: #0f172a;
    font-size: 13px;
    font-weight: 600;
}

#statusDetail {
    color: #64748b;
    font-size: 11px;
}

#helperText {
    color: #94a3b8;
    font-size: 10px;
}

#outputHint {
    color: #0f172a;
    font-size: 11px;
    font-weight: 600;
}

QLabel#statusChip, QLabel#chip {
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 600;
    background-color: #e2e8f0;
    color: #475569;
}

QLabel#statusChip[state="idle"] {
    background-color: #e2e8f0;
    color: #475569;
}

QLabel#statusChip[state="recording"] {
    background-color: #fee2e2;
    color: #b91c1c;
}

QLabel#statusChip[state="processing"] {
    background-color: #dbeafe;
    color: #1d4ed8;
}

QLabel#statusChip[state="success"] {
    background-color: #dcfce7;
    color: #15803d;
}

QLabel#statusChip[state="warning"] {
    background-color: #fef3c7;
    color: #b45309;
}

QLabel#statusChip[state="error"] {
    background-color: #fee2e2;
    color: #b91c1c;
}

QLabel#statusChip[state="info"] {
    background-color: #ede9fe;
    color: #6d28d9;
}

QLabel#chip[state="success"] {
    background-color: #ecfdf3;
    color: #15803d;
}

QLabel#chip[state="warning"] {
    background-color: #fef3c7;
    color: #b45309;
}

QLabel#chip[state="info"] {
    background-color: #e0f2fe;
    color: #0369a1;
}

QLabel#chip[state="accent"] {
    background-color: #ede9fe;
    color: #6d28d9;
}

QLabel#chip[state="muted"] {
    background-color: #e2e8f0;
    color: #64748b;
}

#primaryButton {
    background-color: #111827;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
}

#primaryButton:hover {
    background-color: #0f172a;
}

#primaryButton:pressed {
    background-color: #0b1120;
}

#primaryButton:disabled {
    background-color: #94a3b8;
    color: #f1f5f9;
}

#secondaryButton {
    background-color: #f8fafc;
    color: #111827;
    border-radius: 12px;
    border: 1px solid #d8dee4;
    font-size: 13px;
    font-weight: 600;
}

#secondaryButton:hover {
    background-color: #f1f5f9;
}

#secondaryButton:pressed {
    background-color: #e2e8f0;
}

#secondaryButton:disabled {
    color: #94a3b8;
    border-color: #e2e8f0;
}

#iconButton {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 6px;
    min-width: 32px;
    min-height: 32px;
}

#iconButton:hover {
    background-color: #e2e8f0;
}

#validationDisplay {
    background-color: #f8fafc;
    border: 1px dashed #e2e8f0;
    border-radius: 12px;
    padding: 10px;
}
"""

_SETTINGS_DIALOG_QSS = """
QDialog {
    background-color: #ffffff;
}

#dialogTitle {
    color: #0f172a;
    font-size: 16px;
    font-weight: 700;
}

#dialogSubtitle {
    color: #64748b;
    font-size: 11px;
}

#apiKeyInput {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: #0f172a;
    background-color: #f8fafc;
    font-family: "Segoe UI", Arial, sans-serif;
}

#apiKeyInput:focus {
    border-color: #111827;
    background-color: #ffffff;
}

#hintLabel {
    color: #94a3b8;
    font-size: 10px;
}

#sectionLabel {
    color: #0f172a;
    font-size: 12px;
    font-weight: 600;
}

#toggleSwitch {
    width: 34px;
    height: 20px;
}

#toggleSwitch::indicator {
    width: 34px;
    height: 20px;
    border-radius: 10px;
    background-color: #e2e8f0;
    border: none;
}

#toggleSwitch::indicator:checked {
    background-color: #111827;
    background-position: right 4px center;
    background-repeat: no-repeat;
}

#toggleSwitch::indicator:unchecked {
    background-color: #e2e8f0;
    background-position: left 4px center;
    background-repeat: no-repeat;
}

#modeButton {
    background-color: #f8fafc;
    color: #111827;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
}

#modeButton:checked {
    background-color: #111827;
    color: #ffffff;
    border-color: #111827;
}

#modeButton:hover {
    background-color: #e2e8f0;
}

#primaryButton {
    background-color: #111827;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
}

#primaryButton:hover {
    background-color: #0f172a;
}

#primaryButton:pressed {
    background-color: #0b1120;
}
"""

_VALIDATION_DISPLAY_QSS = """
#validationRoot {
    background-color: transparent;
}

#infoLabel {
    color: #475569;
    font-size: 12px;
}

#statusRow {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    padding: 10px 12px;
}

#statusLabel {
    color: #1f2937;
    font-size: 12px;
    font-weight: 600;
}

#statusValue {
    color: #64748b;
    font-size: 11px;
}

#statusIndicator {
    border-radius: 5px;
    background-color: #cbd5f5;
}

#statusIndicator[state="pending"] {
    background-color: #cbd5f5;
}

#statusIndicator[state="success"] {
    background-color: #16a34a;
}

#statusIndicator[state="error"] {
    background-color: #dc2626;
}

#statusIndicator[state="warning"] {
    background-color: #f59e0b;
}

#validateButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 600;
}

#validateButton:disabled {
    background-color: #94a3b8;
}

#validateButton:hover:!disabled {
    background-color: #1d4ed8;
}
"""


def main_window_styles() -> str:
    """Return the QSS used by the main floating window."""
    return _MAIN_WINDOW_QSS


def settings_dialog_styles() -> str:
    """Return the QSS for the settings dialog."""
    return _SETTINGS_DIALOG_QSS


def validation_display_styles() -> str:
    """Return the QSS for the validation display panel."""
    return _VALIDATION_DISPLAY_QSS

