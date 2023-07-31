/*
 * Copyright 2022 Ceyhun D. Ozkaptan @ The Ohio State University <ozkaptan.1@osu.edu>
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <math.h>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    isStarted = false;

    qDebug() << "[Main] Number of Cameras Found: " <<
    QCameraInfo::availableCameras().count();
    QList<QCameraInfo> cameras = QCameraInfo::availableCameras();
    foreach (const QCameraInfo &cameraInfo, cameras)
    {
        qDebug() << "[Main] Camera Info: " << cameraInfo.deviceName() <<
                    cameraInfo.description() << cameraInfo.position();
        ui->cameraSelect->addItem(cameraInfo.description());
    }
}

MainWindow::~MainWindow()
{
    delete ui;
    delete tx_worker;
}

void MainWindow::closeEvent (QCloseEvent *event)
{
    QMessageBox::StandardButton resBtn =
            QMessageBox::question( this, "Joint Radar PDU Generator", tr("Are you sure?\n"),
                                   QMessageBox::No | QMessageBox::Yes,QMessageBox::Yes);

    if (resBtn != QMessageBox::Yes)
    {
        event->ignore();
    } else
    {
        event->accept();
    }
}


void MainWindow::on_startButton_clicked()
{
    if(!isStarted)
    {
        QMessageBox::StandardButton resBtn =
                QMessageBox::question( this, "Joint Radar PDU Generator", tr("Is GNURadio running? \n Are parameters set correctly?\n"),
                                       QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);
        if (resBtn == QMessageBox::Yes)
        {
            isStarted = true;
            int udpPort = ui->udpPortInput->text().toInt();

            float ndpInterval = ui->ndpIntervalInput->text().toFloat();
            float dataInterval = ui->dataIntervalInput->text().toFloat();
            int dataSize = ui->dataSizeInput->text().toInt();

            QThread* thread = new QThread;

            tx_worker = new TxWorker();
            tx_worker->setPort(udpPort);
            tx_worker->setNdpInterval(ndpInterval);
            tx_worker->setDataInterval(dataInterval);
            tx_worker->setDataSize(dataSize);
            tx_worker->setTxMode(NDP_TX);
            tx_worker->moveToThread(thread);

            connect(thread, SIGNAL(started()), tx_worker, SLOT(process()));                 // the thread’s started() signal to the processing() slot in the tx_worker, causing it to start.
            connect(tx_worker, SIGNAL(finished()), thread, SLOT(quit()));                   // tx_worker instance emits finished(), it will signal the thread to quit
            connect(tx_worker, SIGNAL(finished()), tx_worker, SLOT(deleteLater()));         // mark the tx_worker instance using the same finished() signal for deletion.
            connect(thread, SIGNAL(finished()), thread, SLOT(deleteLater()));               // the thread to be deleted only after it has fully shut down

            thread->start();

            ui->startButton->setText("STOP");

            ui->parameterGroup->setEnabled(false);
            ui->gnuSocketGroup->setEnabled(false);

            ui->txModeGroup->setEnabled(true);
            ui->videoTxGroup->setEnabled(true);
            ui->RateBox->setEnabled(true);

            ui->ndpButton->click();

            ui->txDurationLabel->setText(QString().sprintf("%.3f ms", computeTxDuration()*1e3));
            ui->maximumRateLabel->setText(convertToUnits(computeMaxDataRate()));
            ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(false)));

        }
    }
    else
    {
        tx_worker->setRunning(false);
        isStarted = false;

        ui->startButton->setText("START");
        ui->videoTxButton->setText("Start Streaming");

        ui->parameterGroup->setEnabled(true);
        ui->gnuSocketGroup->setEnabled(true);

        ui->txModeGroup->setEnabled(false);
        ui->videoTxGroup->setEnabled(false);
        ui->ndpButton->click();

        ui->RateBox->setEnabled(false);

        ui->txDurationLabel->setText("0.0");
        ui->currentRateLabel->setText("0.0");
        ui->maximumRateLabel->setText("0.0");
    }
}


void MainWindow::on_ndpIntervalInput_returnPressed()
{
    float ndpInterval = ui->ndpIntervalInput->text().toFloat();
    tx_worker->setNdpInterval(ndpInterval);

    if (tx_worker->getTxMode() == NDP_AIDED_DATA_TX)
    {
        ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(true)));
    }
}

void MainWindow::on_dataIntervalInput_returnPressed()
{
    float dataInterval = ui->dataIntervalInput->text().toFloat();
    tx_worker->setDataInterval(dataInterval);

    if(isStarted)
    {
        ui->txDurationLabel->setText(QString().sprintf("%.3f ms", computeTxDuration()*1e3));
        switch (tx_worker->getTxMode())
        {
            default:
                ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(false)));
                ui->maximumRateLabel->setText(convertToUnits(computeMaxDataRate()));
                break;

            case NDP_AIDED_DATA_TX:
                ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(true)));
                ui->maximumRateLabel->setText("N/A");

                break;
        }
    }
}

void MainWindow::on_dataSizeInput_returnPressed()
{
    int dataSize = ui->dataSizeInput->text().toInt();
    tx_worker->setDataSize(dataSize);

    if(isStarted)
    {
        ui->txDurationLabel->setText(QString().sprintf("%.3f ms", computeTxDuration()*1e3));
        ui->maximumRateLabel->setText(convertToUnits(computeMaxDataRate()));

        if (tx_worker->getTxMode() == NDP_AIDED_DATA_TX)
        {
            ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(true)));
        }
        else
        {
            ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(false)));
        }
    }

}

void MainWindow::on_ndpButton_clicked()
{
    ui->videoTxGroup->setEnabled(false);

    float ndpInterval = ui->ndpIntervalInput->text().toFloat();

    tx_worker->setNdpInterval(ndpInterval);
    tx_worker->setTxMode(NDP_TX);
}

void MainWindow::on_dataButton_clicked()
{

    ui->videoTxGroup->setEnabled(true);

    int dataSize = ui->dataSizeInput->text().toInt();
    tx_worker->setDataSize(dataSize);

    float dataInterval = ui->dataIntervalInput->text().toFloat();
    tx_worker->setDataInterval(dataInterval);
    tx_worker->setTxMode(RANDOM_DATA_TX);

    ui->txDurationLabel->setText(QString().sprintf("%.3f ms", computeTxDuration()*1e3));

    ui->maximumRateLabel->setText(convertToUnits(computeMaxDataRate()));
    ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(false)));
}


void MainWindow::on_comboButton_clicked()
{
    ui->videoTxGroup->setEnabled(false);

    float ndpInterval = ui->ndpIntervalInput->text().toFloat();
    tx_worker->setNdpInterval(ndpInterval);

    int dataSize = ui->dataSizeInput->text().toInt();
    tx_worker->setDataSize(dataSize);

    float dataInterval = ui->dataIntervalInput->text().toFloat();
    tx_worker->setDataInterval(dataInterval);

    tx_worker->setTxMode(NDP_AIDED_DATA_TX);

    ui->txDurationLabel->setText(QString().sprintf("%.3f ms", computeTxDuration()*1e3));
    ui->currentRateLabel->setText(convertToUnits(computeCurrentDataRate(true)));

    ui->maximumRateLabel->setText("N/A");
}


void MainWindow::on_cameraConnectButton_clicked()
{
    if (!tx_worker->isCameraConnected())
    {
        QList<QCameraInfo> cameras = QCameraInfo::availableCameras();

        foreach (const QCameraInfo &cameraInfo, cameras)
        {
            if (cameraInfo.description() == ui->cameraSelect->currentText())
            {
                tx_worker->connectCamera(cameraInfo);
                ui->cameraConnectButton->setText("Disconnect");
                ui->cameraSelect->setEnabled(false);
                ui->videoTxButton->setEnabled(true);
            }
        }
    }
    else
    {
        tx_worker->disconnectCamera();
        ui->cameraConnectButton->setText("Connect");
        ui->cameraSelect->setEnabled(true);
        ui->videoTxButton->setEnabled(false);
    }
}

void MainWindow::on_videoTxButton_clicked()
{
    if (tx_worker->getTxMode() != VIDEO_TX)
    {
        float dataInterval = ui->dataIntervalInput->text().toFloat();
        tx_worker->setDataInterval(dataInterval);
        tx_worker->setTxMode(VIDEO_TX);
        tx_worker->startCamera();

        ui->videoTxButton->setText("STOP Streaming");
        ui->cameraConnectButton->setEnabled(false);
    }
    else
    {
        tx_worker->setTxMode(NDP_TX);
        tx_worker->disconnectCamera();
        ui->cameraConnectButton->setText("Connect");


        ui->videoTxButton->setText("Start Transmission");
        ui->videoTxButton->setEnabled(false);

        ui->cameraConnectButton->setEnabled(true);
        ui->cameraSelect->setEnabled(true);

        ui->currentRateLabel->setText("0.0");
    }
}


int MainWindow::calculateMaxPduSize()
{
    int serviceFieldSize = 3 + 4 + 1; //Service + CRC32 + Padding

    int data_carr_len = ui->dataCarrierInput->text().toInt();

    int mcs_index = ui->mcsSelect->currentIndex();

    int bitsPerSymbol[3] = {1, 2, 4};

    double codingRate[2] = {0.5, 0.75};

    return (int)(bitsPerSymbol[mcs_index/3]*codingRate[mcs_index%2]*data_carr_len/8) - serviceFieldSize;
}

double MainWindow::computeTxDuration()
{
    int mcs_index = ui->mcsSelect->currentIndex();
    int data_carr_len = ui->dataCarrierInput->text().toInt();

    int sampleRate = ui->bandwidthInput->text().toInt();
    int fftLen = ui->fftLengthInput->text().toInt();
    int cpLen = ui->cpPrefixInput->text().toInt();

    int N_tx = ui->txAntennaInput->text().toInt();


    double ofdmSymDuration = (fftLen + cpLen)/ ((double) sampleRate*1e6);

    int bitsPerCarrier[3] = {1, 2, 4};
    double codingRate[2] = {0.5, 0.75};

    int bitsPerOFDM = data_carr_len * bitsPerCarrier[mcs_index/3] * codingRate[mcs_index%2];

    int dataSize_byte = tx_worker->getDataSize();

    int n_ofdm_sym = (int) ceil((16 + 8 * (dataSize_byte+4) + 6) / (double) bitsPerOFDM);

    qDebug("Number of OFDM Symbols for Data: %d", n_ofdm_sym);

    return (4 + 1 + N_tx + n_ofdm_sym) * ofdmSymDuration;
}

double MainWindow::computeNdpTxDuration()
{
    int mcs_index = ui->mcsSelect->currentIndex();
    int data_carr_len = ui->dataCarrierInput->text().toInt();

    int sampleRate = ui->bandwidthInput->text().toInt();
    int fftLen = ui->fftLengthInput->text().toInt();
    int cpLen = ui->cpPrefixInput->text().toInt();

    int N_tx = ui->txAntennaInput->text().toInt();


    double ofdmSymDuration = (fftLen + cpLen)/ ((double) sampleRate*1e6);

    int bitsPerCarrier[3] = {1, 2, 4};
    double codingRate[2] = {0.5, 0.75};

    int bitsPerOFDM = data_carr_len * bitsPerCarrier[mcs_index/3] * codingRate[mcs_index%2];

    int dataSize_byte = 1;

    int n_ofdm_sym = (int) ceil((16 + 8 * (dataSize_byte+4) + 6) / (double) bitsPerOFDM);

    qDebug("Number of OFDM Symbols for NDP: %d", n_ofdm_sym);

    return (4 + 1 + N_tx + n_ofdm_sym) * ofdmSymDuration;
}

double MainWindow::computeCurrentDataRate(bool withNdp)
{
    float dataInterval = ui->dataIntervalInput->text().toFloat();
    double txDuration = computeTxDuration();
    int dataSize = ui->dataSizeInput->text().toFloat();

    double totalDataInterval = (dataInterval * 1e-3) + txDuration;

    if (!withNdp)
    {
        return (double) dataSize*8.0 / totalDataInterval;
    }
    else
    {
        float ndpInterval = ui->ndpIntervalInput->text().toFloat();
        double ndpTxDuration = computeNdpTxDuration();

        double totalNDPInterval = (ndpInterval * 1e-3) + ndpTxDuration;

        return (double) dataSize*8.0 / (totalDataInterval + totalNDPInterval);
    }
}



double MainWindow::computeMaxDataRate()
{
    double txDuration = computeTxDuration();
    int dataSize = ui->dataSizeInput->text().toInt();

    return (double) dataSize*8.0  / (double) txDuration;
}


QString MainWindow::convertToUnits(double l_nvalue)
{
    QString unit;
    double value;

    if(l_nvalue < 0) {
     value = l_nvalue * -1;
    } else {
     value = l_nvalue;
    }

    if(value >= 1000000 && value < 1000000000) {
     value = value/1000000;
     unit = " Mbps";
    }
    else if(value>=1000 && value<1000000){
     value = value/1000;
     unit = " Kbps";
    }
    else if( value>=1 && value<1000) {
     value = value*1;
     unit = " bps";

    }

    if(l_nvalue>0) {
     return (QString::number(value,'f',2)+unit);
    } else
    if(l_nvalue<0) {
     return (QString::number(value*-1)+unit);
    }

    return QString::number(0);
}



