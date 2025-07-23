from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from app.ui.connect_to_server import ConnectToServerWindow


def test_campos_vazios(qtbot):
    window = ConnectToServerWindow()
    qtbot.addWidget(window)

    assert not window.username_input.text()
    assert not window.server_address_input.text()


def test_mostra_alerta_se_campos_vazios(qtbot, monkeypatch):
    window = ConnectToServerWindow()
    qtbot.addWidget(window)

    exibido = {'foi_exibido': False}

    # Intercepta o método exec() da QMessageBox
    def fake_exec(self):
        exibido['foi_exibido'] = True
        return QMessageBox.Ok  # Simula que o usuário clicou em OK

    monkeypatch.setattr(QMessageBox, 'exec', fake_exec)

    # Garante que os campos estão vazios
    window.username_input.setText('')
    window.server_address_input.setText('')

    qtbot.mouseClick(window.connect_button, Qt.LeftButton)

    assert exibido['foi_exibido'] is True
