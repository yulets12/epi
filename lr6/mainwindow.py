from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTableWidgetItem
from matplotlib import pyplot as plt
from cocomo import *
from math import ceil


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('D:/studying/epi/lr6/mainwindow.ui', self)

        self.table_budget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_budget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_worktime.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_worktime.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.btn_calculate.clicked.connect(self.calculate)
        self.btn_analyze.clicked.connect(self.analyze)

        self.show()

    def calculate(self):
        accuracy = 3
        lc_clean, tc_clean = self.get_costs()
        lc = round(lc_clean * 1.08, accuracy)  # 100% + 8% for planning
        tc = round(tc_clean * 1.36, accuracy)  # 100% + 36% for planning

        self.label_lc.setText(f'Трудоемкость: {lc}')
        self.label_tc.setText(f'Время разработки: {tc}')

        budget = [0.04, 0.12, 0.44, 0.06, 0.14, 0.07, 0.07, 0.06, 1]
        labor_costs = [0.08, 0.18, 0.25, 0.26, 0.31, 1, 1.08]
        time_costs = [0.36, 0.36, 0.18, 0.18, 0.28, 1, 1.36]
        for i in range(len(budget)):
            self.table_budget.setItem(i + 1, 1, QTableWidgetItem(str(round(100 * budget[i], accuracy))))
            self.table_budget.setItem(i + 1, 2, QTableWidgetItem(str(round(lc * budget[i], accuracy))))
        for i in range(len(labor_costs)):
            self.table_worktime.setItem(i + 1, 1, QTableWidgetItem(str(round(lc_clean * labor_costs[i], accuracy))))
            self.table_worktime.setItem(i + 1, 2, QTableWidgetItem(str(round(tc_clean * time_costs[i], accuracy))))

        y = list()
        for i in range(5):
            t = tc_clean * time_costs[i]
            y.extend([ceil(lc_clean * labor_costs[i] / t)] * round(t))

        x = [i + 1 for i in range(len(y))]

        plt.bar(x, y)
        for xi in x:
            plt.annotate(str(y[xi - 1]), (xi, y[xi - 1]), ha='center')
        plt.show()

    def calc_eaf(self):
        RELY = params_table['RELY'][self.cbox_rely.currentIndex()]
        DATA = params_table['DATA'][self.cbox_data.currentIndex()]
        CPLX = params_table['CPLX'][self.cbox_cplx.currentIndex()]
        TIME = params_table['TIME'][self.cbox_time.currentIndex()]
        STOR = params_table['STOR'][self.cbox_stor.currentIndex()]
        VIRT = params_table['VIRT'][self.cbox_virt.currentIndex()]
        TURN = params_table['TURN'][self.cbox_turn.currentIndex()]
        ACAP = params_table['ACAP'][self.cbox_acap.currentIndex()]
        AEXP = params_table['AEXP'][self.cbox_aexp.currentIndex()]
        PCAP = params_table['PCAP'][self.cbox_pcap.currentIndex()]
        VEXP = params_table['VEXP'][self.cbox_vexp.currentIndex()]
        LEXP = params_table['LEXP'][self.cbox_lexp.currentIndex()]
        MODP = params_table['MODP'][self.cbox_modp.currentIndex()]
        TOOL = params_table['TOOL'][self.cbox_tool.currentIndex()]
        SCED = params_table['SCED'][self.cbox_sced.currentIndex()]

        return RELY * DATA * CPLX * TIME * STOR * VIRT * TURN * ACAP * AEXP * PCAP * VEXP * LEXP * MODP * TOOL * SCED

    @staticmethod
    def get_size(entry):
        try:
            res = float(entry.text())
        except ValueError:
            entry.setStyleSheet("background:#f88;")
            raise ValueError()

        entry.setStyleSheet("background:#fff;")
        return res

    def get_costs(self):
        size = 0
        mode = self.cbox_mode.currentIndex()
        try:
            size = self.get_size(self.entry_size)
        except ValueError:
            pass

        lc = labor_costs(mode, self.calc_eaf(), size)
        tc = time_costs(mode, lc)
        return lc, tc

    def analyze(self):
        x = range(1, 4)
        size = 100
        for mode in range(3):
            cplx_i = [0, 2, 4]
            fig, axes = plt.subplots(3, 2)
            for cplx_num in range(len(cplx_i)):
                acap_lc = list()
                acap_tc = list()
                aexp_lc = list()
                aexp_tc = list()
                pcap_lc = list()
                pcap_tc = list()
                lexp_lc = list()
                lexp_tc = list()
                for i in x:
                    lc = labor_costs(mode, params_table['ACAP'][i] * params_table['CPLX'][cplx_i[cplx_num]], size)
                    acap_lc.append(lc)
                    acap_tc.append(time_costs(mode, lc))

                    lc = labor_costs(mode, params_table['AEXP'][i] * params_table['CPLX'][cplx_i[cplx_num]], size)
                    aexp_lc.append(lc)
                    aexp_tc.append(time_costs(mode, lc))

                    lc = labor_costs(mode, params_table['PCAP'][i] * params_table['CPLX'][cplx_i[cplx_num]], size)
                    pcap_lc.append(lc)
                    pcap_tc.append(time_costs(mode, lc))

                    lc = labor_costs(mode, params_table['LEXP'][i] * params_table['CPLX'][cplx_i[cplx_num]], size)
                    lexp_lc.append(lc)
                    lexp_tc.append(time_costs(mode, lc))

                plt.suptitle(f'Трудозатраты(слева), время(справа) при разных CPLX. mode={mode}\n'
                             f'Красный - ACAP, зеленый - AEXP, синий = PCAP, желтый - LEXP')
                axes[cplx_num][0].plot(x, acap_lc, 'r', x, aexp_lc, 'g', x, pcap_lc, 'b', x, lexp_lc, 'y')
                axes[cplx_num][1].plot(x, acap_tc, 'r', x, aexp_tc, 'g', x, pcap_tc, 'b', x, lexp_tc, 'y')
                plt.show()
                cplx_num += 1
