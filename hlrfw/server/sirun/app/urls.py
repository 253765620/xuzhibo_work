import views
from core.urls import pattern

"""
the urls control where are the request goes!
dispatch method will return a Dicts to urlpatterns
and then,you can call 'view.register' by nickname 'register'
If you have emergency thing to do,you can reset the value of Dicts
Example, when the position run on the views.position,you want to
get terminal information,so on the linux, CTRL+Z will raise a TSTIP
signal,and then process catch it, and do some change to urlpatterns
so you can make position run on the views.terminal_info ....
"""
urlpatterns = pattern(
        ('t_register', views.t_register),
        ('t_login', views.t_login),
        ('t_logout', views.t_logout),
        ('t_relogin', views.t_relogin),
        ('t_keep_active', views.t_keep_active),
        ('t_err_rep', views.t_actual_msg_rep),
        ('t_actual_msg_rep', views.t_actual_msg_rep),
        ('t_E_call', views.t_E_call),
        ('t_UBI_rep', views.t_UBI_rep),
        ('t_update', views.t_update),
)

if __name__ == '__main__':
    print urlpatterns
