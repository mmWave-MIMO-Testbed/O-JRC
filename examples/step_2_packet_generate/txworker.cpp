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

#include "txworker.h"

TxWorker::TxWorker()
{
    running = false;
    cameraConnected = false;
    currentMode = OFFLINE;
    ndpInterval = -1;
    dataInterval = -1;
    dataSize = 0;
    newFrame = false;
}

TxWorker::~TxWorker()
{
}

void TxWorker::process() {

    if (UDPport == 1)
    {
        qDebug("[Transmitter] Port number is not set correctly!!");
        emit finished();
    }
    else
    {
        running = true;
        qDebug("[Transmitter] Starting Radar...");
        QUdpSocket* UDPsocket = new QUdpSocket();

        std::vector<char> ndpCharArr(3);
        ndpCharArr[0] = (char) PACKET_TYPE::NDP;
        std::fill_n(ndpCharArr.begin()+1, ndpCharArr.size()-1, 'X');

        std::vector<char> randCharArr(dataSize + 1);
        randCharArr[0] = (char) PACKET_TYPE::DATA;
        std::fill_n(randCharArr.begin()+1, dataSize, 'X');

        QByteArray datagram;

        uint8_t numPackets;
        while (running)
        {
            switch(currentMode)
            {
                case OFFLINE:{
                    running = false;
                    break;
                }

                case NDP_TX:{

                    datagram = QByteArray::fromRawData(ndpCharArr.data(), ndpCharArr.size());
                    UDPsocket->writeDatagram(datagram, QHostAddress::LocalHost, UDPport);
                    UDPsocket->flush();

                    std::this_thread::sleep_for(std::chrono::microseconds((int)(ndpInterval*1000)));
                    break;
                }

                case RANDOM_DATA_TX:{

                    if (randCharArr.size() != dataSize + 1)
                    {
                        randCharArr.resize(dataSize + 1);
                        randCharArr[0] = (char) PACKET_TYPE::DATA;
                        std::fill_n(randCharArr.begin() + 1, dataSize, 'X');
                    }
                    datagram = QByteArray::fromRawData(randCharArr.data(), randCharArr.size());
                    UDPsocket->writeDatagram(datagram, QHostAddress::LocalHost, UDPport);
                    UDPsocket->flush();

                    std::this_thread::sleep_for(std::chrono::microseconds((int)(dataInterval*1000)));
                    break;
                }

                case NDP_AIDED_DATA_TX:{

                    datagram = QByteArray::fromRawData(ndpCharArr.data(), ndpCharArr.size());
                    UDPsocket->writeDatagram(datagram, QHostAddress::LocalHost, UDPport);
                    UDPsocket->flush();

                    std::this_thread::sleep_for(std::chrono::microseconds((int)(ndpInterval*1000)));

                    if (randCharArr.size() != dataSize + 1)
                    {
                        randCharArr.resize(dataSize + 1);
                        randCharArr[0] = (char) PACKET_TYPE::DATA;
                        std::fill_n(randCharArr.begin() + 1, dataSize, 'X');
                    }
                    datagram = QByteArray::fromRawData(randCharArr.data(), randCharArr.size());
                    UDPsocket->writeDatagram(datagram, QHostAddress::LocalHost, UDPport);
                    UDPsocket->flush();

                    std::this_thread::sleep_for(std::chrono::microseconds((int)(dataInterval*1000)));
                    break;
                }

                case VIDEO_TX:{
                    if (newFrame)
                    {
                        numPackets = (frameBuffer.size()+2)/dataSize + 1;
                        for (int i = 0; i < numPackets; ++i)
                        {
                            if (i == 0)
                            {
                                qDebug("[Transmitter] numPackets: %d", numPackets);

                                datagram.resize(0);
                                datagram.append('f'); //Frame Start  Signal
                                datagram.append((char) numPackets); //Number of packets for current frame
                                datagram.append(frameBuffer.data(),dataSize-2); //Append first packet
                                UDPsocket->writeDatagram(datagram, QHostAddress::LocalHost, UDPport);
                            }
                            else
                            {
                                int packetSize = std::min(dataSize, frameBuffer.size()-(dataSize-2+(i-1)*dataSize));
                                datagram = QByteArray(frameBuffer.data()+dataSize-2+(i-1)*dataSize, packetSize);
                                UDPsocket->writeDatagram(datagram, QHostAddress::LocalHost, UDPport); 
                            }
                            std::this_thread::sleep_for(std::chrono::microseconds((int)(dataInterval*1000)));

                        }
                        qDebug("All sent");

                        imageCapture->capture();

                        newFrame = false;
                    }
                    else
                    {

                    }
                    break;
                }
            }
        }
        qDebug("[Transmitter] Stopping Radar...");
        delete UDPsocket;
        if (cameraConnected)
        {
            disconnectCamera();
        }
        emit finished();
    }
}

void TxWorker::setPort(int UDPport)
{
    this->UDPport = UDPport;
    qDebug("[Transmitter] Port Number is set to %d", UDPport);
}

void TxWorker::setDataInterval(float dataInterval)
{
    this->dataInterval = dataInterval;
    qDebug("[Transmitter] DATA Interval is set to %.3f ms", dataInterval);
}

void TxWorker::setNdpInterval(float ndpInterval)
{
    this->ndpInterval = ndpInterval;
    qDebug("[Transmitter] NDP Interval is set to %.3f ms", ndpInterval);
}

void TxWorker::setRunning(bool running)
{
    this->running = running;
    if (!running)
    {
        this->currentMode = OFFLINE;
    }
//    qDebug("[Transmitter] Running set to %d", running);
}

void TxWorker::setTxMode(txMode currentMode)
{
    this->currentMode = currentMode;
//    qDebug("[Transmitter] TxMode set to %d", (int)currentMode);
}

void TxWorker::setDataSize(int dataSize)
{
    this->dataSize = dataSize;
    qDebug("Packet Size set to %d bytes", dataSize);
}

int TxWorker::getDataSize()
{
    return this->dataSize;
}

txMode TxWorker::getTxMode()
{
    return this->currentMode;
}

bool TxWorker::isCameraConnected()
{
    return this->cameraConnected;
}

void TxWorker::connectCamera(QCameraInfo selectedCamera)
{
    camera = new QCamera(selectedCamera);
    camera->load();
    camera->setCaptureMode(QCamera::CaptureStillImage);

    imageCapture = new QCameraImageCapture(camera);
    imageCapture->setCaptureDestination(QCameraImageCapture::CaptureToBuffer);

    QImageEncoderSettings settings = imageCapture->encodingSettings();
    settings.setQuality(QMultimedia::EncodingQuality(2));
//    settings.setResolution(QSize(1280,720));
    settings.setResolution(QSize(960,720));
//    settings.setResolution(QSize(640,480));

    imageCapture->setEncodingSettings(settings);

    qDebug() << "[Transmitter] Camera connected to " << selectedCamera.description();

    connect(imageCapture, &QCameraImageCapture::imageCaptured, [=] (int id, QImage img)
    {
        qDebug() << "[Transmitter] imageCaptured";
//        qDebug("[Transmitter] Image Format: %d", img.format());
        frameBuffer.resize(0);
        QBuffer buffer(&frameBuffer);
        buffer.open(QIODevice::WriteOnly);
        img.save(&buffer, "JPEG", 30);
//        img.save(&buffer, "JPEG",-1);
        qDebug("[Transmitter] Frame Size: %d", frameBuffer.size());

        newFrame = true;
    });

    connect(imageCapture, &QCameraImageCapture::readyForCaptureChanged, [=] (bool state)
    {
       if(state == true)
       {
           qDebug() << "[Transmitter] readyForCaptureChanged";

           camera->searchAndLock();
           imageCapture->capture();
           camera->unlock();
       }
    });

    const QStringList supportedImageCodecs = imageCapture->supportedImageCodecs();
    for (const QString &codecName : supportedImageCodecs) {
        qDebug() << "Camera Codecs: " << imageCapture->imageCodecDescription(codecName);
    }

    const QList<QSize> supportedResolutions = imageCapture->supportedResolutions();
    qDebug("Supported  Resolutions: %d", supportedResolutions.size());

    for (const QSize &resolution : supportedResolutions) {
            qDebug("Resolution: %dx%d", resolution.height(),resolution.width());
    }

    this->cameraConnected = true;
}

void TxWorker::disconnectCamera()
{
    camera->stop();
    camera->disconnect();
    qDebug() << "Camera disconnected...";

    this->imageCapture->disconnect();
    this->cameraConnected = false;
}

void TxWorker::stopCamera()
{
    camera->stop();
    camera->unload();
    qDebug() << "Camera stopped...";
}

void TxWorker::startCamera()
{
    camera->load();
    camera->setCaptureMode(QCamera::CaptureStillImage);
    camera->start();
    qDebug() << "Camera started...";
}





