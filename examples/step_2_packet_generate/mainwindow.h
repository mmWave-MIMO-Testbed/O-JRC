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

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QDebug>
#include <QCloseEvent>
#include <QMessageBox>
#include <QThread>
#include <QMediaRecorder>
#include <QUrl>
#include "txworker.h"

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    void closeEvent (QCloseEvent *event);
    ~MainWindow();

private slots:
    void on_startButton_clicked();

    void on_cameraConnectButton_clicked();

    void on_videoTxButton_clicked();

    void on_dataIntervalInput_returnPressed();

    void on_ndpButton_clicked();

    void on_dataButton_clicked();

    void on_comboButton_clicked();

    void on_ndpIntervalInput_returnPressed();

    void on_dataSizeInput_returnPressed();

private:
    Ui::MainWindow *ui;
    TxWorker* tx_worker;

    bool isStarted;
    int calculateMaxPduSize();
    double computeMaxDataRate();
    double computeTxDuration();
    double computeNdpTxDuration();
    double computeCurrentDataRate(bool withNdp);
    QString convertToUnits(double l_nvalue);

};

#endif // MAINWINDOW_H
