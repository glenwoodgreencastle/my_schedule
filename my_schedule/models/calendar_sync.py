
from odoo import api, fields, models, _
from datetime import datetime, timedelta
import pytz

class CalendarSync(models.AbstractModel):
    _name = 'my.schedule.calendar.sync'
    _description = 'Calendar Synchronization'
    
    @api.model
    def _sync_regular_schedules(self):
        """Sync regular employee schedules to calendar events"""
        # Get the date range for the next 4 weeks
        today = fields.Date.today()
        end_date = today + timedelta(days=28)  # 4 weeks ahead
        
        calendar_obj = self.env['my.schedule.calendar']
        
        # Delete old regular schedule events
        old_events = calendar_obj.search([
            ('schedule_type', '=', 'regular'),
            ('date', '>=', today),
        ])
        old_events.unlink()
        
        # Get all employee schedules from the main employee_schedule module
        schedules = self.env['employee.custom.schedule'].search([])
        
        # For each schedule, create events for the next 4 weeks
        for schedule in schedules:
            employee = schedule.employee_id
            current_date = today
            
            # Loop through each day for the next 4 weeks
            while current_date <= end_date:
                weekday = current_date.weekday()  # 0 is Monday, 6 is Sunday
                
                # Skip Sunday
                if weekday == 6:
                    current_date += timedelta(days=1)
                    continue
                
                # Determine if employee works on this day
                works_today = False
                start_time = 0
                end_time = 0
                
                if weekday == 0 and schedule.monday_active:  # Monday
                    works_today = True
                    start_time = schedule.monday_start
                    end_time = schedule.monday_end
                elif weekday == 1 and schedule.tuesday_active:  # Tuesday
                    works_today = True
                    start_time = schedule.tuesday_start
                    end_time = schedule.tuesday_end
                elif weekday == 2 and schedule.wednesday_active:  # Wednesday
                    works_today = True
                    start_time = schedule.wednesday_start
                    end_time = schedule.wednesday_end
                elif weekday == 3 and schedule.thursday_active:  # Thursday
                    works_today = True
                    start_time = schedule.thursday_start
                    end_time = schedule.thursday_end
                elif weekday == 4 and schedule.friday_active:  # Friday
                    works_today = True
                    start_time = schedule.friday_start
                    end_time = schedule.friday_end
                elif weekday == 5 and schedule.saturday_active:  # Saturday
                    works_today = True
                    start_time = schedule.saturday_start
                    end_time = schedule.saturday_end
                
                if works_today:
                    # Create calendar entry
                    calendar_obj.create({
                        'employee_id': employee.id,
                        'date': current_date,
                        'start_time': start_time,
                        'end_time': end_time,
                        'schedule_type': 'regular'
                    })
                
                current_date += timedelta(days=1)
    
    @api.model
    def _sync_time_off(self):
        """Sync approved time off to calendar"""
        # Get all approved time off that hasn't expired
        time_offs = self.env['my.schedule.time.off'].search([
            ('state', '=', 'approved'),
            ('end_date', '>=', fields.Date.today())
        ])
        
        calendar_obj = self.env['my.schedule.calendar']
        
        # Delete old time off events that are in the future
        old_events = calendar_obj.search([
            ('schedule_type', '=', 'off'),
            ('date', '>=', fields.Date.today()),
        ])
        old_events.unlink()
        
        # Create new calendar entries for each time off
        for time_off in time_offs:
            current_date = time_off.start_date
            while current_date <= time_off.end_date:
                calendar_obj.create({
                    'employee_id': time_off.employee_id.id,
                    'date': current_date,
                    'schedule_type': 'off',
                    'start_time': 0.0,
                    'end_time': 0.0
                })
                current_date += timedelta(days=1)
    
    @api.model
    def _sync_saturday_signups(self):
        """Sync confirmed Saturday signups to calendar"""
        # Get all confirmed Saturday signups that haven't expired
        saturdays = self.env['my.schedule.saturday'].search([
            ('state', '=', 'confirmed'),
            ('date', '>=', fields.Date.today())
        ])
        
        calendar_obj = self.env['my.schedule.calendar']
        
        # Delete old Saturday events that are in the future
        old_events = calendar_obj.search([
            ('schedule_type', '=', 'saturday'),
            ('date', '>=', fields.Date.today()),
        ])
        old_events.unlink()
        
        # Create new calendar entries for each Saturday signup
        for saturday in saturdays:
            calendar_obj.create({
                'employee_id': saturday.employee_id.id,
                'date': saturday.date,
                'start_time': saturday.start_time,
                'end_time': saturday.end_time,
                'schedule_type': 'saturday'
            })
    
    @api.model
    def _sync_extra_days(self):
        """Sync confirmed extra days to calendar"""
        # Get all confirmed extra days that haven't expired
        extra_days = self.env['my.schedule.extra.day'].search([
            ('state', '=', 'confirmed'),
            ('date', '>=', fields.Date.today())
        ])
        
        calendar_obj = self.env['my.schedule.calendar']
        
        # Delete old extra day events that are in the future
        old_events = calendar_obj.search([
            ('schedule_type', '=', 'extra'),
            ('date', '>=', fields.Date.today()),
        ])
        old_events.unlink()
        
        # Create new calendar entries for each extra day
        for extra_day in extra_days:
            calendar_obj.create({
                'employee_id': extra_day.employee_id.id,
                'date': extra_day.date,
                'start_time': extra_day.start_time,
                'end_time': extra_day.end_time,
                'schedule_type': 'extra'
            })
    
    @api.model
    def sync_all_calendars(self):
        """Sync all schedules, time off, and extra days to the calendar"""
        self._sync_regular_schedules()
        self._sync_time_off()
        self._sync_saturday_signups()
        self._sync_extra_days()
        return True
