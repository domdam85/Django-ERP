import django_tables2 as tables
from django.utils.html import format_html
from django.utils import timezone
from .models import SyncSession

class SyncSessionTable(tables.Table):
    start_time = tables.DateTimeColumn(
        format='Y-m-d H:i:s',
        attrs={'td': {'class': 'align-middle'}}
    )
    status = tables.Column(
        attrs={'td': {'class': 'align-middle text-center'}}
    )
    progress = tables.Column(
        empty_values=(),
        orderable=False,
        attrs={'td': {'class': 'align-middle', 'style': 'min-width: 200px;'}}
    )
    synced_objects = tables.Column(
        attrs={'td': {'class': 'align-middle text-center'}}
    )
    failed_objects = tables.Column(
        attrs={'td': {'class': 'align-middle text-center'}}
    )
    duration = tables.Column(
        empty_values=(),
        attrs={'td': {'class': 'align-middle text-center'}}
    )
    
    def render_status(self, value):
        badge_class = {
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        }.get(value, 'bg-secondary')
        
        return format_html(
            '<span class="badge rounded-pill {}">{}</span>',
            badge_class,
            value.title()
        )
    
    def render_progress(self, record):
        bar_class = {
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        }.get(record.status, 'bg-primary')
        
        return format_html(
            '''
            <div class="progress" style="height: 20px;">
                <div class="progress-bar {} {}" 
                     role="progressbar" 
                     style="width: {}%"
                     aria-valuenow="{}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    {}%
                </div>
            </div>
            ''',
            bar_class,
            'progress-bar-striped progress-bar-animated' if record.status == 'running' else '',
            record.progress_percentage,
            record.progress_percentage,
            record.progress_percentage
        )
    
    def render_duration(self, record):
        if record.status == 'running':
            duration = timezone.now() - record.start_time
            minutes = duration.seconds // 60
            seconds = duration.seconds % 60
            return format_html(
                '<span class="badge bg-primary">Running ({} min {} sec)</span>',
                str(minutes), str(seconds)
            )
        elif record.end_time:
            duration = record.end_time - record.start_time
            minutes = duration.seconds // 60
            seconds = duration.seconds % 60
            return f"{minutes} min {seconds} sec"
        return '-'
    
    class Meta:
        model = SyncSession
        template_name = "django_tables2/bootstrap5.html"
        fields = ('start_time', 'status', 'progress', 'synced_objects', 'failed_objects', 'duration')
        attrs = {
            'class': 'table table-dark table-hover',
            'thead': {
                'class': 'table-dark'
            }
        }
        row_attrs = {
            'class': lambda record: 'table-danger' if record.status == 'failed' else ''
        }
