from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,
    Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget,
    QStyleOptionComboBox, QStyle)

class RIScontroller_ui(object):
    def setupUi(self, RIScontroller):
        if not RIScontroller.objectName():
            RIScontroller.setObjectName(u"RIScontroller")
        RIScontroller.resize(800, 600)
        RIScontroller.setMinimumSize(QSize(800, 600))
        self.horizontalLayout_3 = QHBoxLayout(RIScontroller)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalFrame = QFrame(RIScontroller)
        self.verticalFrame.setObjectName(u"verticalFrame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalFrame.sizePolicy().hasHeightForWidth())
        self.verticalFrame.setSizePolicy(sizePolicy)
        self.verticalFrame.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.verticalFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.GB_buttons = QGroupBox(self.verticalFrame)
        self.GB_buttons.setObjectName(u"GB_buttons")
        self.verticalLayout = QVBoxLayout(self.GB_buttons)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.PB_connect = QPushButton(self.GB_buttons)
        self.PB_connect.setObjectName(u"PB_connect")

        self.verticalLayout.addWidget(self.PB_connect)

        self.PB_disconnect = QPushButton(self.GB_buttons)
        self.PB_disconnect.setObjectName(u"PB_disconnect")
        self.PB_disconnect.setEnabled(False)

        self.verticalLayout.addWidget(self.PB_disconnect)

        self.PB_reset = QPushButton(self.GB_buttons)
        self.PB_reset.setObjectName(u"PB_reset")
        self.PB_reset.setEnabled(False)

        self.verticalLayout.addWidget(self.PB_reset)

        self.PB_readVoltage = QPushButton(self.GB_buttons)
        self.PB_readVoltage.setObjectName(u"PB_readVoltage")
        self.PB_readVoltage.setEnabled(False)

        self.verticalLayout.addWidget(self.PB_readVoltage)

        self.PB_readpattern = QPushButton(self.GB_buttons)
        self.PB_readpattern.setObjectName(u"PB_readpattern")
        self.PB_readpattern.setEnabled(False)

        self.verticalLayout.addWidget(self.PB_readpattern)

        self.PB_readserial = QPushButton(self.GB_buttons)
        self.PB_readserial.setObjectName(u"PB_readserial")
        self.PB_readserial.setEnabled(False)

        self.verticalLayout.addWidget(self.PB_readserial)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.L_port = QLabel(self.GB_buttons)
        self.L_port.setObjectName(u"L_port")
        self.L_port.setMaximumSize(QSize(48, 24))
        self.L_port.setMargin(5)

        self.horizontalLayout.addWidget(self.L_port)

        self.CB_port = PortComboBox(self.GB_buttons)
        self.CB_port.addItem("DEMO")
        self.CB_port.setCurrentIndex(0)
        self.CB_port.setObjectName(u"CB_port")


        self.horizontalLayout.addWidget(self.CB_port)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.CB_Debug = QCheckBox(self.GB_buttons)
        self.CB_Debug.setObjectName(u"CB_Debug")
        self.CB_Debug.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.CB_Debug.setChecked(True)

        self.horizontalLayout_2.addWidget(self.CB_Debug)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.verticalLayout_2.addWidget(self.GB_buttons)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout_3.addWidget(self.verticalFrame)

        self.TE_Debug = QTextEdit(RIScontroller)
        self.TE_Debug.setObjectName(u"TE_Debug")
        self.TE_Debug.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.TE_Debug)


        self.retranslateUi(RIScontroller)

        QMetaObject.connectSlotsByName(RIScontroller)


    def retranslateUi(self, RIScontroller):
        RIScontroller.setWindowTitle(QCoreApplication.translate("RIScontroller", u"RIScontroller", None))
        self.GB_buttons.setTitle(QCoreApplication.translate("RIScontroller", u"Serial Communication", None))
        self.PB_connect.setText(QCoreApplication.translate("RIScontroller", u"connect", None))
        self.PB_disconnect.setText(QCoreApplication.translate("RIScontroller", u"disconnect", None))
        self.PB_reset.setText(QCoreApplication.translate("RIScontroller", u"reset", None))
        self.PB_readVoltage.setText(QCoreApplication.translate("RIScontroller", u"read RIS voltage", None))
        self.PB_readpattern.setText(QCoreApplication.translate("RIScontroller", u"read Pattern", None))
        self.PB_readserial.setText(QCoreApplication.translate("RIScontroller", u"read serial number", None))
        self.L_port.setText(QCoreApplication.translate("RIScontroller", u"Port:", None))
        self.CB_port.setItemText(0, QCoreApplication.translate("RIScontroller", u"DEMO", None))

        self.CB_Debug.setText(QCoreApplication.translate("RIScontroller", u"Debugmode:", None))



class PortComboBox(QComboBox):
    popupAboutToBeShown = Signal()  # custom Signal

    def __init__(self, parent=None):
        super().__init__(parent)

    def showPopup(self):
        self.popupAboutToBeShown.emit()  # send custom signal before pop-up menu is shown
        super().showPopup()