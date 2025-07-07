# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(780, 579)
        self.actionSpeichern = QAction(MainWindow)
        self.actionSpeichern.setObjectName(u"actionSpeichern")
        self.action_ffnen = QAction(MainWindow)
        self.action_ffnen.setObjectName(u"action_ffnen")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.RIS_tab = QWidget()
        self.RIS_tab.setObjectName(u"RIS_tab")
        self.tabWidget.addTab(self.RIS_tab, "")
        self.config_tab = QWidget()
        self.config_tab.setObjectName(u"config_tab")
        self.frame = QFrame(self.config_tab)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 10, 135, 147))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setLineWidth(2)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.PB_on = QPushButton(self.groupBox)
        self.PB_on.setObjectName(u"PB_on")

        self.verticalLayout.addWidget(self.PB_on)

        self.PB_off = QPushButton(self.groupBox)
        self.PB_off.setObjectName(u"PB_off")

        self.verticalLayout.addWidget(self.PB_off)

        self.PB_invert = QPushButton(self.groupBox)
        self.PB_invert.setObjectName(u"PB_invert")

        self.verticalLayout.addWidget(self.PB_invert)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.PB_update_RIS = QPushButton(self.config_tab)
        self.PB_update_RIS.setObjectName(u"PB_update_RIS")
        self.PB_update_RIS.setGeometry(QRect(200, 60, 80, 24))
        self.tabWidget.addTab(self.config_tab, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 780, 21))
        self.menuDatei = QMenu(self.menubar)
        self.menuDatei.setObjectName(u"menuDatei")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuDatei.menuAction())
        self.menuDatei.addAction(self.action_ffnen)
        self.menuDatei.addAction(self.actionSpeichern)
        self.menuDatei.addSeparator()

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Reconfigurable Intelligent Surface - RIS", None))
        self.actionSpeichern.setText(QCoreApplication.translate("MainWindow", u"Speichern", None))
        self.action_ffnen.setText(QCoreApplication.translate("MainWindow", u"\u00d6ffnen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.RIS_tab), QCoreApplication.translate("MainWindow", u"RIS", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"RIS schalten", None))
        self.PB_on.setText(QCoreApplication.translate("MainWindow", u"alle an", None))
        self.PB_off.setText(QCoreApplication.translate("MainWindow", u"alle aus", None))
        self.PB_invert.setText(QCoreApplication.translate("MainWindow", u"alle invertieren", None))
        self.PB_update_RIS.setText(QCoreApplication.translate("MainWindow", u"update RIS", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.config_tab), QCoreApplication.translate("MainWindow", u"Konfiguration", None))
        self.menuDatei.setTitle(QCoreApplication.translate("MainWindow", u"Datei", None))
    # retranslateUi

