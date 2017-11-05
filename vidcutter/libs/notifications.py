#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#######################################################################
#
# VidCutter - media cutter & joiner
#
# copyright © 2017 Pete Alexandrou
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import os
import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QTimer, QUrl
from PyQt5.QtGui import QDesktopServices, QIcon, QMouseEvent, QPixmap
from PyQt5.QtWidgets import qApp, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class Notification(QDialog):
    shown = pyqtSignal()
    duration = 10

    def __init__(self, parent=None, f=Qt.Dialog | Qt.FramelessWindowHint):
        super(Notification, self).__init__(parent, f)
        self.parent = parent
        self.theme = self.parent.theme
        self.setObjectName('notification')
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(550)
        self._title, self._message = '', ''
        self.buttons = list()
        self.msgLabel = QLabel(self)
        self.msgLabel.setWordWrap(True)
        logo = QPixmap(82, 82)
        logo.load(':/images/vidcutter-small.png', 'PNG')
        logo_label = QLabel(self)
        logo_label.setPixmap(logo)
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(logo_label)
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.msgLabel)
        self.shown.connect(lambda: QTimer.singleShot(self.duration * 1000, self.fadeOut))
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addLayout(self.left_layout)
        layout.addSpacing(10)
        layout.addLayout(self.right_layout)
        layout.addStretch(1)
        self.setLayout(layout)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def message(self):
        return self._message
    
    @message.setter
    def message(self, value):
        self._message = value

    @pyqtSlot()
    def fadeOut(self):
        for step in range(100, 0, -10):
            self.setWindowOpacity(step / 100)
            qApp.processEvents()
            time.sleep(0.05)
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.fadeOut()

    # noinspection PyTypeChecker
    def showEvent(self, event):
        if self.isVisible():
            self.shown.emit()
        self.msgLabel.setText(self._message)
        [self.left_layout.addWidget(btn) for btn in self.buttons]
        super(Notification, self).showEvent(event)

    def closeEvent(self, event):
        self.deleteLater()


class JobCompleteNotification(Notification):
    def __init__(self, filename: str, filesize: str, runtime: str, parent=None):
        super(JobCompleteNotification, self).__init__(parent)
        pencolor = '#C681D5' if self.theme == 'dark' else '#642C68'
        self.filename = filename
        self.filesize = filesize
        self.runtime = runtime
        self.parent = parent
        self.title = 'Your media file is ready!'
        self.message = '''
    <style>
        h2 {{
            color: {labelscolor};
            font-family: "Futura-Light", sans-serif;
            font-weight: 500;
            text-align: center;
        }}
        table.info {{
            margin: 6px;
            padding: 4px 2px;
            font-family: "Noto Sans UI", sans-serif;
        }}
        td {{
            padding-top: 5px;
            vertical-align: top;
        }}
        td.label {{
            font-weight: bold;
            color: {labelscolor};
            text-transform: lowercase;
            text-align: right;
            padding-right: 5px;
            font-size: 14px;
        }}
        td.value {{
            color: {valuescolor};
            font-size: 14px;
        }}
    </style>
    <div style="margin:20px 10px 0;">
        <h2>{heading}</h2>
        <table border="0" class="info" cellpadding="2" cellspacing="0" align="left">
            <tr>
                <td width="20%%" class="label"><b>File:</b></td>
                <td width="80%%" class="value" nowrap>{filename}</td>
            </tr>
            <tr>
                <td width="20%%" class="label"><b>Size:</b></td>
                <td width="80%%" class="value">{filesize}</td>
            </tr>
            <tr>
                <td width="20%%" class="label"><b>Runtime:</b></td>
                <td width="80%%" class="value">{runtime}</td>
            </tr>
        </table>
    </div>'''.format(labelscolor=pencolor,
                     valuescolor=('#EFF0F1' if self.theme == 'dark' else '#222'),
                     heading=self._title,
                     filename=os.path.basename(self.filename),
                     filesize=self.filesize,
                     runtime=self.runtime)
        playButton = QPushButton(QIcon(':/images/complete-play.png'), 'Play', self)
        playButton.setFixedWidth(82)
        playButton.clicked.connect(self.playMedia)
        playButton.setCursor(Qt.PointingHandCursor)
        self.buttons.append(playButton)

    @pyqtSlot()
    def playMedia(self) -> None:
        if os.path.isfile(self.filename):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.filename))
