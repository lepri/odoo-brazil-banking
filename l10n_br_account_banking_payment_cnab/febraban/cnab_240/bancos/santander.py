# coding: utf-8
# ###########################################################################
#
#    Author: Luis Felipe Mileo
#            Fernando Marcato Rodrigues
#            Daniel Sadamo Hirayama
#            Gustavo Lepri
#    Copyright 2015 KMEE - www.kmee.com.br
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from ..cnab_240 import Cnab240
import re
import string
from decimal import *


class Santander240(Cnab240):
    """

    """

    def __init__(self):
        """

        :return:
        """
        super(Cnab240, self).__init__()
        from cnab240.bancos import santander
        self.bank = santander

    def _prepare_header(self):
        """
        :param order:
        :return:
        """
        vals = super(Santander240, self)._prepare_header()
        vals['mensagem1'] = self.order.mode.instrucoes
        vals['mensagem2'] = self.order.mode.instrucoes2
        del vals['arquivo_hora_de_geracao']
        return vals

    def _prepare_segmento(self, line):
        """

        :param line:
        :return:
        """
        vals = super(Santander240, self)._prepare_segmento(line)

        carteira, nosso_numero, digito = self.nosso_numero(
            line.move_line_id.transaction_ref)

        vals['servico_codigo_movimento'] = 1  # 01 - Entrada de titulo
        vals['tipo_documento'] = int(self.order.mode.boleto_especie)
        if self.order.mode.boleto_type == '10':
            vals['forma_cadastramento'] = 1  # boleto registrado caso o boleto_type seja igual a 10 #TODO melhorar
            vals['tipo_cobranca'] = 5
        vals['carteira_numero'] = int(carteira)
        vals['nosso_numero'] = int(nosso_numero)
        vals['nosso_numero_dv'] = int(digito)
        vals['sacado_endereco'] = vals['sacado_endereco'][:40]
        vals['mensagem_recibo_pagador'] = 2
        vals['mensagem1'] = self.order.mode.instrucoes[:100]
        vals['mensagem2'] = self.order.mode.instrucoes2
        vals['conta_cobranca'] = int(self.order.mode.bank_id.acc_number)
        vals['conta_cobranca_dv'] = int(self.order.mode.bank_id.acc_number_dig)
        vals['codigo_juros_mora'] = int(self.order.mode.boleto_mora)
        vals['juros_mora_data'] = self.format_date(line.ml_maturity_date)
        vals['juros_mora_taxa'] = Decimal("{0:,.2f}".format(float(self.order.mode.boleto_mora_juros)))

        return vals

    def nosso_numero(self, format):
        digito = format[-1:]
        if self.order.mode.boleto_type == '10':
            carteira = 5
        nosso_numero = re.sub(
            '[%s]' % re.escape(string.punctuation), '', format[3:-1] or '')
        return carteira, nosso_numero, digito