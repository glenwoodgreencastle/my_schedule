
{
    'name': 'My Schedule',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage employee schedules with time off, Saturday signups, and extra day working',
    'description': """
        My Schedule
        =======================
        This module extends the existing employee schedule functionality with:
        - Custom time off tracking separate from standard HR time off
        - Saturday signup management
        - Extra day signup management
        - Calendar view showing all employee schedules
        - Manager approval workflows
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['hr', 'employee_schedule'],
    'data': [
        'security/my_schedule_security.xml',
        'security/ir.model.access.csv',
        'views/my_schedule_views.xml',
        'views/my_schedule_calendar_views.xml',
        'views/my_schedule_time_off_views.xml',
        'views/my_schedule_saturday_views.xml',
        'views/my_schedule_extra_day_views.xml',
        'views/hr_employee_views.xml',
        'data/ir_cron.xml',
    ],
    'demo': [],
    'application': True,
    'sequence': 105,  # Position after employee_schedule
    'category': 'Human Resources',
    'auto_install': False,
    'license': 'LGPL-3',
}
