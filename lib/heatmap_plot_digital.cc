/* -*- c++ -*- */
/*
 * Copyright 2022 gr-mimo_ofdm_jrc author.
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

#include "heatmap_plot_digital.h"
#include <iostream>
#include <stdexcept>
#include <fstream>
#include <sstream>
#include <string>


namespace gr {
namespace mimo_ofdm_jrc {


    heatmap_plot_digital::heatmap_plot_digital(int interval,
                                                    int vlen,
                                                    std::vector<float>* buffer,
                                                    std::string label_x,
                                                    std::string label_y,
                                                    std::string label,
                                                    std::vector<float> axis_x,
                                                    std::vector<float> axis_y,
                                                    float dynamic_range_db,
                                                    std::vector<float> x_axis_ticks,
                                                    std::vector<float> y_axis_ticks,
                                                    bool autoscale_z,
                                                    bool db_scale,
                                                    QWidget* parent)
        : QWidget(parent)
    {
        d_interval = interval;
        d_vlen = vlen;
        d_buffer = buffer;
        d_autoscale_z = autoscale_z;
        d_db_scale = db_scale;
        // d_axis_x = QVector<double>(axis_x.begin(), axis_x.end());
        // d_axis_y = QVector<double>(axis_y.begin(), axis_y.end());
        // d_axis_z = QVector<double>(axis_z.begin(), axis_z.end());
        // d_x_axis_ticks = QVector<double>(x_axis_ticks.begin(), x_axis_ticks.end());
        // d_y_axis_ticks = QVector<double>(y_axis_ticks.begin(), y_axis_ticks.end());

        d_axis_x = QVector<double>::fromStdVector(std::vector<double>(axis_x.begin(), axis_x.end()));
        d_axis_y = QVector<double>::fromStdVector(std::vector<double>(axis_y.begin(), axis_y.end()));
        // d_axis_z = QVector<double>::fromStdVector(std::vector<double>(axis_z.begin(), axis_z.end()));
        d_x_axis_ticks = QVector<double>::fromStdVector(std::vector<double>(x_axis_ticks.begin(), x_axis_ticks.end()));
        d_y_axis_ticks = QVector<double>::fromStdVector(std::vector<double>(y_axis_ticks.begin(), y_axis_ticks.end()));

        d_dynamic_range_db = dynamic_range_db;
        // Setup GUI
        resize(QSize(960, 960));
        setWindowTitle("Heatmap Plot");

        d_plot = new QwtPlot(this);               // make main plot
        d_spectrogram = new QwtPlotSpectrogram(); // make spectrogram
        d_spectrogram->attach(d_plot);            // attach spectrogram to plot

        // d_data = new QwtMatrixRasterData(); // make data structure
        d_data = new RangeAngleRasterData(); // make data structure

        // Setup colormap
        // d_colormap = new QwtLinearColorMap(Qt::darkCyan, Qt::red);
        // d_colormap->addColorStop(0.25, Qt::cyan);
        // d_colormap->addColorStop(0.5, Qt::green);
        // d_colormap->addColorStop(0.75, Qt::yellow);

        d_colormap = new QwtLinearColorMap( QColor(0,0,189), QColor(132,0,0), QwtColorMap::RGB );
        double pos;
        pos = 1.0/13.0*1.0; d_colormap->addColorStop(pos, QColor(0,0,255));
        pos = 1.0/13.0*2.0; d_colormap->addColorStop(pos, QColor(0,66,255));
        pos = 1.0/13.0*3.0; d_colormap->addColorStop(pos, QColor(0,132,255));
        pos = 1.0/13.0*4.0; d_colormap->addColorStop(pos, QColor(0,189,255));
        pos = 1.0/13.0*5.0; d_colormap->addColorStop(pos, QColor(0,255,255));
        pos = 1.0/13.0*6.0; d_colormap->addColorStop(pos, QColor(66,255,189));
        pos = 1.0/13.0*7.0; d_colormap->addColorStop(pos, QColor(132,255,132));
        pos = 1.0/13.0*8.0; d_colormap->addColorStop(pos, QColor(189,255,66));
        pos = 1.0/13.0*9.0; d_colormap->addColorStop(pos, QColor(255,255,0));
        pos = 1.0/13.0*10.0; d_colormap->addColorStop(pos, QColor(255,189,0));
        pos = 1.0/13.0*12.0; d_colormap->addColorStop(pos, QColor(255,66,0));
        pos = 1.0/13.0*13.0; d_colormap->addColorStop(pos, QColor(189,0,0));

        d_spectrogram->setColorMap(d_colormap);

        // Plot axis and title
        // std::string label_title = "Heatmap: ";
        // label_title.append(label_x);
        // label_title.append("/");
        // label_title.append(label_y);
        // if (label != "") {
        //     label_title.append(" (");
        //     label_title.append(label);
        //     label_title.append(")");
        // }

        QwtText title_text;
        QFont title_font;
        title_font.setPointSize(20); 
        title_font.setBold(true);
        title_text.setFont(title_font);
        title_text.setText(label.c_str());
        d_plot->setTitle(title_text);

        QwtText axis_title_text;
        axis_title_font.setPointSize(20); 
        axis_title_font.setBold(true);
        axis_title_text.setFont(axis_title_font);
        axis_title_text.setText(label_x.c_str());

        d_plot->setAxisTitle(QwtPlot::xBottom, axis_title_text);
        axis_title_text.setText(label_y.c_str());
        d_plot->setAxisTitle(QwtPlot::yLeft, axis_title_text);

        axis_font.setPointSize(15); 
        d_plot->setAxisFont(QwtPlot::xBottom, axis_font);
        d_plot->setAxisFont(QwtPlot::yLeft, axis_font);

        // d_plot->setAxisScaleDiv(QwtPlot::xBottom, QwtScaleDiv(d_x_axis_ticks.first(),d_x_axis_ticks.back(),d_x_axis_ticks.toList()));
        // QwtScaleDiv()

        if (d_x_axis_ticks.size() != 3 || d_y_axis_ticks.size() != 3)
        {
            throw std::invalid_argument("[HEATMAP PLOT] x-axis and y-axis ticks should be as [start, stop, step size]!");
        }

        d_plot->setAxisScale(QwtPlot::xBottom, d_x_axis_ticks[0], d_x_axis_ticks[1], d_x_axis_ticks[2]);
        d_plot->setAxisScale(QwtPlot::yLeft, d_y_axis_ticks[0], d_y_axis_ticks[1], d_y_axis_ticks[2]);

        // Do replot
        d_plot->replot();

        // Setup timer and connect refreshing plot
        d_timer = new QTimer(this);
        connect(d_timer, SIGNAL(timeout()), this, SLOT(refresh()));
        d_timer->start(d_interval);
    }

    heatmap_plot_digital::~heatmap_plot_digital() {}

    void heatmap_plot_digital::resizeEvent(QResizeEvent* event)
    {
        d_plot->setGeometry(0, 0, this->width(), this->height());
    }

    void heatmap_plot_digital::refresh()
    {
        // Fetch new data and push to matrix
        d_plot_data.clear();
        
        float maximum, minimum; // get maximum and minimum
        float min_display;

        // digital or analog
        if (true)  // digital Beamforming mode
        {

            if (d_buffer->size() != 0) {
                d_plot_data.resize(d_buffer->size());

                // d_plot_data = QVector<double>(d_buffer->begin(), d_buffer->end());
                d_plot_data = QVector<double>::fromStdVector(std::vector<double>(d_buffer->begin(), d_buffer->end()));

                minimum = *std::min_element( std::begin(d_plot_data), std::end(d_plot_data) );
                maximum = *std::max_element( std::begin(d_plot_data), std::end(d_plot_data) );
                
                if (std::isnan(minimum) || std::isnan(maximum)){
                    throw std::runtime_error("minimum or maximum for z axis is NaN");
                }
                    
                // Fill data in spectrogram
                // d_data->setValueMatrix(d_plot_data, columns);
                d_data->setValueMatrix(d_plot_data, d_axis_x, d_axis_y);
                // d_plot_data: the data, d_axis_x: the position of x axis(nubmer of columns), d_axis_y: number of rows.
                // d_data: d_axis_y * d_axis_x matrix, filling the matrix row by row 
                d_data->setResampleMode(RangeAngleRasterData::BilinearInterpolation); 

                // d_data->setInterval(Qt::XAxis, QwtInterval(d_axis_x[0], d_axis_x[1]));
                // d_data->setInterval(Qt::YAxis, QwtInterval(d_axis_y[0], d_axis_y[1]));
                QwtInterval intervall = QwtInterval(d_axis_x.front(), d_axis_x.back());
                
                d_data->setInterval(Qt::XAxis, QwtInterval(d_axis_x.front(), d_axis_x.back()));
                d_data->setInterval(Qt::YAxis, QwtInterval(d_axis_y.front(), d_axis_y.back()));
            }
        }
        

            if (d_db_scale)
            {
                min_display = maximum-d_dynamic_range_db;
            }
            else
            {
                min_display = maximum/std::pow(10,d_dynamic_range_db/10);
            }

            if (d_autoscale_z) 
            {
                d_data->setInterval(Qt::ZAxis, QwtInterval(minimum, maximum));
            } 
            else 
            {
                d_data->setInterval(Qt::ZAxis, QwtInterval(min_display, maximum));
            }
            d_spectrogram->setData(d_data);

            QFont colorbar_font;
            colorbar_font.setPointSize(10); 

            // Set colorbar
            d_scale = d_plot->axisWidget(QwtPlot::yRight);
            d_scale->setColorBarEnabled(true);
            d_scale->setColorBarWidth(20);
            d_scale->setFont(colorbar_font);

            if (d_autoscale_z) 
            {
                d_scale->setColorMap(QwtInterval(minimum, maximum), d_colormap);
                d_plot->setAxisScale(QwtPlot::yRight, minimum, maximum);
            } 
            else 
            {
                d_scale->setColorMap(QwtInterval(min_display, maximum), d_colormap);
                d_plot->setAxisScale(QwtPlot::yRight, min_display, maximum);
            }
            d_plot->enableAxis(QwtPlot::yRight);
        
            // d_plot->setAxisScaleDiv(Qt::ZAxis, QwtScaleDiv(QwtInterval(d_axis_x.front(), d_axis_x.back()), d_axis_x.front(), d_axis_x.back()));
            // Do replot
            d_plot->replot();
        
    }

} // namespace mimo_ofdm_jrc
} // namespace gr

