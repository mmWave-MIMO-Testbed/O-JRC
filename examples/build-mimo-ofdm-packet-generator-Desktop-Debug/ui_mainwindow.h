/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 5.12.8
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QFormLayout>
#include <QtWidgets/QFrame>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralWidget;
    QGridLayout *gridLayout_4;
    QSpacerItem *horizontalSpacer_8;
    QSpacerItem *horizontalSpacer_7;
    QGroupBox *groupBox;
    QGridLayout *gridLayout_7;
    QSpacerItem *horizontalSpacer_3;
    QSpacerItem *horizontalSpacer_4;
    QSpacerItem *verticalSpacer_10;
    QSpacerItem *verticalSpacer_12;
    QGroupBox *parameterGroup;
    QGridLayout *gridLayout;
    QSpacerItem *horizontalSpacer_5;
    QSpacerItem *horizontalSpacer_6;
    QFormLayout *formLayout;
    QSpacerItem *verticalSpacer;
    QLabel *label_9;
    QLineEdit *dataCarrierInput;
    QLabel *label_5;
    QComboBox *mcsSelect;
    QLabel *label_3;
    QLabel *label_4;
    QLineEdit *cpPrefixInput;
    QLineEdit *fftLengthInput;
    QLabel *label_10;
    QLineEdit *txAntennaInput;
    QLabel *label_12;
    QLineEdit *bandwidthInput;
    QGroupBox *gnuSocketGroup;
    QGridLayout *gridLayout_2;
    QSpacerItem *horizontalSpacer;
    QFormLayout *formLayout_2;
    QLineEdit *udpPortInput;
    QLabel *label_6;
    QSpacerItem *verticalSpacer_4;
    QSpacerItem *horizontalSpacer_2;
    QSpacerItem *horizontalSpacer_9;
    QGroupBox *RateBox;
    QGridLayout *gridLayout_3;
    QGridLayout *gridLayout_11;
    QLabel *label_14;
    QLabel *label_13;
    QLabel *currentRateLabel;
    QLabel *label_11;
    QLabel *maximumRateLabel;
    QLabel *txDurationLabel;
    QGroupBox *pduGeneratorGroup;
    QGridLayout *gridLayout_8;
    QSpacerItem *verticalSpacer_2;
    QSpacerItem *verticalSpacer_3;
    QGroupBox *videoTxGroup;
    QGridLayout *gridLayout_6;
    QFormLayout *formLayout_3;
    QLabel *label_7;
    QComboBox *cameraSelect;
    QPushButton *cameraConnectButton;
    QPushButton *videoTxButton;
    QSpacerItem *horizontalSpacer_11;
    QGroupBox *txParamGroup;
    QGridLayout *gridLayout_10;
    QGridLayout *gridLayout_9;
    QFormLayout *formLayout_5;
    QLabel *dataIntervalLabel;
    QLineEdit *dataIntervalInput;
    QLabel *dataSizeLabel;
    QLineEdit *dataSizeInput;
    QLabel *ndpIntervalLabel;
    QLineEdit *ndpIntervalInput;
    QFrame *line_3;
    QSpacerItem *verticalSpacer_6;
    QGroupBox *txModeGroup;
    QVBoxLayout *verticalLayout_8;
    QVBoxLayout *verticalLayout_7;
    QHBoxLayout *horizontalLayout_2;
    QRadioButton *ndpButton;
    QRadioButton *dataButton;
    QRadioButton *comboButton;
    QSpacerItem *horizontalSpacer_10;
    QPushButton *startButton;
    QButtonGroup *txButtonGroup;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(960, 555);
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(MainWindow->sizePolicy().hasHeightForWidth());
        MainWindow->setSizePolicy(sizePolicy);
        centralWidget = new QWidget(MainWindow);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        QSizePolicy sizePolicy1(QSizePolicy::Fixed, QSizePolicy::Fixed);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(centralWidget->sizePolicy().hasHeightForWidth());
        centralWidget->setSizePolicy(sizePolicy1);
        gridLayout_4 = new QGridLayout(centralWidget);
        gridLayout_4->setSpacing(6);
        gridLayout_4->setContentsMargins(11, 11, 11, 11);
        gridLayout_4->setObjectName(QString::fromUtf8("gridLayout_4"));
        gridLayout_4->setSizeConstraint(QLayout::SetDefaultConstraint);
        horizontalSpacer_8 = new QSpacerItem(10, 20, QSizePolicy::Maximum, QSizePolicy::Minimum);

        gridLayout_4->addItem(horizontalSpacer_8, 0, 0, 1, 1);

        horizontalSpacer_7 = new QSpacerItem(10, 20, QSizePolicy::Maximum, QSizePolicy::Minimum);

        gridLayout_4->addItem(horizontalSpacer_7, 0, 2, 1, 1);

        groupBox = new QGroupBox(centralWidget);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        QFont font;
        font.setFamily(QString::fromUtf8("Ubuntu"));
        font.setPointSize(16);
        font.setBold(false);
        font.setWeight(50);
        groupBox->setFont(font);
        groupBox->setStyleSheet(QString::fromUtf8("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 5px;\n"
"    margin-top: 0.6em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
"}"));
        gridLayout_7 = new QGridLayout(groupBox);
        gridLayout_7->setSpacing(6);
        gridLayout_7->setContentsMargins(11, 11, 11, 11);
        gridLayout_7->setObjectName(QString::fromUtf8("gridLayout_7"));
        horizontalSpacer_3 = new QSpacerItem(10, 10, QSizePolicy::Minimum, QSizePolicy::Minimum);

        gridLayout_7->addItem(horizontalSpacer_3, 1, 0, 1, 1);

        horizontalSpacer_4 = new QSpacerItem(10, 20, QSizePolicy::Minimum, QSizePolicy::Minimum);

        gridLayout_7->addItem(horizontalSpacer_4, 1, 2, 1, 1);

        verticalSpacer_10 = new QSpacerItem(20, 5, QSizePolicy::Minimum, QSizePolicy::MinimumExpanding);

        gridLayout_7->addItem(verticalSpacer_10, 2, 1, 1, 1);

        verticalSpacer_12 = new QSpacerItem(20, 2, QSizePolicy::Minimum, QSizePolicy::Minimum);

        gridLayout_7->addItem(verticalSpacer_12, 0, 1, 1, 1);

        parameterGroup = new QGroupBox(groupBox);
        parameterGroup->setObjectName(QString::fromUtf8("parameterGroup"));
        parameterGroup->setEnabled(true);
        QFont font1;
        font1.setPointSize(14);
        parameterGroup->setFont(font1);
        parameterGroup->setStyleSheet(QString::fromUtf8("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 5px;\n"
"    margin-top: 0.6em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
"}"));
        parameterGroup->setFlat(true);
        gridLayout = new QGridLayout(parameterGroup);
        gridLayout->setSpacing(6);
        gridLayout->setContentsMargins(11, 11, 11, 11);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        horizontalSpacer_5 = new QSpacerItem(10, 20, QSizePolicy::Maximum, QSizePolicy::Minimum);

        gridLayout->addItem(horizontalSpacer_5, 0, 0, 1, 1);

        horizontalSpacer_6 = new QSpacerItem(10, 20, QSizePolicy::Maximum, QSizePolicy::Minimum);

        gridLayout->addItem(horizontalSpacer_6, 0, 2, 1, 1);

        formLayout = new QFormLayout();
        formLayout->setSpacing(6);
        formLayout->setObjectName(QString::fromUtf8("formLayout"));
        verticalSpacer = new QSpacerItem(20, 5, QSizePolicy::Minimum, QSizePolicy::Maximum);

        formLayout->setItem(0, QFormLayout::LabelRole, verticalSpacer);

        label_9 = new QLabel(parameterGroup);
        label_9->setObjectName(QString::fromUtf8("label_9"));
        QFont font2;
        font2.setPointSize(12);
        label_9->setFont(font2);

        formLayout->setWidget(3, QFormLayout::LabelRole, label_9);

        dataCarrierInput = new QLineEdit(parameterGroup);
        dataCarrierInput->setObjectName(QString::fromUtf8("dataCarrierInput"));
        dataCarrierInput->setFont(font2);
        dataCarrierInput->setInputMethodHints(Qt::ImhPreferNumbers);
        dataCarrierInput->setReadOnly(true);

        formLayout->setWidget(3, QFormLayout::FieldRole, dataCarrierInput);

        label_5 = new QLabel(parameterGroup);
        label_5->setObjectName(QString::fromUtf8("label_5"));
        label_5->setFont(font2);

        formLayout->setWidget(6, QFormLayout::LabelRole, label_5);

        mcsSelect = new QComboBox(parameterGroup);
        mcsSelect->addItem(QString());
        mcsSelect->addItem(QString());
        mcsSelect->addItem(QString());
        mcsSelect->addItem(QString());
        mcsSelect->addItem(QString());
        mcsSelect->addItem(QString());
        mcsSelect->setObjectName(QString::fromUtf8("mcsSelect"));
        mcsSelect->setFont(font2);

        formLayout->setWidget(6, QFormLayout::FieldRole, mcsSelect);

        label_3 = new QLabel(parameterGroup);
        label_3->setObjectName(QString::fromUtf8("label_3"));
        label_3->setFont(font2);

        formLayout->setWidget(1, QFormLayout::LabelRole, label_3);

        label_4 = new QLabel(parameterGroup);
        label_4->setObjectName(QString::fromUtf8("label_4"));
        label_4->setFont(font2);

        formLayout->setWidget(2, QFormLayout::LabelRole, label_4);

        cpPrefixInput = new QLineEdit(parameterGroup);
        cpPrefixInput->setObjectName(QString::fromUtf8("cpPrefixInput"));
        cpPrefixInput->setFont(font2);

        formLayout->setWidget(2, QFormLayout::FieldRole, cpPrefixInput);

        fftLengthInput = new QLineEdit(parameterGroup);
        fftLengthInput->setObjectName(QString::fromUtf8("fftLengthInput"));
        fftLengthInput->setFont(font2);

        formLayout->setWidget(1, QFormLayout::FieldRole, fftLengthInput);

        label_10 = new QLabel(parameterGroup);
        label_10->setObjectName(QString::fromUtf8("label_10"));
        QFont font3;
        font3.setFamily(QString::fromUtf8("Ubuntu"));
        font3.setPointSize(12);
        label_10->setFont(font3);

        formLayout->setWidget(4, QFormLayout::LabelRole, label_10);

        txAntennaInput = new QLineEdit(parameterGroup);
        txAntennaInput->setObjectName(QString::fromUtf8("txAntennaInput"));
        txAntennaInput->setFont(font2);

        formLayout->setWidget(4, QFormLayout::FieldRole, txAntennaInput);

        label_12 = new QLabel(parameterGroup);
        label_12->setObjectName(QString::fromUtf8("label_12"));
        label_12->setFont(font2);

        formLayout->setWidget(5, QFormLayout::LabelRole, label_12);

        bandwidthInput = new QLineEdit(parameterGroup);
        bandwidthInput->setObjectName(QString::fromUtf8("bandwidthInput"));
        bandwidthInput->setFont(font2);

        formLayout->setWidget(5, QFormLayout::FieldRole, bandwidthInput);


        gridLayout->addLayout(formLayout, 0, 1, 1, 1);


        gridLayout_7->addWidget(parameterGroup, 1, 1, 1, 1);

        gnuSocketGroup = new QGroupBox(groupBox);
        gnuSocketGroup->setObjectName(QString::fromUtf8("gnuSocketGroup"));
        gnuSocketGroup->setFont(font1);
        gnuSocketGroup->setStyleSheet(QString::fromUtf8("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 5px;\n"
"    margin-top: 0.6em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
"}"));
        gridLayout_2 = new QGridLayout(gnuSocketGroup);
        gridLayout_2->setSpacing(6);
        gridLayout_2->setContentsMargins(11, 11, 11, 11);
        gridLayout_2->setObjectName(QString::fromUtf8("gridLayout_2"));
        horizontalSpacer = new QSpacerItem(10, 20, QSizePolicy::Maximum, QSizePolicy::Minimum);

        gridLayout_2->addItem(horizontalSpacer, 0, 0, 1, 1);

        formLayout_2 = new QFormLayout();
        formLayout_2->setSpacing(6);
        formLayout_2->setObjectName(QString::fromUtf8("formLayout_2"));
        udpPortInput = new QLineEdit(gnuSocketGroup);
        udpPortInput->setObjectName(QString::fromUtf8("udpPortInput"));
        udpPortInput->setFont(font1);
        udpPortInput->setInputMethodHints(Qt::ImhPreferNumbers);
        udpPortInput->setEchoMode(QLineEdit::Normal);

        formLayout_2->setWidget(1, QFormLayout::FieldRole, udpPortInput);

        label_6 = new QLabel(gnuSocketGroup);
        label_6->setObjectName(QString::fromUtf8("label_6"));
        label_6->setFont(font1);

        formLayout_2->setWidget(1, QFormLayout::LabelRole, label_6);

        verticalSpacer_4 = new QSpacerItem(20, 10, QSizePolicy::Minimum, QSizePolicy::Preferred);

        formLayout_2->setItem(0, QFormLayout::FieldRole, verticalSpacer_4);


        gridLayout_2->addLayout(formLayout_2, 0, 1, 1, 1);

        horizontalSpacer_2 = new QSpacerItem(10, 20, QSizePolicy::Maximum, QSizePolicy::Minimum);

        gridLayout_2->addItem(horizontalSpacer_2, 0, 2, 1, 1);


        gridLayout_7->addWidget(gnuSocketGroup, 3, 1, 1, 1);


        gridLayout_4->addWidget(groupBox, 0, 1, 1, 1);

        horizontalSpacer_9 = new QSpacerItem(10, 20, QSizePolicy::Maximum, QSizePolicy::Minimum);

        gridLayout_4->addItem(horizontalSpacer_9, 0, 4, 1, 1);

        RateBox = new QGroupBox(centralWidget);
        RateBox->setObjectName(QString::fromUtf8("RateBox"));
        QSizePolicy sizePolicy2(QSizePolicy::Preferred, QSizePolicy::Preferred);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(RateBox->sizePolicy().hasHeightForWidth());
        RateBox->setSizePolicy(sizePolicy2);
        RateBox->setMaximumSize(QSize(16777215, 80));
        RateBox->setFont(font1);
        RateBox->setStyleSheet(QString::fromUtf8("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 5px;\n"
"    margin-top: 0.6em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
"}"));
        gridLayout_3 = new QGridLayout(RateBox);
        gridLayout_3->setSpacing(6);
        gridLayout_3->setContentsMargins(11, 11, 11, 11);
        gridLayout_3->setObjectName(QString::fromUtf8("gridLayout_3"));
        gridLayout_11 = new QGridLayout();
        gridLayout_11->setSpacing(6);
        gridLayout_11->setObjectName(QString::fromUtf8("gridLayout_11"));
        gridLayout_11->setSizeConstraint(QLayout::SetMinimumSize);
        gridLayout_11->setVerticalSpacing(6);
        label_14 = new QLabel(RateBox);
        label_14->setObjectName(QString::fromUtf8("label_14"));
        QFont font4;
        font4.setPointSize(13);
        label_14->setFont(font4);

        gridLayout_11->addWidget(label_14, 1, 0, 1, 1);

        label_13 = new QLabel(RateBox);
        label_13->setObjectName(QString::fromUtf8("label_13"));
        label_13->setFont(font4);

        gridLayout_11->addWidget(label_13, 0, 2, 1, 1);

        currentRateLabel = new QLabel(RateBox);
        currentRateLabel->setObjectName(QString::fromUtf8("currentRateLabel"));
        QFont font5;
        font5.setFamily(QString::fromUtf8("DejaVu Sans Mono"));
        font5.setPointSize(13);
        currentRateLabel->setFont(font5);

        gridLayout_11->addWidget(currentRateLabel, 0, 1, 1, 1);

        label_11 = new QLabel(RateBox);
        label_11->setObjectName(QString::fromUtf8("label_11"));
        label_11->setFont(font4);

        gridLayout_11->addWidget(label_11, 0, 0, 1, 1);

        maximumRateLabel = new QLabel(RateBox);
        maximumRateLabel->setObjectName(QString::fromUtf8("maximumRateLabel"));
        maximumRateLabel->setFont(font5);

        gridLayout_11->addWidget(maximumRateLabel, 0, 3, 1, 1);

        txDurationLabel = new QLabel(RateBox);
        txDurationLabel->setObjectName(QString::fromUtf8("txDurationLabel"));
        txDurationLabel->setFont(font5);

        gridLayout_11->addWidget(txDurationLabel, 1, 1, 1, 1);

        gridLayout_11->setRowStretch(0, 2);

        gridLayout_3->addLayout(gridLayout_11, 0, 0, 1, 1);


        gridLayout_4->addWidget(RateBox, 2, 1, 1, 3);

        pduGeneratorGroup = new QGroupBox(centralWidget);
        pduGeneratorGroup->setObjectName(QString::fromUtf8("pduGeneratorGroup"));
        pduGeneratorGroup->setEnabled(true);
        QFont font6;
        font6.setPointSize(15);
        pduGeneratorGroup->setFont(font6);
        pduGeneratorGroup->setStyleSheet(QString::fromUtf8("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 5px;\n"
"    margin-top: 0.5em;\n"
"    margin-top: 0.6em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
"}"));
        gridLayout_8 = new QGridLayout(pduGeneratorGroup);
        gridLayout_8->setSpacing(6);
        gridLayout_8->setContentsMargins(11, 11, 11, 11);
        gridLayout_8->setObjectName(QString::fromUtf8("gridLayout_8"));
        verticalSpacer_2 = new QSpacerItem(20, 2, QSizePolicy::Minimum, QSizePolicy::Preferred);

        gridLayout_8->addItem(verticalSpacer_2, 0, 1, 1, 1);

        verticalSpacer_3 = new QSpacerItem(20, 2, QSizePolicy::Minimum, QSizePolicy::MinimumExpanding);

        gridLayout_8->addItem(verticalSpacer_3, 7, 1, 4, 1);

        videoTxGroup = new QGroupBox(pduGeneratorGroup);
        videoTxGroup->setObjectName(QString::fromUtf8("videoTxGroup"));
        videoTxGroup->setEnabled(false);
        videoTxGroup->setFont(font1);
        videoTxGroup->setStyleSheet(QString::fromUtf8("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 5px;\n"
"    margin-top: 0.6em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
"}"));
        gridLayout_6 = new QGridLayout(videoTxGroup);
        gridLayout_6->setSpacing(6);
        gridLayout_6->setContentsMargins(11, 11, 11, 11);
        gridLayout_6->setObjectName(QString::fromUtf8("gridLayout_6"));
        formLayout_3 = new QFormLayout();
        formLayout_3->setSpacing(6);
        formLayout_3->setObjectName(QString::fromUtf8("formLayout_3"));
        label_7 = new QLabel(videoTxGroup);
        label_7->setObjectName(QString::fromUtf8("label_7"));
        label_7->setFont(font2);

        formLayout_3->setWidget(0, QFormLayout::LabelRole, label_7);

        cameraSelect = new QComboBox(videoTxGroup);
        cameraSelect->setObjectName(QString::fromUtf8("cameraSelect"));

        formLayout_3->setWidget(0, QFormLayout::FieldRole, cameraSelect);

        cameraConnectButton = new QPushButton(videoTxGroup);
        cameraConnectButton->setObjectName(QString::fromUtf8("cameraConnectButton"));

        formLayout_3->setWidget(1, QFormLayout::FieldRole, cameraConnectButton);

        videoTxButton = new QPushButton(videoTxGroup);
        videoTxButton->setObjectName(QString::fromUtf8("videoTxButton"));
        videoTxButton->setEnabled(false);
        QFont font7;
        font7.setFamily(QString::fromUtf8("Ubuntu"));
        font7.setPointSize(14);
        font7.setBold(true);
        font7.setItalic(false);
        font7.setWeight(75);
        videoTxButton->setFont(font7);

        formLayout_3->setWidget(2, QFormLayout::SpanningRole, videoTxButton);


        gridLayout_6->addLayout(formLayout_3, 1, 1, 1, 1);


        gridLayout_8->addWidget(videoTxGroup, 13, 1, 1, 1);

        horizontalSpacer_11 = new QSpacerItem(10, 20, QSizePolicy::Minimum, QSizePolicy::Minimum);

        gridLayout_8->addItem(horizontalSpacer_11, 13, 0, 1, 1);

        txParamGroup = new QGroupBox(pduGeneratorGroup);
        txParamGroup->setObjectName(QString::fromUtf8("txParamGroup"));
        txParamGroup->setFont(font1);
        gridLayout_10 = new QGridLayout(txParamGroup);
        gridLayout_10->setSpacing(6);
        gridLayout_10->setContentsMargins(11, 11, 11, 11);
        gridLayout_10->setObjectName(QString::fromUtf8("gridLayout_10"));
        gridLayout_9 = new QGridLayout();
        gridLayout_9->setSpacing(6);
        gridLayout_9->setObjectName(QString::fromUtf8("gridLayout_9"));
        formLayout_5 = new QFormLayout();
        formLayout_5->setSpacing(6);
        formLayout_5->setObjectName(QString::fromUtf8("formLayout_5"));
        formLayout_5->setSizeConstraint(QLayout::SetDefaultConstraint);
        dataIntervalLabel = new QLabel(txParamGroup);
        dataIntervalLabel->setObjectName(QString::fromUtf8("dataIntervalLabel"));
        dataIntervalLabel->setFont(font2);

        formLayout_5->setWidget(3, QFormLayout::LabelRole, dataIntervalLabel);

        dataIntervalInput = new QLineEdit(txParamGroup);
        dataIntervalInput->setObjectName(QString::fromUtf8("dataIntervalInput"));
        dataIntervalInput->setFont(font4);
        dataIntervalInput->setInputMethodHints(Qt::ImhPreferNumbers);
        dataIntervalInput->setEchoMode(QLineEdit::Normal);

        formLayout_5->setWidget(3, QFormLayout::FieldRole, dataIntervalInput);

        dataSizeLabel = new QLabel(txParamGroup);
        dataSizeLabel->setObjectName(QString::fromUtf8("dataSizeLabel"));
        dataSizeLabel->setFont(font2);

        formLayout_5->setWidget(4, QFormLayout::LabelRole, dataSizeLabel);

        dataSizeInput = new QLineEdit(txParamGroup);
        dataSizeInput->setObjectName(QString::fromUtf8("dataSizeInput"));
        dataSizeInput->setFont(font4);

        formLayout_5->setWidget(4, QFormLayout::FieldRole, dataSizeInput);

        ndpIntervalLabel = new QLabel(txParamGroup);
        ndpIntervalLabel->setObjectName(QString::fromUtf8("ndpIntervalLabel"));
        ndpIntervalLabel->setFont(font2);

        formLayout_5->setWidget(1, QFormLayout::LabelRole, ndpIntervalLabel);

        ndpIntervalInput = new QLineEdit(txParamGroup);
        ndpIntervalInput->setObjectName(QString::fromUtf8("ndpIntervalInput"));
        ndpIntervalInput->setFont(font4);

        formLayout_5->setWidget(1, QFormLayout::FieldRole, ndpIntervalInput);

        line_3 = new QFrame(txParamGroup);
        line_3->setObjectName(QString::fromUtf8("line_3"));
        line_3->setFrameShape(QFrame::HLine);
        line_3->setFrameShadow(QFrame::Sunken);

        formLayout_5->setWidget(2, QFormLayout::SpanningRole, line_3);


        gridLayout_9->addLayout(formLayout_5, 3, 0, 1, 1);

        verticalSpacer_6 = new QSpacerItem(20, 2, QSizePolicy::Minimum, QSizePolicy::Preferred);

        gridLayout_9->addItem(verticalSpacer_6, 0, 0, 1, 1);


        gridLayout_10->addLayout(gridLayout_9, 0, 0, 1, 1);


        gridLayout_8->addWidget(txParamGroup, 1, 1, 1, 1);

        txModeGroup = new QGroupBox(pduGeneratorGroup);
        txModeGroup->setObjectName(QString::fromUtf8("txModeGroup"));
        txModeGroup->setEnabled(false);
        txModeGroup->setFont(font1);
        verticalLayout_8 = new QVBoxLayout(txModeGroup);
        verticalLayout_8->setSpacing(6);
        verticalLayout_8->setContentsMargins(11, 11, 11, 11);
        verticalLayout_8->setObjectName(QString::fromUtf8("verticalLayout_8"));
        verticalLayout_7 = new QVBoxLayout();
        verticalLayout_7->setSpacing(6);
        verticalLayout_7->setObjectName(QString::fromUtf8("verticalLayout_7"));
        horizontalLayout_2 = new QHBoxLayout();
        horizontalLayout_2->setSpacing(6);
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        ndpButton = new QRadioButton(txModeGroup);
        txButtonGroup = new QButtonGroup(MainWindow);
        txButtonGroup->setObjectName(QString::fromUtf8("txButtonGroup"));
        txButtonGroup->addButton(ndpButton);
        ndpButton->setObjectName(QString::fromUtf8("ndpButton"));
        ndpButton->setFont(font4);
        ndpButton->setChecked(true);

        horizontalLayout_2->addWidget(ndpButton);

        dataButton = new QRadioButton(txModeGroup);
        txButtonGroup->addButton(dataButton);
        dataButton->setObjectName(QString::fromUtf8("dataButton"));
        dataButton->setFont(font4);

        horizontalLayout_2->addWidget(dataButton);

        comboButton = new QRadioButton(txModeGroup);
        txButtonGroup->addButton(comboButton);
        comboButton->setObjectName(QString::fromUtf8("comboButton"));
        comboButton->setFont(font4);

        horizontalLayout_2->addWidget(comboButton);


        verticalLayout_7->addLayout(horizontalLayout_2);


        verticalLayout_8->addLayout(verticalLayout_7);


        gridLayout_8->addWidget(txModeGroup, 5, 1, 1, 1);

        horizontalSpacer_10 = new QSpacerItem(10, 20, QSizePolicy::Minimum, QSizePolicy::Minimum);

        gridLayout_8->addItem(horizontalSpacer_10, 13, 2, 1, 1);


        gridLayout_4->addWidget(pduGeneratorGroup, 0, 3, 1, 1);

        startButton = new QPushButton(centralWidget);
        startButton->setObjectName(QString::fromUtf8("startButton"));
        startButton->setMinimumSize(QSize(0, 50));
        QFont font8;
        font8.setPointSize(19);
        font8.setBold(true);
        font8.setWeight(75);
        startButton->setFont(font8);
        startButton->setFocusPolicy(Qt::StrongFocus);
        startButton->setAcceptDrops(false);
        startButton->setStyleSheet(QString::fromUtf8("color: rgb(204, 0, 0);"));

        gridLayout_4->addWidget(startButton, 1, 1, 1, 3);

        gridLayout_4->setColumnStretch(0, 1);
        MainWindow->setCentralWidget(centralWidget);

        retranslateUi(MainWindow);

        mcsSelect->setCurrentIndex(3);


        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QApplication::translate("MainWindow", "MIMO OFDM Packet Generator", nullptr));
        groupBox->setTitle(QApplication::translate("MainWindow", "System Configuration", nullptr));
        parameterGroup->setTitle(QApplication::translate("MainWindow", "System Parameters", nullptr));
        label_9->setText(QApplication::translate("MainWindow", "Data Subcarriers", nullptr));
        dataCarrierInput->setText(QApplication::translate("MainWindow", "48", nullptr));
        label_5->setText(QApplication::translate("MainWindow", "Modulation", nullptr));
        mcsSelect->setItemText(0, QApplication::translate("MainWindow", "BPSK 1/2", nullptr));
        mcsSelect->setItemText(1, QApplication::translate("MainWindow", "BPSK 3/4", nullptr));
        mcsSelect->setItemText(2, QApplication::translate("MainWindow", "QPSK 1/2", nullptr));
        mcsSelect->setItemText(3, QApplication::translate("MainWindow", "QPSK 3/4", nullptr));
        mcsSelect->setItemText(4, QApplication::translate("MainWindow", "16QAM 1/2", nullptr));
        mcsSelect->setItemText(5, QApplication::translate("MainWindow", "16 QAM 3/4", nullptr));

        label_3->setText(QApplication::translate("MainWindow", "FFT Length", nullptr));
        label_4->setText(QApplication::translate("MainWindow", "Cyclic Prefix Length", nullptr));
        cpPrefixInput->setText(QApplication::translate("MainWindow", "16", nullptr));
        fftLengthInput->setText(QApplication::translate("MainWindow", "64", nullptr));
        label_10->setText(QApplication::translate("MainWindow", "TX Antennas", nullptr));
        txAntennaInput->setText(QApplication::translate("MainWindow", "2", nullptr));
        label_12->setText(QApplication::translate("MainWindow", "Bandwidth (MHz)", nullptr));
        bandwidthInput->setText(QApplication::translate("MainWindow", "125", nullptr));
        gnuSocketGroup->setTitle(QApplication::translate("MainWindow", "GNU Radio Connection", nullptr));
        udpPortInput->setText(QApplication::translate("MainWindow", "52001", nullptr));
        label_6->setText(QApplication::translate("MainWindow", "UDP Port:", nullptr));
        RateBox->setTitle(QApplication::translate("MainWindow", "Current Configuration", nullptr));
        label_14->setText(QApplication::translate("MainWindow", "Data Tx Duration: ", nullptr));
        label_13->setText(QApplication::translate("MainWindow", "Maximum Throughput:", nullptr));
        currentRateLabel->setText(QApplication::translate("MainWindow", "0.0", nullptr));
        label_11->setText(QApplication::translate("MainWindow", "Data Throughput:", nullptr));
        maximumRateLabel->setText(QApplication::translate("MainWindow", "0.0", nullptr));
        txDurationLabel->setText(QApplication::translate("MainWindow", "0.0", nullptr));
        pduGeneratorGroup->setTitle(QApplication::translate("MainWindow", "Packet Configuration", nullptr));
        videoTxGroup->setTitle(QApplication::translate("MainWindow", "Video Streaming", nullptr));
        label_7->setText(QApplication::translate("MainWindow", "Camera Device: ", nullptr));
        cameraConnectButton->setText(QApplication::translate("MainWindow", "Connect", nullptr));
        videoTxButton->setText(QApplication::translate("MainWindow", "Start Streaming", nullptr));
        txParamGroup->setTitle(QApplication::translate("MainWindow", "Tranmission Parameters", nullptr));
        dataIntervalLabel->setText(QApplication::translate("MainWindow", "DATA Interval [ms]:", nullptr));
        dataIntervalInput->setText(QApplication::translate("MainWindow", "100", nullptr));
        dataSizeLabel->setText(QApplication::translate("MainWindow", "Packet Size [byte]: ", nullptr));
        dataSizeInput->setText(QApplication::translate("MainWindow", "500", nullptr));
        ndpIntervalLabel->setText(QApplication::translate("MainWindow", "NDP Interval [ms]:", nullptr));
        ndpIntervalInput->setText(QApplication::translate("MainWindow", "100", nullptr));
        txModeGroup->setTitle(QApplication::translate("MainWindow", "Transmission Mode", nullptr));
        ndpButton->setText(QApplication::translate("MainWindow", "NDP", nullptr));
        dataButton->setText(QApplication::translate("MainWindow", "DATA", nullptr));
        comboButton->setText(QApplication::translate("MainWindow", "NDP + DATA", nullptr));
        startButton->setText(QApplication::translate("MainWindow", "START", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
