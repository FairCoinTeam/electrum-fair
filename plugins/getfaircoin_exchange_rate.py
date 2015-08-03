from PyQt4.QtGui import *
from PyQt4.QtCore import *

import datetime
import decimal
import requests
import json
import threading
import time
import re
from ssl import SSLError
from decimal import Decimal

from electrum_fair.bitcoin import COIN
from electrum_fair.plugins import BasePlugin, hook
from electrum_fair.i18n import _
from electrum_fair_gui.qt.util import *
from electrum_fair_gui.qt.amountedit import AmountEdit


EXCHANGES = ["chain.fair-coin.org",
             "getfaircoin.net"]

class GetfaircoinExchange(threading.Thread):

    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.daemon = True
        self.parent = parent
        self.quote_currencies = None
        self.lock = threading.Lock()
        self.query_rates = threading.Event()
        self.use_exchange = self.parent.config.get('use_getfaircoin_exchange', "chain.fair-coin.org")
        self.parent.exchanges = EXCHANGES
        #self.parent.win.emit(SIGNAL("refresh_exchanges_combo()"))
        #self.parent.win.emit(SIGNAL("refresh_currencies_combo()"))
        self.is_running = False

    def get_json(self, site, get_string):
        resp = requests.request('GET', 'https://' + site + get_string, headers={"User-Agent":"Electrum for FairCoin"})
        return resp.json()
        
    def exchange(self, btc_amount, quote_currency):
        with self.lock:
            if self.quote_currencies is None:
                return None
            quote_currencies = self.quote_currencies.copy()
        if quote_currency not in quote_currencies:
            return None
        return btc_amount * Decimal(str(quote_currencies[quote_currency]))

    def stop(self):
        self.is_running = False

    def update_rate(self):
        self.use_exchange = self.parent.config.get('use_getfaircoin_exchange', "chain.fair-coin.org")
        update_rates = {
            "chain.fair-coin.org": self.update_chain,
            "getfaircoin.net": self.update_gf,
        }
        try:
            rates = update_rates[self.use_exchange]()
        except Exception as e:
            self.parent.print_error(e)
            rates = {}
        with self.lock:
            self.quote_currencies = rates
            self.parent.set_currencies(rates)

    def run(self):
        self.is_running = True
        while self.is_running:
            self.query_rates.clear()
            self.update_rate()
            self.query_rates.wait(150)


    def update_chain(self):
        jsonresp = self.get_json('chain.fair-coin.org', "/download/ticker")
        return dict([(r, Decimal(str(jsonresp[r]["last"]))) for r in jsonresp])

    def update_gf(self):
        jsonresp = self.get_json('getfaircoin.net', "/api/ticker")
        return dict([(r, Decimal(str(jsonresp[r]["last"]))) for r in jsonresp])

class Plugin(BasePlugin):

    def __init__(self,a,b):
        BasePlugin.__init__(self,a,b)
        self.currencies = [self.fiat_unit()]
        self.exchanges = [self.config.get('use_getfaircoin_exchange', "chain.fair-coin.org")]
        # Do price discovery
        self.exchanger = GetfaircoinExchange(self)
        self.exchanger.start()
        self.win = None

    @hook
    def init_qt(self, gui):
        self.gui = gui
        self.win = self.gui.main_window
        self.win.connect(self.win, SIGNAL("refresh_currencies()"), self.win.update_status)
        self.btc_rate = Decimal("0.0")
        self.tx_list = {}
        self.gui.exchanger = self.exchanger #
        self.add_send_edit()
        self.add_receive_edit()
        self.win.update_status()

    def close(self):
        BasePlugin.close(self)
        self.exchanger.stop()
        self.exchanger = None
        self.gui.exchanger = None
        self.send_fiat_e.hide()
        self.receive_fiat_e.hide()
        self.win.update_status()

    def set_currencies(self, currency_options):
        self.currencies = sorted(currency_options)
        if self.win:
            self.win.emit(SIGNAL("refresh_currencies()"))
            self.win.emit(SIGNAL("refresh_currencies_combo()"))

    @hook
    def get_fiat_balance_text(self, btc_balance, r):
        # return balance as: 1.23 USD
        r[0] = self.create_fiat_balance_text(Decimal(btc_balance) / COIN)

    def get_fiat_price_text(self, r):
        # return BTC price as: 123.45 USD
        r[0] = self.create_fiat_balance_text(1)
        quote = r[0]
        if quote:
            r[0] = "%s"%quote

    @hook
    def get_fiat_status_text(self, btc_balance, r2):
        # return status as:   (1.23 USD)    1 BTC~123.45 USD
        text = ""
        r = {}
        self.get_fiat_price_text(r)
        quote = r.get(0)
        if quote:
            price_text = "1 FAIR~%s"%quote
            fiat_currency = quote[-3:]
            btc_price = self.btc_rate
            fiat_balance = Decimal(btc_price) * Decimal(btc_balance) / COIN
            balance_text = "(%.2f %s)" % (fiat_balance,fiat_currency)
            text = "  " + balance_text + "     " + price_text + " "
        r2[0] = text

    def create_fiat_balance_text(self, btc_balance):
        quote_currency = self.fiat_unit()
        self.exchanger.use_exchange = self.config.get("use_getfaircoin_exchange", "chain.fair-coin.org")
        cur_rate = self.exchanger.exchange(Decimal("1.0"), quote_currency)
        if cur_rate is None:
            quote_text = ""
        else:
            quote_balance = btc_balance * Decimal(cur_rate)
            self.btc_rate = cur_rate
            quote_text = "%.2f %s" % (quote_balance, quote_currency)
        return quote_text

    @hook
    def load_wallet(self, wallet, window):
        tx_list = {}
        for item in self.wallet.get_history(self.wallet.storage.get("current_account", None)):
            tx_hash, conf, value, timestamp, balance = item
            tx_list[tx_hash] = {'value': value, 'timestamp': timestamp }

        self.tx_list = tx_list
        self.cur_exchange = self.config.get('use_getfaircoin_exchange', "chain.fair-coin.org")

    def requires_settings(self):
        return True

    def settings_widget(self, window):
        return EnterButton(_('Settings'), self.settings_dialog)

    def settings_dialog(self):
        d = QDialog()
        d.setWindowTitle("Settings")
        layout = QGridLayout(d)
        layout.addWidget(QLabel(_('Exchange rate API: ')), 0, 0)
        layout.addWidget(QLabel(_('Currency: ')), 1, 0)
        combo = QComboBox()
        combo_ex = QComboBox()
        ok_button = QPushButton(_("OK"))

        def on_change(x):
            try:
                cur_request = str(self.currencies[x])
            except Exception:
                return
            if cur_request != self.fiat_unit():
                self.config.set_key('currency', cur_request, True)
                self.win.update_status()
                try:
                    self.fiat_button
                except:
                    pass
                else:
                    self.fiat_button.setText(cur_request)

        def on_change_ex(x):
            cur_request = str(self.exchanges[x])
            if cur_request != self.config.get('use_getfaircoin_exchange', "chain.fair-coin.org"):
                self.config.set_key('use_getfaircoin_exchange', cur_request, True)
                self.currencies = []
                combo.clear()
                self.exchanger.query_rates.set()
                set_currencies(combo)
                self.win.update_status()

        def set_currencies(combo):
            try:
                combo.blockSignals(True)
                current_currency = self.fiat_unit()
                combo.clear()
            except Exception:
                return
            combo.addItems(self.currencies)
            try:
                index = self.currencies.index(current_currency)
            except Exception:
                index = 0
            combo.blockSignals(False)
            combo.setCurrentIndex(index)

        def set_exchanges(combo_ex):
            try:
                combo_ex.clear()
            except Exception:
                return
            combo_ex.addItems(self.exchanges)
            try:
                index = self.exchanges.index(self.config.get('use_getfaircoin_exchange', "chain.fair-coin.org"))
            except Exception:
                index = 0
            combo_ex.setCurrentIndex(index)

        def ok_clicked():
            if self.config.get('use_getfaircoin_exchange', "chain.fair-coin.org") in ["CoinDesk", "itBit"]:
                self.exchanger.query_rates.set()
            d.accept();

        set_exchanges(combo_ex)
        set_currencies(combo)
        combo.currentIndexChanged.connect(on_change)
        combo_ex.currentIndexChanged.connect(on_change_ex)
        combo.connect(self.win, SIGNAL('refresh_currencies_combo()'), lambda: set_currencies(combo))
        combo_ex.connect(d, SIGNAL('refresh_exchanges_combo()'), lambda: set_exchanges(combo_ex))
        ok_button.clicked.connect(lambda: ok_clicked())
        layout.addWidget(combo,1,1)
        layout.addWidget(combo_ex,0,1)
        layout.addWidget(ok_button,3,1)

        if d.exec_():
            return True
        else:
            return False

    def fiat_unit(self):
        return self.config.get("currency", "EUR")

    def add_send_edit(self):
        self.send_fiat_e = AmountEdit(self.fiat_unit)
        btc_e = self.win.amount_e
        fee_e = self.win.fee_e
        self.connect_fields(btc_e, self.send_fiat_e, fee_e)
        self.win.send_grid.addWidget(self.send_fiat_e, 4, 3, Qt.AlignHCenter)
        btc_e.frozen.connect(lambda: self.send_fiat_e.setFrozen(btc_e.isReadOnly()))

    def add_receive_edit(self):
        self.receive_fiat_e = AmountEdit(self.fiat_unit)
        btc_e = self.win.receive_amount_e
        self.connect_fields(btc_e, self.receive_fiat_e, None)
        self.win.receive_grid.addWidget(self.receive_fiat_e, 2, 3, Qt.AlignHCenter)

    def connect_fields(self, btc_e, fiat_e, fee_e):
        def fiat_changed():
            try:
                fiat_amount = Decimal(str(fiat_e.text()))
            except:
                btc_e.setText("")
                if fee_e: fee_e.setText("")
                return
            exchange_rate = self.exchanger.exchange(Decimal("1.0"), self.fiat_unit())
            if exchange_rate is not None:
                btc_amount = fiat_amount/exchange_rate
                btc_e.setAmount(int(btc_amount*Decimal(COIN)))
                if fee_e: self.win.update_fee(False)
        fiat_e.textEdited.connect(fiat_changed)
        def btc_changed():
            if self.exchanger is None:
                return
            btc_amount = btc_e.get_amount()
            if btc_amount is None:
                fiat_e.setText("")
                return
            fiat_amount = self.exchanger.exchange(Decimal(btc_amount)/Decimal(COIN), self.fiat_unit())
            if fiat_amount is not None:
                pos = fiat_e.cursorPosition()
                fiat_e.setText("%.2f"%fiat_amount)
                fiat_e.setCursorPosition(pos)
        btc_e.textEdited.connect(btc_changed)
