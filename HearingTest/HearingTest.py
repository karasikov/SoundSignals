# -*- coding: utf-8 -*-

import pyaudio
import wave
import numpy as np
import struct
import re
import sys
import wx


class FreqSimulatorApp(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Frequency Simulator')

        self.panel = wx.Panel(self.frame)

        self.CreateWidgets()
        self.frame.Show()

    def CreateWidgets(self):
        self.statusbar = self.frame.CreateStatusBar(1)

        def NewButton(label, action):
            new_button = wx.Button(self.panel, label=label)
            new_button.Bind(wx.EVT_BUTTON, action)
            return new_button

        # Initialize Grid
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # first column
        self.column_1 = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.column_1, 1, wx.ALL|wx.EXPAND, 5)

        self.volume_sld = wx.Slider(self.panel, value=50,
                            minValue=0, maxValue=100,
                            pos=(20, 20), size=(250, -1),
                            style=wx.SL_HORIZONTAL)

        self.volume_sld.Bind(wx.EVT_SCROLL, self.OnVolumeScroll)

        self.volume = wx.StaticText(self.panel, label='', pos=(20, 90))
        self.OnVolumeScroll(None)

        self.column_1.Add(self.volume_sld, 0, wx.ALL|wx.EXPAND, 5)
        self.column_1.Add(self.volume, 0, wx.ALL|wx.EXPAND, 5)

        self.column_1.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                                        0, wx.ALL|wx.EXPAND, 5)

        self.frequency_sld = wx.Slider(self.panel, value=2000,
                            minValue=20, maxValue=20000,
                            pos=(20, 20), size=(250, -1),
                            style=wx.SL_HORIZONTAL)

        self.frequency_sld.Bind(wx.EVT_SCROLL, self.OnFrequencyScroll)

        self.freq = wx.StaticText(self.panel, label='', pos=(20, 90))
        self.OnFrequencyScroll(None)

        self.column_1.Add(self.frequency_sld, 0, wx.ALL|wx.EXPAND, 5)
        self.column_1.Add(self.freq, 0, wx.ALL|wx.EXPAND, 5)

        self.column_1.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                                        0, wx.ALL|wx.EXPAND, 5)

        self.horizontal_1_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.column_1.Add(self.horizontal_1_1, 0, wx.ALL, 5)

        play_left = NewButton('Play Left', self.on_play_left)
        play_right = NewButton('Play Right', self.on_play_right)

        self.horizontal_1_1.Add(play_left, 0, wx.ALL, 5)
        self.horizontal_1_1.Add(play_right, 0, wx.ALL, 5)

        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self.frame)
        self.panel.Layout()

    def OnVolumeScroll(self, e):
        self.volume.SetLabel(
            'Volume:   {},   {}dBFS'.format(
                int(self.volume_sld.GetValue()),
                20 * np.log10(self.GetVolume())
            )
        )

    def GetVolume(self):
        EPSILON = 0.001
        volume = float(self.volume_sld.GetValue()) / 100
        volume = EPSILON ** (1 - volume)
        return volume if volume > EPSILON else 0.0

    def OnFrequencyScroll(self, e):
        self.freq.SetLabel('Frequency:   {} Hz'.format(self.frequency_sld.GetValue()))

    def on_play_left(self, event):
        self.on_play(event, 'left')

    def on_play_right(self, event):
        self.on_play(event, 'right')

    def on_play(self, event, side='left'):
        try:
            volume = self.GetVolume()
            freq = float(self.frequency_sld.GetValue())

            p = pyaudio.PyAudio()

            rate = 192000 * 2
            stream = p.open(format=pyaudio.paFloat32,
                            channels=2,
                            rate=rate,
                            output=True)

            signal = np.sin(2 * np.pi * np.arange(rate * 3) * freq / rate) * volume / 5

            stereo_signal = np.zeros([len(signal), 2])
            if side == 'left':
                stereo_signal[:, 0] = signal
            else:
                stereo_signal[:, 1] = signal

            stream.write(np.concatenate(stereo_signal).astype(np.float32).tostring())
            stream.stop_stream()
            stream.close()

            p.terminate()

        except Exception as e:
            print str(e)
            self.statusbar.SetStatusText('Wrong frequency')
        self.Refresh()

    def Refresh(self):
        self.panel.Refresh()

if __name__ == '__main__':
    app = FreqSimulatorApp()
    app.MainLoop()
