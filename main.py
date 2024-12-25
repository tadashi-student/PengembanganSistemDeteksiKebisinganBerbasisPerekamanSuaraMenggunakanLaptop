import os
import sys
import numpy as np
import sounddevice as sd
import wave
import requests
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

class LivePlotWidget(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(facecolor='white')
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: white;")
        self.ax.set_facecolor('white')

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_title("Grafik Dihapus")
        self.draw()

    def plot_time(self, data, sample_rate, time_range):
        self.ax.clear()
        t = np.linspace(0, len(data) / sample_rate, num=len(data))
        if len(t) > 0:
            if t[-1] > time_range:
                start_idx = np.searchsorted(t, t[-1] - time_range)
                t = t[start_idx:]
                data = data[start_idx:]
        self.ax.plot(t, data, label="Domain Waktu", color='green')
        self.ax.set_title("Sinyal dalam Domain Waktu")
        self.ax.set_xlabel("Waktu [s]")
        self.ax.set_ylabel("Amplitudo")
        self.ax.set_xlim(t[0] if len(t) > 0 else 0, t[-1] if len(t) > 0 else time_range)
        self.ax.legend(loc='upper right')

        if len(data) > 0:
            dB = self.calculate_average_dB(data)
            dB_text = f"Desibel Rata-rata: {dB:.2f} dB"
            self.ax.text(0.05, 0.95, dB_text, transform=self.ax.transAxes,
                         fontsize=12, color='red', ha='left', va='top',
                         bbox=dict(facecolor='white', alpha=0.7))

        self.draw()

    def calculate_average_dB(self, data):
        ref_amplitude = 2e-5
        rms_amplitudes = [np.sqrt(np.mean(chunk**2)) for chunk in np.array_split(data, max(len(data) // 4410, 1))]
        avg_rms_amplitude = np.mean(rms_amplitudes)
        dB = 20 * np.log10(avg_rms_amplitude / ref_amplitude) if avg_rms_amplitude > 0 else -np.inf
        return dB

    def plot_frequency(self, data, sample_rate, time_range):
        self.ax.clear()
        if len(data) > 0:
            window = np.hamming(len(data))
            data_windowed = data * window
            freqs = np.fft.rfftfreq(len(data), 1 / sample_rate)
            magnitude = np.abs(np.fft.rfft(data_windowed))
            magnitude = magnitude / np.max(magnitude) if np.max(magnitude) > 0 else magnitude
            self.ax.plot(freqs, magnitude, label="Domain Frekuensi")
        self.ax.set_title("Sinyal dalam Domain Frekuensi")
        self.ax.set_xlabel("Frekuensi [Hz]")
        self.ax.set_ylabel("Magnitudo Ternormalisasi")
        self.ax.legend()
        self.draw()

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.sample_rate = 44100
        self.buffer = np.array([])
        self.is_recording = False
        self.time_range = 5
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

        self.api_url = "https://ingestion.edgeimpulse.com/api/testing/files"
        self.api_key = "ei_ce6953680d8a478f33ac818e5bbd5f73e697d75fb69ed231"
        self.label = "Kebisingan"

    def init_ui(self):
        self.setWindowTitle("Pendeteksi kebisingan")
        self.setGeometry(100, 100, 1000, 800)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setStyleSheet("background-color: #f0f0f0;")
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        self.title_label = QtWidgets.QLabel(self.centralwidget)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setText("<html><head/><body><p><span style=\"font-size:16pt; font-weight:600;\">Pendeteksi Kebisingan (Kelompok 1)</span></p></body></html>")
        self.gridLayout.addWidget(self.title_label, 0, 0, 1, 2)

        self.widget = LivePlotWidget(self.centralwidget)
        self.gridLayout.addWidget(self.widget, 1, 0, 1, 2)

        self.widget_2 = LivePlotWidget(self.centralwidget)
        self.gridLayout.addWidget(self.widget_2, 2, 0, 1, 2)

        self.groupBox = QtWidgets.QGroupBox("Controls", self.centralwidget)
        self.gridLayout.addWidget(self.groupBox, 3, 0, 1, 2)
        self.buttonLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.groupBox.setStyleSheet("background-color: #e0e0e0;")

        self.record_button = QtWidgets.QPushButton("Record", self.groupBox)
        self.record_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.record_button.clicked.connect(self.start_recording)
        self.buttonLayout.addWidget(self.record_button)

        self.stop_button = QtWidgets.QPushButton("Stop", self.groupBox)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_button.clicked.connect(self.stop_recording)
        self.buttonLayout.addWidget(self.stop_button)

        self.play_button = QtWidgets.QPushButton("Play", self.groupBox)
        self.play_button.setStyleSheet("background-color: #008CBA; color: white;")
        self.play_button.clicked.connect(self.play_audio)
        self.buttonLayout.addWidget(self.play_button)

        self.save_button = QtWidgets.QPushButton("Save", self.groupBox)
        self.save_button.setStyleSheet("background-color: #FF9800; color: white;")
        self.save_button.clicked.connect(self.save_audio)
        self.buttonLayout.addWidget(self.save_button)

        self.reset_button = QtWidgets.QPushButton("Reset", self.groupBox)
        self.reset_button.setStyleSheet("background-color: #9E9E9E; color: white;")
        self.reset_button.clicked.connect(self.reset_all)
        self.buttonLayout.addWidget(self.reset_button)

        self.result_label = QtWidgets.QLabel("Hasil Klasifikasi: -", self.centralwidget)
        self.result_label.setAlignment(QtCore.Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #3f51b5;")
        self.gridLayout.addWidget(self.result_label, 4, 0, 1, 2)

    def start_recording(self):
        self.is_recording = True
        self.buffer = np.array([])
        self.timer.start(100)
        self.result_label.setText("Sedang Merekam...")
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self.audio_callback)
        self.stream.start()

    def stop_recording(self):
        self.is_recording = False
        self.timer.stop()
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        self.result_label.setText("Proses selesai, simpan untuk klasifikasi.")

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.buffer = np.append(self.buffer, indata[:, 0])

    def update_plot(self):
        if self.is_recording and self.buffer.size > 0:
            normalized_data = self.buffer / np.max(np.abs(self.buffer)) if np.max(np.abs(self.buffer)) > 0 else self.buffer
            self.widget.plot_time(normalized_data, self.sample_rate, self.time_range)
            self.widget_2.plot_frequency(normalized_data, self.sample_rate, self.time_range)

    def play_audio(self):
        if len(self.buffer) > 0:
            sd.play(self.buffer, samplerate=self.sample_rate)
            sd.wait()

    def save_audio(self):
        if len(self.buffer) > 0:
            folder_path = "recordings"
            os.makedirs(folder_path, exist_ok=True)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(folder_path, f"recording_{current_time}.wav")
            scaled = np.int16(self.buffer / np.max(np.abs(self.buffer)) * 32767)
            with wave.open(filename, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(scaled.tobytes())
            QtWidgets.QMessageBox.information(self, "Save Audio", f"Audio saved to {filename}")

            self.result_label.setText("Mengklasifikasi...")
            QtCore.QTimer.singleShot(2000, lambda: self.perform_classification(filename))

    def perform_classification(self, audio_filename):
        dB = self.widget.calculate_average_dB(self.buffer)
        self.label = "Bising" if dB > 50 else "Tidak Bising"
        self.result_label.setText(f"Hasil Klasifikasi: {self.label}")
        self.upload_audio_to_edge_impulse(audio_filename)

    def upload_audio_to_edge_impulse(self, audio_filename):
        with open(audio_filename, "rb") as f:
            response = requests.post(
                self.api_url,
                headers={
                    "x-label": self.label,
                    "x-api-key": self.api_key,
                },
                files={"data": (os.path.basename(audio_filename), f, "audio/wav")},
            )
        if response.status_code == 200:
            QtWidgets.QMessageBox.information(self, "Upload Success", f"{audio_filename} uploaded successfully to Edge Impulse!")
        else:
            QtWidgets.QMessageBox.warning(self, "Upload Failed", f"Failed to upload {audio_filename}. Status: {response.status_code}")

    def reset_all(self):
        self.buffer = np.array([])
        self.is_recording = False
        self.widget.clear_plot()
        self.widget_2.clear_plot()
        self.timer.stop()
        self.result_label.setText("Hasil Klasifikasi: -")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = Ui_MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

