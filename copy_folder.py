
import shutil
import os
import time 
source_path = '/opt/odoo9/openerp/lcpl_addons/' 
dest_path='/opt/odoo9/openerp/HHH/'

files_to_copy = ['assemble_pro','dev_inv_gst_template_india','manage_settings','odoo_material_old_layout','upgrade_button_globalteckz','web_menu_hide_9','odoo_top_trending_products','stock','mrp','stock_transfer_restrict_lot','sale','stock_account','account_voucher','mail','hr_holidays','account','account_accountant','hr_payroll','purchase','hr','account_bank_statement_import','account_full_reconcile','analytic','auth_crypt','auth_signup','auto_backup','auto_backup_download','barcodes','base','base_action_rule','base_directory_files_download','base_import','base_report_to_printer','base_setup','base_technical_features','biometrics_integration','bom_components_image','bus','decimal_precision','delivery','document','fetchmail','hr_attendance','hr_contract','im_odoo_support','l10n_in','l10n_in_hr_payroll','mail_tip','menu_collapsible','odoo_web_login','payment','payment_transfer','portal','portal_sale','portal_stock','pricelists_import','procurement','procurement_jit','product','product_expiry','report','resource','rowno_in_tree','sale_mrp','sales_team','sale_stock','stock_barcode','stock_inventory_import','stock_inventory_line_price','stock_split_availability','web','web_calendar','web_debranding','web_diagram','web_editor','web_export_view','web_kanban','web_kanban_gauge','web_m2x_options','web_planner','web_settings_dashboard','web_tip','web_tree_image','web_view_editor','calendar','stock_get_name_qty']

try:
	path_new=os.path.dirname(dest_path) 
	path = os.path.dirname(source_path) 
	if os.path.exists(path): 
		listing = os.listdir(path)
		for folders in files_to_copy:
			if folders in listing:
				folders_copy = "/opt/odoo9/openerp/lcpl_addons/"+folders
				oldLoc = source_path + folders
				newLoc = dest_path  + folders
				shutil.copytree(oldLoc, newLoc)

except: 
        raise 

