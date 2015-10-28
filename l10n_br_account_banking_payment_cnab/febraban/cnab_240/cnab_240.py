# coding: utf-8
# ###########################################################################
#
#    Author: Luis Felipe Mileo
#            Fernando Marcato Rodrigues
#            Daniel Sadamo Hirayama
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

from ..cnab import Cnab
from cnab240.tipos import Arquivo
from cnab240.tipos import Evento
from cnab240.tipos import Lote
from decimal import Decimal
from openerp.addons.l10n_br_base.tools.misc import punctuation_rm
import datetime
import re
import string
import unicodedata
import time


class Cnab240(Cnab):
    """

    """
    def __init__(self):
        super(Cnab, self).__init__()

    @staticmethod
    def get_bank(bank):
        if bank == '341':
            from bancos.itau import Itau240
            return Itau240
        elif bank == '237':
            from bancos.bradesco import Bradesco240
            return Bradesco240
        elif bank == '104':
            from bancos.cef import Cef240
            return Cef240
        elif bank == '033':
            from bancos.santander import Santander240
            return Santander240
        else:
            return Cnab240

    @staticmethod
    def get_cnab_bank(bank):
        if bank == '341':
            from cnab240.bancos import itau
            return itau
        elif bank == '033':
            from cnab240.bancos import santander
            return santander
        else:
            raise NotImplementedError

    @property
    def inscricao_tipo(self):
        # TODO: Implementar codigo para PIS/PASEP
        if self.order.company_id.partner_id.is_company:
            return 2
        else:
            return 1

    def _prepare_header(self):
        """

        :param:
        :return:
        """
        data_de_geracao = self.order.date_created[8:11] + self.order.date_created[5:7] + self.order.date_created[0:4]
        t = datetime.datetime.now() - datetime.timedelta(hours=3)  # FIXME
        hora_de_geracao = t.strftime("%H%M%S")

        return {
            'arquivo_data_de_geracao': int(data_de_geracao),
            'arquivo_hora_de_geracao': int(hora_de_geracao),
            # TODO: Numero sequencial de arquivo
            'arquivo_sequencia': 1,
            'cedente_inscricao_tipo': self.inscricao_tipo,
            'cedente_inscricao_numero': int(punctuation_rm(self.order.company_id.cnpj_cpf)),
            'cedente_agencia': int(self.order.mode.bank_id.bra_number),
            'cedente_conta': int(self.order.mode.bank_id.acc_number),
            'cedente_agencia_conta_dv': int(self.order.mode.bank_id.acc_number_dig),
            'cedente_nome': self.order.company_id.legal_name,
            'cedente_agencia_dv': int(self.order.mode.bank_id.bra_number_dig),
            # nao eh necessario o campo abaixo pois ja esta definido no cnab240
            # 'arquivo_codigo': 1,  # Remessa/Retorno
            'reservado_cedente_campo': u'REMESSA-TESTE',
            # nao eh necessario o campo abaixo pois ja esta definido no cnab240
            # 'servico_operacao': u'R',
            'codigo_transmissao': int(self.order.mode.boleto_cnab_code),

        }

    def format_date(self, srt_date):
        return int(datetime.datetime.strptime(
            srt_date, '%Y-%m-%d').strftime('%d%m%Y'))

    def nosso_numero(self, format):
        pass

    def cep(self, format):
        sulfixo = format[-3:]
        prefixo = format[:5]
        return prefixo, sulfixo

    def sacado_inscricao_tipo(self, partner_id):
        # TODO: Implementar codigo para PIS/PASEP
        if partner_id.is_company:
            return 2
        else:
            return 1

    def rmchar(self, format):
        return re.sub('[%s]' % re.escape(string.punctuation), '', format or '')

    def _prepare_segmento(self, line):
        """

        :param line:
        :return:
        """
        prefixo, sulfixo = self.cep(line.partner_id.zip)
        if self.order.mode.boleto_aceite == 'S':
            aceite = 'A'
        else:
            aceite = 'N'
        return {
            'cedente_agencia': int(self.order.mode.bank_id.bra_number),
            'cedente_agencia_dv': int(self.order.mode.bank_id.bra_number_dig),
            'cedente_conta': int(self.order.mode.bank_id.acc_number),
            'cedente_conta_dv': int(self.order.mode.bank_id.acc_number_dig),
            'identificacao_titulo': u'%s' % str(line.move_line_id.move_id.id),
            'numero_documento': line.move_line_id.invoice.internal_number,
            'vencimento_titulo': self.format_date(line.ml_maturity_date),
            'valor_titulo': Decimal("{0:,.2f}".format(line.move_line_id.debit)),
            'especie_titulo': int(self.order.mode.boleto_especie),
            'aceite_titulo': u'%s' % aceite,
            'data_emissao_titulo': self.format_date(line.ml_date_created),
            'juros_mora_taxa_dia': Decimal("{0:,.2f}".format(line.move_line_id.debit * 0.00066666667)),
            'valor_abatimento': Decimal('0.00'),
            'sacado_inscricao_tipo': int(
                self.sacado_inscricao_tipo(line.partner_id)),
            'sacado_inscricao_numero': int(
                self.rmchar(line.partner_id.cnpj_cpf)),
            'sacado_nome': line.partner_id.legal_name,
            'sacado_endereco': (
                line.partner_id.street + ' ' + line.partner_id.number),
            'sacado_bairro': line.partner_id.district,
            'sacado_cep': int(prefixo),
            'sacado_cep_sufixo': int(sulfixo),
            'sacado_cidade': line.partner_id.l10n_br_city_id.name,
            'sacado_uf': line.partner_id.state_id.code,
            'codigo_protesto': int(self.order.mode.boleto_protesto),
            'prazo_protesto': int(self.order.mode.boleto_protesto),
            'codigo_baixa': int(self.order.mode.boleto_baixa),
            'prazo_baixa': int(self.order.mode.boleto_baixa_prazo)
        }

    def remessa(self, order):
        """

        :param order:
        :return:
        """
        self.order = order
        banco_num = self.order.mode.bank_id.bank_bic
        banco = self.get_cnab_bank(banco_num)
        self.arquivo = Arquivo(self.bank, **self._prepare_header())
        codigo_evento = 1
        evento = Evento(self.bank, codigo_evento)

        count = 0
        for line in order.line_ids:

            seg = self._prepare_segmento(line)
            if int(banco_num) == 33:
                seg_s = banco.registros.SegmentoS(**seg)
            if seg_s.mensagem_recibo_pagador == 2 and count == 0:
                evento.adicionar_segmento(seg_s)
                count += 1

            seg_p = banco.registros.SegmentoP(**seg)
            evento.adicionar_segmento(seg_p)

            seg_q = banco.registros.SegmentoQ(**seg)
            evento.adicionar_segmento(seg_q)

            seg_r = banco.registros.SegmentoR(**seg)
            if seg_r.necessario():
                evento.adicionar_segmento(seg_r)

            if (banco_num) == 33:
                seg_s = banco.registros.SegmentoS(**seg)
                if seg_s.mensagem_recibo_pagador == 4:
                    evento.adicionar_segmento(seg_s)
        lote_cobranca = self.arquivo.encontrar_lote(codigo_evento)

        if lote_cobranca is None:
            header = banco.registros.HeaderLoteCobranca(**self.arquivo.header.todict())
            trailer = banco.registros.TrailerLoteCobranca()
            lote_cobranca = Lote(self.bank, header, trailer)
            self.arquivo.adicionar_lote(lote_cobranca)

        if header.controlecob_numero is None:
            header.controlecob_numero = int('{0}{1:02}'.format(
                self.arquivo.header.arquivo_sequencia, lote_cobranca.codigo))

        if header.controlecob_data_gravacao is None:
            header.controlecob_data_gravacao = self.arquivo.header.arquivo_data_de_geracao

        lote_cobranca.adicionar_evento(evento)
        self.arquivo.trailer.totais_quantidade_registros += len(evento)

        remessa = unicode(self.arquivo)
        return unicodedata.normalize(
            'NFKD', remessa).encode('ascii', 'ignore')

    @staticmethod
    def data_hoje(self):
        return int(time.strftime("%d%m%Y"))

    @staticmethod
    def hora_agora(self):
        return int(time.strftime("%H%M%S"))
