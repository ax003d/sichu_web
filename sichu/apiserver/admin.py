from django.contrib import admin

from apiserver.models import *


class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'opcode', 'model', 'data')

    def user(self, obj):
        return ','.join([i.username for i in obj.users.all()])

class GexinIDAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'user')


class ExportLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'email', 'status', 'user')


class EmailVerifyAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at', 'email', 
                    'code', 'verified', 'user')


admin.site.register(OperationLog, OperationLogAdmin)
admin.site.register(GexinID, GexinIDAdmin)
admin.site.register(ExportLog, ExportLogAdmin)
admin.site.register(EmailVerify, EmailVerifyAdmin)
