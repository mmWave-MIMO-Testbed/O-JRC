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

#ifndef TXWORKER_H
#define TXWORKER_H

#include <QObject>
#include <QUdpSocket>
#include <QBuffer>
#include <chrono>
#include <thread>
#include <unistd.h>
#include <QCameraInfo>
#include <QCamera>
#include <QCameraViewfinder>
#include <QCameraImageCapture>
#include <QMediaRecorder>

enum txMode {
    OFFLINE,
    NDP_TX,
    RANDOM_DATA_TX,
    NDP_AIDED_DATA_TX,
    VIDEO_TX
};

enum PACKET_TYPE : uint8_t {
    NDP = 1,
    DATA = 2
};


class TxWorker : public QObject
{
    Q_OBJECT
public:
    TxWorker();
    ~TxWorker();
    void setPort(int UDPport);
    void setRunning(bool running);

    void setDataInterval(float dataInterval);
    void setNdpInterval(float ndpInterval);
    void setDataSize(int dataSize);
    void setTxMode(txMode mode);

    txMode getTxMode();
    int getDataSize();
    bool isCameraConnected();

    void connectCamera(QCameraInfo selectedCamera);
    void disconnectCamera();
    void stopCamera();
    void startCamera();



public slots:
    void process();

signals:
    void finished();
    void error(QString err);

private:
    bool running;
    bool cameraConnected;
    bool newFrame;

    int UDPport;

    double dataInterval;
    double ndpInterval;

    int dataSize;

    txMode currentMode;

    QByteArray frameBuffer;

    QCamera* camera;
    QCameraImageCapture* imageCapture;
};

#endif // TXWORKER_H
