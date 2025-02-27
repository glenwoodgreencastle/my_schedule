
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class MySchedule(models.Model):
    _name = 'my.schedule'
    _description = 'My Schedule'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    
    # Time off requests
    time_off_ids = fields.One2many('my.schedule.time.off', 'schedule_id', string='Time Off Requests')
    
    # Saturday signup
    saturday_signup_ids = fields.One2many('my.schedule.saturday', 'schedule_id', string='Saturday Signups')
    
    # Extra day signup
    extra_day_ids = fields.One2many('my.schedule.extra.day', 'schedule_id', string='Extra Day Signups')

class MyScheduleTimeOff(models.Model):
    _name = 'my.schedule.time.off'
    _description = 'Custom Time Off Request'
    
    schedule_id = fields.Many2one('my.schedule', string='Schedule', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='schedule_id.employee_id', store=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    reason = fields.Text(string='Reason')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    
    def action_submit(self):
        self.state = 'submitted'
    
    def action_approve(self):
        self.state = 'approved'
        self._update_calendar()
    
    def action_reject(self):
        self.state = 'rejected'
        
    def _update_calendar(self):
        """Update the calendar with time off entries"""
        calendar_obj = self.env['my.schedule.calendar']
        
        # Calculate all days between start and end date
        current_date = self.start_date
        while current_date <= self.end_date:
            # Create or update calendar entry
            calendar_obj.create({
                'employee_id': self.employee_id.id,
                'date': current_date,
                'schedule_type': 'off',
                'start_time': 0.0,
                'end_time': 0.0,
                'hours': 0.0
            })
            current_date += timedelta(days=1)

class MyScheduleSaturday(models.Model):
    _name = 'my.schedule.saturday'
    _description = 'Saturday Signup'
    
    schedule_id = fields.Many2one('my.schedule', string='Schedule', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='schedule_id.employee_id', store=True)
    date = fields.Date(string='Saturday Date', required=True)
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    hours = fields.Float(string='Hours', compute='_compute_hours', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    
    @api.depends('start_time', 'end_time')
    def _compute_hours(self):
        for record in self:
            record.hours = record.end_time - record.start_time if record.start_time and record.end_time else 0
    
    def action_confirm(self):
        self.state = 'confirmed'
        self._update_calendar()
    
    def action_reject(self):
        self.state = 'rejected'
    
    def _update_calendar(self):
        """Update the calendar with Saturday signup"""
        calendar_obj = self.env['my.schedule.calendar']
        
        # Create or update calendar entry
        calendar_obj.create({
            'employee_id': self.employee_id.id,
            'date': self.date,
            'schedule_type': 'saturday',
            'start_time': self.start_time,
            'end_time': self.end_time,
            'hours': self.hours
        })

class MyScheduleExtraDay(models.Model):
    _name = 'my.schedule.extra.day'
    _description = 'Extra Day Signup'
    
    schedule_id = fields.Many2one('my.schedule', string='Schedule', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='schedule_id.employee_id', store=True)
    date = fields.Date(string='Date', required=True)
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    hours = fields.Float(string='Hours', compute='_compute_hours', store=True)
    reason = fields.Text(string='Reason')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    
    @api.depends('start_time', 'end_time')
    def _compute_hours(self):
        for record in self:
            record.hours = record.end_time - record.start_time if record.start_time and record.end_time else 0
    
    def action_confirm(self):
        self.state = 'confirmed'
        self._update_calendar()
    
    def action_reject(self):
        self.state = 'rejected'
    
    def _update_calendar(self):
        """Update the calendar with extra day signup"""
        calendar_obj = self.env['my.schedule.calendar']
        
        # Create or update calendar entry
        calendar_obj.create({
            'employee_id': self.employee_id.id,
            'date': self.date,
            'schedule_type': 'extra',
            'start_time': self.start_time,
            'end_time': self.end_time,
            'hours': self.hours
        })

class ScheduleCalendar(models.Model):
    _name = 'my.schedule.calendar'
    _description = 'Schedule Calendar'
    
    name = fields.Char(string='Name', compute='_compute_name')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Date', required=True)
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    hours = fields.Float(string='Hours', compute='_compute_hours', store=True)
    schedule_type = fields.Selection([
        ('regular', 'Regular Schedule'),
        ('saturday', 'Saturday Signup'),
        ('extra', 'Extra Day'),
        ('off', 'Time Off')
    ], string='Schedule Type', default='regular')
    
    @api.depends('employee_id', 'date', 'schedule_type')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.employee_id.name} - {record.date} ({record.schedule_type})"
    
    @api.depends('start_time', 'end_time')
    def _compute_hours(self):
        for record in self:
            record.hours = record.end_time - record.start_time if record.start_time and record.end_time else 0

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    my_schedule_id = fields.One2many('my.schedule', 'employee_id', string='My Schedule')
