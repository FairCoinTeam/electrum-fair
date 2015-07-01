#!/usr/bin/env python
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2014 Thomas Voegtlin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import urllib
import json
import sys
import requests

from PyQt4.QtGui import QMessageBox, QApplication, QPushButton

from electrum_fair.account import BIP32_Account
from electrum_fair import bitcoin, util
from electrum_fair import transaction
from electrum_fair.plugins import BasePlugin, hook
from electrum_fair.i18n import _
from electrum_fair.bitcoin import regenerate_key



class Plugin(BasePlugin):

    button_label = _("Verify GA instant")

    @hook 
    def init_qt(self, gui):
        self.win = gui.main_window

    @hook
    def transaction_dialog(self, d):
        self.wallet = d.wallet
        self.verify_button = b = QPushButton(self.button_label)
        b.clicked.connect(lambda: self.do_verify(d.tx))
        d.buttons.insert(1, b)
        self.transaction_dialog_update(d)

    def get_my_addr(self, tx):
        """Returns the address for given tx which can be used to request
        instant confirmation verification from GreenAddress"""

        for addr, _ in tx.get_outputs():
            if self.wallet.is_mine(addr):
                return addr
        return None

    @hook
    def transaction_dialog_update(self, d):
        if d.tx.is_complete() and self.get_my_addr(d.tx):
            self.verify_button.show()
        else:
            self.verify_button.hide()

    def do_verify(self, tx):
        # 1. get the password and sign the verification request
        password = None
        if self.wallet.use_encryption:
            msg = _('GreenAddress requires your signature to verify that transaction is instant.\n'
                    'Please enter your password to sign a verification request.')
            password = self.win.password_dialog(msg)
            if not password:
                return
        try:
            self.verify_button.setText(_('Verifying...'))
            QApplication.processEvents()  # update the button label

            addr = self.get_my_addr(tx)
            message = "Please verify if %s is GreenAddress instant confirmed" % tx.hash()
            sig = self.wallet.sign_message(addr, message, password)

            # 2. send the request
            response = requests.request("GET", ("https://greenaddress.it/verify/?signature=%s&txhash=%s" % (urllib.quote(sig), tx.hash())),
                                        headers = {'User-Agent': 'Electrum'})
            response = response.json()

            # 3. display the result
            if response.get('verified'):
                QMessageBox.information(None, _('Verification successful!'),
                    _('%s is covered by GreenAddress instant confirmation') % (tx.hash()), _('OK'))
            else:
                QMessageBox.critical(None, _('Verification failed!'),
                    _('%s is not covered by GreenAddress instant confirmation') % (tx.hash()), _('OK'))
        except BaseException as e:
            import traceback
            traceback.print_exc(file=sys.stdout)
            QMessageBox.information(None, _('Error'), str(e), _('OK'))
        finally:
            self.verify_button.setText(self.button_label)
