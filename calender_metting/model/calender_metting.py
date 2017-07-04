# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import timedelta
from datetime import datetime

class crm_phonecall_log_wizard(models.TransientModel):
    _inherit = 'crm.phonecall.log.wizard'

    def schedule_again(self):
        res = super(crm_phonecall_log_wizard, self).schedule_again()
        if self.reschedule_option != "no_reschedule" and self.custom_duration > 0.0 and self.opportunity_id:
            start = datetime.now()
            end = datetime.now() + timedelta(hours=self.custom_duration)
            if self.reschedule_option == "7d":
                start = datetime.now() + timedelta(weeks=1)
                end = datetime.now() + timedelta(weeks=1, hours=self.custom_duration)
            elif self.reschedule_option == "1d":
                start = datetime.now() + timedelta(days=1)
                end = datetime.now() + timedelta(days=1, hours=self.custom_duration)
            elif self.reschedule_option == "15d":
                start = datetime.now() + timedelta(days=15)
                end = datetime.now() + timedelta(days=15, hours=self.custom_duration)
            elif self.reschedule_option == "2m":
                start = datetime.now() + timedelta(weeks=8)
                end = datetime.now() + timedelta(weeks=8, hours=self.custom_duration)
            elif self.reschedule_option == "custom":
                d = datetime.strptime(self.reschedule_date, '%Y-%m-%d %H:%M:%S')
                start = d
                end = d + timedelta(hours=self.custom_duration)

            vals = {
                'duration': self.custom_duration,
                'name': self.description,
                'opportunity_id': self.opportunity_id,
                'start': str(start),
                'stop': str(end),
                }
            self.env['calendar.event'].create(vals)
            return res