import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfilt, sosfreqz, sosfiltfilt
from scipy.fft import fft
import sounddevice as sd

#２回拍手されるまで待つ関数 拍手する速さによって検出されたりされなかったり（変えれる）
def wait_hands_clap():
    # バンドパスフィルタの適用関数
    def bandpass_filter(data, lowcut, highcut, fs, order=4):
        sos = butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos')
        return sosfiltfilt(sos, data)

    # 音声録音の設定
    Fs = 44100
    #nChannels = 2
    recDuration = 0.4 #録音１回の時間

    amplitude_border = 0.20
    clap_cnt = 0
    rec_cnt = 1
    while clap_cnt != 2:
        # 音声録音
        #print("Recording...")
        data = sd.rec(int(Fs * recDuration), samplerate=Fs, channels=1, dtype='float64')
        sd.wait()  # 録音終了を待つ

        # FFT解析
        N = len(data)
        frequencies = np.fft.rfftfreq(N, 1/Fs)  # 正の周波数成分
        data_fft = np.abs(np.fft.rfft(data.flatten()) / N)

        # 700 Hzから2300 Hzまでの振幅の平均値を計算
        idx_700Hz = np.argmax(frequencies >= 700)  # 700 Hz以上の最初のインデックス
        idx_2300Hz = np.argmax(frequencies > 2300)  # 2300 Hz以下の最後のインデックス
        amplitude_sum = np.sum(data_fft[idx_700Hz:idx_2300Hz])

        print(f"700 Hzから2300 Hzまでの振幅の合計: {amplitude_sum:.4f}")
        if rec_cnt == 2 or rec_cnt == 3:
            if amplitude_sum > amplitude_border:
                clap_cnt += 1
            rec_cnt += 1
        elif rec_cnt > 3:
            rec_cnt = 1
            clap_cnt = 0

        if rec_cnt == 1 and amplitude_sum > amplitude_border:
            clap_cnt += 1
            rec_cnt += 1
        print(f"clap_cnt: {clap_cnt}", f"rec_cnt: {rec_cnt}")
    print("clap!")
    return True