# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account Payment Boleto module for Odoo
#    Copyright (C) 2012-2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Miléo <mileo@kmee.com.br>
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

from openerp import models, fields, api
from ..boleto.document import getBoletoSelection
from openerp.exceptions import ValidationError

selection = getBoletoSelection()


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    boleto_carteira = fields.Char('Carteira', size=3)
    boleto_modalidade = fields.Char('Modalidade', size=2)
    boleto_convenio = fields.Char(u'Codigo convênio', size=10)
    boleto_variacao = fields.Char(u'Variação', size=2)
    boleto_cnab_code = fields.Char(u'Código Cnab', size=20)
    boleto_aceite = fields.Selection(
        [('S', 'Sim'), ('N', 'Não')], string='Aceite', default='N')
    boleto_type = fields.Selection(
        selection, string="Boleto")
    boleto_tipo_documento = fields.Selection([
        ('1', u'Tradicional'),
        ('2', u'Escritural')
    ], string=u'Tipo de Documento', default='1')
    boleto_especie = fields.Selection([
        ('02', u'DM - Duplicada Mercantil'),
        ('04', u'DS - Duplicada de Serviço'),
        ('12', u'NP - Nota Promissória'),
        ('13', u'NR - Nota Promissória Rural'),
        ('17', u'RC - Recibo'),
        ('20', u'AP - Apólice de Seguro'),
        ('32', u'BDP - Boleto de Proposta'),
        ('97', u'CH - Cheque'),
        ('98', u'ND - Nota Promissória Direta'),
    ], string=u'Espécie do Título', default='01')
    boleto_protesto = fields.Selection([
        ('0', u'Não Protestar'),
        ('1', u'Protestar (Dias Corridos)'),
        ('2', u'Protestar (Dias Úteis)'),
        ('3', u'Utilizar Perfil Beneficiário'),
        ('8', u'Cancelamento de Protesto Automático')
    ], string=u'Códigos para Protesto', default='0')
    boleto_protesto_prazo = fields.Char(u'Prazo protesto', size=2)
    boleto_baixa = fields.Selection([
        ('1', u'Baixar/Devolver'),
        ('2', u'Não Baixar/Não Devolver'),
        ('3', u'Utilizar Perfil Beneficiário')
    ], string=u'Código para Baixa/Devolução', default='1')
    boleto_baixa_prazo = fields.Char(u'Número de dias para Baixa/Devolução ', size=2)
    boleto_mora = fields.Selection([
        ('1', u'Valor por dia - Informar no campo o valor/dia a mora a ser cobrada.'),
        ('2', u'Taxa Mensal - Informar no campo taxa mensal o percentual a ser aplicado sobre valor do titulo que será'
              u' calculado por dia de atraso.'),
        ('3', u'Isento'),
        ('4', u'Utilizar comissão permanência do Banco por dia de atraso'),
        ('5', u'Tolerância valor por dia (cobrar juros a partir de'),
        ('6', u'Tolerância taxa mensal (cobrar juros a partir de')
    ], string=u'Código para juros de Mora', default='3')
    boleto_mora_juros = fields.Char(u'Juros de Mora', help=u'Informe o juro usando ponto e não vírgula.', size=5)

    @api.constrains('boleto_type', 'boleto_carteira',
                    'boleto_modalidade', 'boleto_convenio',
                    'boleto_variacao', 'boleto_aceite')
    def boleto_restriction(self):
        if self.boleto_type == '6' and not self.boleto_carteira:
            raise ValidationError(u'Carteira no banco Itaú é obrigatória')
