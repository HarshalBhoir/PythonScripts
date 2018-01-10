from datetime import date,datetime, timedelta
from osv import osv,fields
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
import calendar
import re
from base.res import res_partner
from datetime import datetime#-----kirti 06 jan-#
import decimal_precision as dp


class invoice_search_master(osv.osv):

	_name="invoice.search.master"
	_columns = {
		'invoice_number':fields.char('Invoice Number',size=124),
		'cust_name':fields.char('Customer Name',size=124),
		'contact_name':fields.char('Contact Name',size=124),
		'pms':fields.many2one('product.product',"PMS",domain="[('type','=','service')]",),
		'contract_no':fields.many2one('sale.contract','Contract Number'),
		'state':fields.selection([('open','Opened'),('created','Created'),('printed','Printed'),('paid','Paid')],'State'),
		'cse':fields.many2one('hr.employee','CSE'),
		'search_invoice_line':fields.one2many('invoice.adhoc.master','search_id',''),
		'location':fields.many2one('res.partner.address','Location'),
		'contact_no':fields.char('Contact No',size=124),
		'invoice_type':fields.selection([('standard','Standard Invoice'),('adhoc','Adhoc Invoice'),('exempted','Exempted')],'Invoice Type'),
	}


	def search_invoice(self,cr,uid,ids,context=None):
		for temp in self.browse(cr,uid,ids):
			list_id = []
			Sql_Str = ''
			if temp.cust_name != False:
				Sql_Str = Sql_Str + " and IAM.cust_name ilike '" +"%"+ str(temp.cust_name) + "%'"
			if temp.contact_name != False:
				Sql_Str = Sql_Str +" and IAM.contact_name ilike '" +  "%" + str(temp.contact_name) + "%'"
			if temp.invoice_number != False:
				Sql_Str = Sql_Str + " and IAM.invoice_number ilike '" +"%"+ str(temp.invoice_number) + "%'"
			if temp.state != False:
				Sql_Str = Sql_Str + " and IAM.status ilike '" +"%"+ str(temp.state) + "%'"
			if temp.pms.id != False:
				Sql_Str = Sql_Str + " and IA.pms ='" +str(temp.pms.id) + "'"
			if temp.cse.id != False:
				Sql_Str = Sql_Str + " and IAM.cse ='" +str(temp.cse.id) + "'"
			if temp.contract_no.id != False:
				Sql_Str = Sql_Str + " and IAM.contract_no ='" +str(temp.contract_no.id) + "'"
			if temp.invoice_type == 'adhoc':
				Sql_Str = Sql_Str + " and IAM.adhoc_invoice = 't'"
			if temp.invoice_type == 'standard':
				Sql_Str = Sql_Str + " and IAM.adhoc_invoice = 'f' and IAM.exempted = 'f'"  
			if temp.invoice_type == 'exempted':
				Sql_Str = Sql_Str + " and IAM.exempted = 't'"
			#if temp.contact_no != False:
				#Sql_Str = Sql_Str + " and IAM.contact_no ilike '" +"%"+ str(temp.contact_no) + "%'"
			

			Main_Str = "select IAM.id from invoice_adhoc_master IAM,invoice_adhoc IA where IAM.id = IA.invoice_adhoc_id11"
			Main_Str2 = "select IAM.id from invoice_adhoc_master IAM,invoice_adhoc IA where IAM.id = IA.invoice_adhoc_id"

			Main_Str1 = Main_Str + Sql_Str
			cr.execute(Main_Str1)
			query_result2=cr.fetchall()
			for x in query_result2:
					self.pool.get('invoice.adhoc.master').write(cr,uid,x[0],{'search_id':temp.id})
					list_id.extend([x[0]])

			Main_Str3 = Main_Str2 + Sql_Str
			cr.execute(Main_Str3)
			query_result=cr.fetchall()
			for x in query_result:
					self.pool.get('invoice.adhoc.master').write(cr,uid,x[0],{'search_id':temp.id})
					list_id.extend([x[0]])

			rec = self.pool.get('invoice.adhoc.master').search(cr,uid,[('id','not in',list_id)])
			for part in self.pool.get('invoice.adhoc.master').browse(cr,uid,rec):
						self.pool.get('invoice.adhoc.master').write(cr,uid,part.id,{'search_id':False})				


	def clear_invoice(self,cr,uid,ids,context=None):	
		for k in self.browse(cr,uid,ids):		
			self.write(cr,uid,k.id,{'contact_name':None,'cust_name':None,'state':None,'invoice_number':None,'contract_no':None,
								'pms':None,'cse':None,'contact_no':None,'location':None,'invoice_type':None})

			for req in k.search_invoice_line:
				self.pool.get('invoice.adhoc.master').write(cr,uid,req.id,{'search_id':None})												
		return True									

invoice_search_master()

class invoice_adhoc_master(osv.osv):
	_name = 'invoice.adhoc.master'

	def _get_service_tax(self, cr, uid, context=None):		
		res={}
		tax_name = 'Service Tax (12.0)%'
		search_tax = self.pool.get('account.tax').search(cr,uid,[('name','ilike',tax_name)])
		if search_tax:
			return search_tax[0]
		else:
			return None

	def _get_edu_tax(self, cr, uid, context=None):		
		res={}
		tax_name = 'Edu Cess(2.0)%'
		search_tax = self.pool.get('account.tax').search(cr,uid,[('name','ilike',tax_name)])
		if search_tax:
			return search_tax[0]
		else:
			return None

	def _get_hs_edu(self, cr, uid, context=None):		
		res={}
		tax_name = 'Hs Edu(1.0)%'
		search_tax = self.pool.get('account.tax').search(cr,uid,[('name','ilike',tax_name)])
		if search_tax:
			return search_tax[0]
		else:
			return None


	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		cur_obj = self.pool.get('res.currency')
		res = {}
		service_tax_value = 0.0
		edu_tax_value = 0.0
		hs_edu_value = 0.0
		grand_total_value = 0.0
		total_tax = 0.0
		service_tax_value1 = 0.0
		edu_tax_value1 = 0.0
		hs_edu_value1 = 0.0
		grand_total_value1 = 0.0
		total_tax1 = 0.0
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
		        	'service_tax':0.0,
		        	'total_amount': 0.0,
				'edu_tax':0.0,
				'hs_edu':0.0,
				'grand_total':0.0,
				'total_tax':0.0,
		        	'service_tax1':0.0,
		        	'total_amount1': 0.0,
				'edu_tax1':0.0,
				'hs_edu1':0.0,
				'grand_total1':0.0,
				'total_tax1':0.0,

			}
			val = val1 = 0.0
			if order.exempted != True:
			    if order.adhoc_invoice == True:
				    for line in order.invoice_line_adhoc:
					   val1 += line.amount
				    res[order.id]['total_amount1'] = round(val1)
				    search_tax = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Service Tax (12.0)%')])
				    for tax in self.pool.get('account.tax').browse(cr,uid,search_tax):
					service_tax_value = (tax.amount*val1)
				    search_tax_edu = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Edu Cess(2.0)%')])
				    for tax in self.pool.get('account.tax').browse(cr,uid,search_tax_edu):
					edu_tax_value = (tax.amount*service_tax_value)
				    search_tax_hs_edu = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Hs Edu Cess(1.0)%')])
				    for tax in self.pool.get('account.tax').browse(cr,uid,search_tax_hs_edu):
					hs_edu_value = (tax.amount*service_tax_value)
				    total_tax= service_tax_value+edu_tax_value+hs_edu_value
				    grand_total_value = round((val1+service_tax_value+edu_tax_value+hs_edu_value))
				    res[order.id]['service_tax1'] = round(service_tax_value)
				    res[order.id]['edu_tax1'] = round(edu_tax_value)
				    res[order.id]['hs_edu1'] = round(hs_edu_value)
				    res[order.id]['grand_total1'] = round(grand_total_value)
				    res[order.id]['total_tax1'] = round(total_tax)
			    
			    elif order.adhoc_invoice != True:
				    for line in order.invoice_line_adhoc_11:
					   val1 += line.amount
				    res[order.id]['total_amount'] = round(val1)
				    search_tax = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Service Tax (12.0)%')])
				    for tax in self.pool.get('account.tax').browse(cr,uid,search_tax):
					service_tax_value = (tax.amount*val1)
				    search_tax_edu = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Edu Cess(2.0)%')])
				    for tax in self.pool.get('account.tax').browse(cr,uid,search_tax_edu):
					edu_tax_value = (tax.amount*service_tax_value)
				    search_tax_hs_edu = self.pool.get('account.tax').search(cr,uid,[('name','ilike','Hs Edu Cess(1.0)%')])
				    for tax in self.pool.get('account.tax').browse(cr,uid,search_tax_hs_edu):
					hs_edu_value = (tax.amount*service_tax_value)
				    total_tax= service_tax_value+edu_tax_value+hs_edu_value
				    grand_total_value = round((val1+service_tax_value+edu_tax_value+hs_edu_value))    
			    res[order.id]['service_tax'] = round(service_tax_value)
			    res[order.id]['edu_tax'] = round(edu_tax_value)
			    res[order.id]['hs_edu'] = round(hs_edu_value)
			    res[order.id]['grand_total'] = round(grand_total_value)
			    res[order.id]['total_tax'] = round(total_tax)
			else:
				if order.adhoc_invoice == True:
					for line in order.invoice_line_adhoc:
					   val1 += line.amount
					res[order.id]['total_amount'] = round(val1)
					res[order.id]['grand_total'] = round(val1)
				if order.adhoc_invoice != True:
					for line in order.invoice_line_adhoc_11:
					   val1 += line.amount
					res[order.id]['total_amount'] = round(val1)
					res[order.id]['grand_total'] = round(val1)
		return res

	_columns = {
		'service_tax_many2one':fields.many2one('account.tax',''),
		'edu_tax_many2one':fields.many2one('account.tax',''),
		'hs_edu_many2one':fields.many2one('account.tax',''),
		'search_id':fields.many2one('invoice.search.master',''),
		'exempted':fields.boolean('Exempted'),
		'adhoc_invoice':fields.boolean('Adhoc-Invoice'),
		'partner_id':fields.many2one('res.partner',''),
		'cust_name':fields.char('Customer Name',size=124),#make read only xml
		'invoice_date':fields.date('Invoice Date'),#
		'invoice_number':fields.char('Invoice Number',size=124),#
		'contract_no':fields.many2one('sale.contract','Contract Number'),
		'cse':fields.many2one('hr.employee','CSE'),#	
		'payment_term':fields.selection([('full_payment','Full Payment'),('advance','50% Advance & Balance 50% within 6 Months'),('quarter','Quarterly Payment'),('monthly','Monthly Payment'),('annual','Annual Payment')],'Payment Term'),
		'service_classification':fields.selection([('residential','Residential Service'),('commercial','Commercial Service'),('port','Port Service'),('airport','Airport Service'),('exempted','Exempted')],'Service Classification'),
		'cce':fields.many2one('res.users','CCE'),
		'billing_term':fields.char('Billing Term',size=124),
		'invoice_period_from':fields.date('Invoice Period'),
		'invoice_period_to':fields.date('To'),
		'invoice_due_date':fields.date('Invoice Due Date'),
		'status':fields.selection([('open','Open'),('printed','Printed'),('paid','Paid')],'Status'),
		'invoice_line_adhoc':fields.one2many('invoice.adhoc','invoice_adhoc_id',''),
		'history_invoice_adhoc':fields.one2many('payment.contract.history','history_adhoc_invoice_id',''),
		'purchase_order_number':fields.char('Purchase Order Number',size=124),
		'total_amount':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Total',help="The total amount.",multi="sum"),
		'total_tax':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Total Tax',multi='sum'),
		'service_tax':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Service Tax(12.0)%',help="The Service Tax.",multi='sum'),
		'edu_tax':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Edu Cess(2.0)%',multi='sum'),
		'hs_edu':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Hs Edu(1.0)%',multi='sum'),
		'grand_total':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Grand Total',multi='sum'),
		'invoice_narration':fields.text('Invoice Narration'),
		'invoice_narration_adhoc':fields.text('Invoice Narration'),
		'invoice_line_adhoc_11':fields.one2many('invoice.adhoc','invoice_adhoc_id11',''),
	#-------------kirti 14 jan----------#
		'grand_total1':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Grand Total',multi='sum'),	
		'total_amount1':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Total',help="The total amount.",multi="sum"),
		'total_tax1':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Total Tax',multi='sum'),
		'service_tax1':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Service Tax(12.0)%',help="The Service Tax.",multi='sum'),
		'edu_tax1':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Edu Cess(2.0)%',multi='sum'),
		'hs_edu1':fields.function(_amount_all,digits_compute=dp.get_precision('Account'), string='Hs Edu(1.0)%',multi='sum'),
		'service_tax_many2one_new':fields.many2one('account.tax',''),
		'edu_tax_many2one_new':fields.many2one('account.tax',''),
		'hs_edu_many2one_new':fields.many2one('account.tax',''),
		'branch_id':fields.many2one('res.company','Branch Office'),#--babita 13 jan--#
		'cse_new':fields.char('CSE',size=124),
		'customer_key':fields.char('Customer Key',size=364),
		'invoice_key':fields.char('Invoice Key', size=364),
		'import_flag':fields.boolean('Import Flag'),
		'cce_new':fields.char('CCE',size=500),
		
	}

	def _get_user(self, cr, uid, context=None):
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).company_id.id

	_defaults = {
		'service_tax_many2one_new':_get_service_tax,
		'edu_tax_many2one_new':_get_edu_tax,
		'hs_edu_many2one_new':_get_hs_edu,
		'edu_tax_many2one':_get_edu_tax,
		'hs_edu_many2one':_get_hs_edu,
		'service_tax_many2one':_get_service_tax,
		'branch_id':lambda self, cr, uid, context: self._get_user(cr, uid, context),
		}

	def view_invoice(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			if res.adhoc_invoice == True:
				name = "Adhoc Invoice"
			else :
				name = "Invoice"
			return{
						'type': 'ir.actions.act_window',
						'name':name,
						'view_type': 'form',
						'view_mode': 'form',
						'res_model': 'invoice.adhoc.master',
						'res_id':ids[0],
						'view_id':False,
						'target':'current',	
						'context': context,
						}
	def create(self,cr,uid,vals,context=None):
		if vals.get('customer_key'):
			customer_key = vals.get('customer_key')
			customer_id = self.pool.get('res.partner').search(cr, uid, [('customer_key','=',customer_key)])
			if customer_id:
				cust_name = self.pool.get('res.partner').browse(cr, uid, customer_id[0]).name
				vals.update({'partner_id':customer_id[0], 'cust_name':cust_name})
		invoice_super_id=super(invoice_adhoc_master, self).create(cr,uid,vals,context=context)
		cr.commit()
		return invoice_super_id

	def show_details_invoice(self,cr,uid,ids,context=None):
		models_data=self.pool.get('ir.model.data')
		form_id = models_data.get_object_reference(cr, uid, 'account_sales_branch', 'invoice_adhoc_search_id1')
		print "\n FORM ",form_id,"\t",form_id[1],ids,"\n",context,self._name
		for res in self.browse(cr,uid,ids):
			return{
			'type': 'ir.actions.act_window',
			'name':'Invoice',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'invoice.adhoc.master',
			'res_id':ids[0],
						  #'res_id':val,
			'view_id':form_id[1],
			'target':'current',	
			'context': context,
			}
	

	def generate_invoice(self,cr,uid,ids,context=None):
		for res in self.browse(cr,uid,ids):
			seq_id = self.pool.get('ir.sequence').get(cr, uid, 'invoice.adhoc.master')
			self.write(cr,uid,res.id,{'invoice_number':seq_id})
			cr.execute(('select icl.id from invoice_adhoc_master ic,payment_contract_history icl where icl.history_adhoc_invoice_id=ic.id and ic.partner_id=%(val)s and icl.invoice_number Is Null'),({'val':res.partner_id.id}))
			for invoice_id in cr.fetchall():
						if isinstance(invoice_id,(list,tuple)):
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id[0]))
						else:
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id))
		
		return True


	"""def write(self, cr, uid, ids, vals, context=None):
		if isinstance(ids,list):
			for res in self.browse(cr,uid,ids):
				if not res.invoice_number and res.invoice_period_from and res.billing_term:
					seq_id = self.pool.get('ir.sequence').get(cr, uid, 'invoice.adhoc.master')
					vals['invoice_number'] = seq_id
					cr.execute(('select icl.id from sale_contract ic,contract_history icl where icl.contract_history_id=ic.id and ic.partner_id=%(val)s and icl.invoice_number Is Null'),({'val':res.partner_id.id}))
					for delete_id in cr.fetchall():
						if isinstance(delete_id,(list,tuple)):
							self.pool.get('contract.history').write(cr,uid,delete_id[0],{'invoice_number':seq_id})
					cr.execute(('select icl.id from invoice_adhoc_master ic,payment_contract_history icl where icl.history_adhoc_invoice_id=ic.id and ic.partner_id=%(val)s and icl.invoice_number Is Null'),({'val':res.partner_id.id}))
					for invoice_id in cr.fetchall():
						if isinstance(delete_id,(list,tuple)):
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id[0]))
						else:
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id))
		else:
			for res in self.browse(cr,uid,[ids]):
				if not res.invoice_number and res.invoice_period_from and res.billing_term:
					seq_id = self.pool.get('ir.sequence').get(cr, uid, 'invoice.adhoc.master')
					vals['invoice_number'] = seq_id
					cr.execute(('select icl.id from sale_contract ic,contract_history icl where icl.contract_history_id=ic.id and ic.partner_id=%(val)s and icl.invoice_number Is Null'),({'val':res.partner_id.id}))
					for delete_id in cr.fetchall():
						if isinstance(delete_id,(list,tuple)):
						
							self.pool.get('contract.history').write(cr,uid,delete_id[0],{'invoice_number':seq_id})
						else:
						
							self.pool.get('contract.history').write(cr,uid,delete_id)
					cr.execute(('select icl.id from invoice_adhoc_master ic,payment_contract_history icl where icl.history_adhoc_invoice_id=ic.id and ic.partner_id=%(val)s and icl.invoice_number Is Null'),({'val':res.partner_id.id}))
					for invoice_id in cr.fetchall():
						if isinstance(delete_id,(list,tuple)):
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id[0]))
						else:
							cr.execute('update payment_contract_history set invoice_number=%s,invoice_date=%s where id=%s',(seq_id,res.invoice_date,invoice_id))
        	return super(invoice_adhoc_master, self).write(cr, uid, ids, vals, context=context)"""


	def print1(self,cr,uid,ids,context=None):
		for rec in self.browse(cr,uid,ids):
			self.write(cr,uid,rec.id,{'status':'printed'})
			data = self.pool.get('invoice.adhoc.master').read(cr, uid, [rec.id],context)
			datas = {
					'ids': ids,
					'model': 'invoice.adhoc.master',
					'form': data
					}
			if rec.adhoc_invoice == True:
				if rec.service_classification == 'port':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'port_adhoc',
						'datas': datas,
						}

				if rec.service_classification == 'airport':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'airport_adhoc',
						'datas': datas,
						}
				if rec.service_classification == 'commercial':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'commercial_adhoc',
						'datas': datas,
						}

				if rec.service_classification == 'exempted':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'exempted_adhoc',
						'datas': datas,
						}

			else:
				if rec.service_classification == 'port':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'port_new1',
						'datas': datas,
						}

				if rec.service_classification == 'airport':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'sale.contract1',
						'datas': datas,
						}
				if rec.service_classification == 'commercial':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'commercial1',
						'datas': datas,
						}

				if rec.service_classification == 'exempted':
					return {
						'type': 'ir.actions.report.xml',
						'report_name': 'exempted1',
						'datas': datas,
						}
		return {'type': 'ir.actions.act_window_close'}


invoice_adhoc_master()

class payment_contract_history(osv.osv):
	_name = 'payment.contract.history'
	_rec_name = 'invoice_number'
	_columns = {
		'history_adhoc_invoice_id':fields.many2one('invoice.adhoc.master',''),
		'invoice_number':fields.char('Invoice_number',size=124),
		'invoice_date':fields.date('Invoice date'),
		'cse':fields.many2one('hr.employee','CSE'),
		'order_number':fields.char('Order Number',size=124),
		'basic_amount':fields.float('Basic Amount',digits_compute=dp.get_precision('Account')),
		'tax_amount':fields.float('Tax Amount',digits_compute=dp.get_precision('Account')),
		'grand_total':fields.float('Grand Total',digits_compute=dp.get_precision('Account')),
		'payment_status':fields.selection([('open','Invoice Created'),('printed','Printed'),('paid','Paid')],'Status'),
		'payment_cancel_reason':fields.text('Payment Cancel Reason'),
		}
payment_contract_history()

class invoice_adhoc(osv.osv):
	_name = 'invoice.adhoc'
	_columns = {
		'invoice_adhoc_id11':fields.many2one('invoice.adhoc.master',''),
		'invoice_adhoc_id':fields.many2one('invoice.adhoc.master',''),
		'location':fields.many2one('new.address','Location Name'),
		'location_invoice':fields.many2one('res.partner.address','Location Name'),
		'pms':fields.many2one('product.product',"PMS",domain="[('type','=','service')]"),
		'rate':fields.float('(Rate) Rs per unit Ares'),
		'unit':fields.selection([('sqr_ft','Sq.ft'),('sqr_mt','Sq.Mt'),('running_mt','Running Mtr')],'Unit'),
		'area':fields.char('Area',size=132),
		'amount':fields.float('Amount(INR)'),
		'location_key':fields.char('Location Key', size=364),
		'invoice_key':fields.char('Invoice Key', size=364),


	}
	_defaults = {
		'unit':'sqr_ft',
	}
	
	
	
	'''def create(self,cr,uid,vals,context=None):

		location_id = ou_id = ''

		if vals.get('invoice_key'):
			invoice_key = vals.get('invoice_key')
			invoice_id = self.pool.get('invoice.adhoc.master').search(cr, uid, [('invoice_key','=',invoice_key)])
			if invoice_id:
				res1 = self.pool.get('invoice.adhoc.master').browse(cr,uid,invoice_id[0] )
				ou_id = res1.partner_id.ou_id if res1.partner_id else ''
				print res1, ou_id,"dssdsdsdsd"
			loc_key = vals.get('location_key')
			address_id = self.pool.get('res.partner.address').search(cr, uid, [('location_id','=',loc_key)])
			
			print invoice_id, address_id
			"""if address_id:
				
				srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',self.pool.get('res.partner.address').browse(cr,uid,address_id[0]).location_id)])
				print srch
				if srch:
					
					location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id
					print "dssdsdsd",location_id
					#ou_id = self.pool.get('res.partner').browse(cr,uid,address_id[0] ).ou_id	
					
					#ou_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).ou_id"""
			
			if invoice_id:
				invoice_brw = self.pool.get('invoice.adhoc.master').browse(cr, uid, invoice_id[0])
				if invoice_brw:
					if invoice_brw.adhoc_invoice and invoice_id:
						vals.update({'invoice_adhoc_id':invoice_id[0],})
						if address_id:
							
							vals.update({'location_invoice':address_id[0] if address_id else '' })

					elif not invoice_brw.adhoc_invoice and invoice_id:
						vals.update({'invoice_adhoc_id11':invoice_id[0],})
						if address_id:
							vals.update({'location_invoice':address_id[0] if address_id else '' })
		#print vals,address_id,new_address_id,"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
		res=super(invoice_adhoc,self).create(cr,uid,vals,context=context)
		return res'''	
		
		
		
		
		
		
	def create(self,cr,uid,vals,context=None):

		location_id = ou_id = ''

		if vals.get('invoice_key'):
			invoice_key = vals.get('invoice_key')
			invoice_id = self.pool.get('invoice.adhoc.master').search(cr, uid, [('invoice_key','=',invoice_key)])
			if invoice_id:
				res1 = self.pool.get('invoice.adhoc.master').browse(cr,uid,invoice_id[0] )
				ou_id = res1.partner_id.ou_id if res1.partner_id else ''
				print res1, ou_id,"dssdsdsdsd"
			loc_key = vals.get('location_key')
			address_id = self.pool.get('res.partner.address').search(cr, uid, [('location_id','=',loc_key)])
			
			print invoice_id, address_id
			"""if address_id:
				
				srch = self.pool.get('customer.line').search(cr,uid,[('customer_address','=',self.pool.get('res.partner.address').browse(cr,uid,address_id[0]).location_id)])
				print srch
				if srch:
					
					location_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).location_id
					print "dssdsdsd",location_id
					#ou_id = self.pool.get('res.partner').browse(cr,uid,address_id[0] ).ou_id	
					
					#ou_id = self.pool.get('customer.line').browse(cr,uid,srch[0]).ou_id"""
			
			if invoice_id:
				invoice_brw = self.pool.get('invoice.adhoc.master').browse(cr, uid, invoice_id[0])
				if invoice_brw:
					if invoice_brw.adhoc_invoice and invoice_id:
						vals.update({'invoice_adhoc_id':invoice_id[0],})
						if address_id:
							new_address_id = self.pool.get('new.address').search(cr, uid, [('partner_address','=',address_id[0])])
							if not new_address_id:
								for add in self.pool.get('res.partner.address').browse(cr, uid, address_id):
									new_address = self.pool.get('new.address').create(cr, uid, {'partner_address':address_id[0], 'fax':add.fax, 'street':add.street, 'landmark':add.landmark, 'sub_area':add.sub_area,'city_id':add.city_id.id if add.city_id else '','building':add.building, 'zip':add.zip,'service_area':add.service_area.id if add.service_area else '', 'state_id': add.state_id.id if add.state_id else '', 'email':add.email, 'district':add.district.id if add.district else '', 'tehsil': add.tehsil.id if add.tehsil else '', 'apartment':add.apartment})
							vals.update({'location':new_address_id[0] if new_address_id else new_address, })

					elif not invoice_brw.adhoc_invoice and invoice_id:
						vals.update({'invoice_adhoc_id11':invoice_id[0],})
						if address_id:
							new_address_id = self.pool.get('new.address').search(cr, uid, [('partner_address','=',address_id[0])])
							if not new_address_id:
								for add in self.pool.get('res.partner.address').browse(cr, uid, address_id):
									new_address = self.pool.get('new.address').create(cr, uid, {'partner_address':address_id[0], 'fax':add.fax, 'street':add.street, 'landmark':add.landmark, 'sub_area':add.sub_area,'city_id':add.city_id.id if add.city_id else '','building':add.building, 'zip':add.zip,'service_area':add.service_area.id if add.service_area else '', 'state_id': add.state_id.id if add.state_id else '', 'email':add.email, 'district':add.district.id if add.district else '', 'tehsil': add.tehsil.id if add.tehsil else '', 'apartment':add.apartment})
							vals.update({'location':new_address_id[0] if new_address_id else new_address, })
		#print vals,address_id,new_address_id,"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
		res=super(invoice_adhoc,self).create(cr,uid,vals,context=context)
		return res
		
		
		
		
		
		
		
		
		
		
		
		
invoice_adhoc()








