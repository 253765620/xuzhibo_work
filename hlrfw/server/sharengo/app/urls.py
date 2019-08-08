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
        ('actual_msg_report', views.actual_msg_report),
        ('load_car', views.load_car),
        ('err_rep', views.err_rep),
        ('regular_err_rep', views.regular_err_rep),
        ('log', views.log),
        ('heart_beat', views.heart_beat),
)

if __name__ == '__main__':
    print urlpatterns
