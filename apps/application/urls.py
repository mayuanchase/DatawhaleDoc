from django.urls import path

from . import views

app_name = "application"
urlpatterns = [
    path('application', views.Application.as_view(), name="application"),
    path('application/profile', views.Application.Profile.as_view()),
    path('application/embed', views.Application.Embed.as_view()),
    path('application/authentication', views.Application.Authentication.as_view()),
    path('application/<str:application_id>/edit_icon', views.Application.EditIcon.as_view()),
    path('application/<str:application_id>/statistics/customer_count',
         views.ApplicationStatistics.CustomerCount.as_view()),
    path('application/<str:application_id>/statistics/customer_count_trend',
         views.ApplicationStatistics.CustomerCountTrend.as_view()),
    path('application/<str:application_id>/statistics/chat_record_aggregate',
         views.ApplicationStatistics.ChatRecordAggregate.as_view()),
    path('application/<str:application_id>/statistics/chat_record_aggregate_trend',
         views.ApplicationStatistics.ChatRecordAggregateTrend.as_view()),
    path('application/<str:application_id>/model', views.Application.Model.as_view()),
    path('application/<str:application_id>/hit_test', views.Application.HitTest.as_view()),
    path('application/<str:application_id>/api_key', views.Application.ApplicationKey.as_view()),
    path("application/<str:application_id>/api_key/<str:api_key_id>",
         views.Application.ApplicationKey.Operate.as_view()),
    path('application/<str:application_id>', views.Application.Operate.as_view(), name='application/operate'),
    path('application/<str:application_id>/list_dataset', views.Application.ListApplicationDataSet.as_view(),
         name='application/dataset'),
    path('application/<str:application_id>/access_token', views.Application.AccessToken.as_view(),
         name='application/access_token'),
    path('application/<int:current_page>/<int:page_size>', views.Application.Page.as_view(), name='application_page'),
    path('application/<str:application_id>/chat/open', views.ChatView.Open.as_view()),
    path("application/chat/open", views.ChatView.OpenTemp.as_view()),
    path('application/<str:application_id>/chat/export', views.ChatView.Export.as_view(), name='export'),
    path('application/<str:application_id>/chat', views.ChatView.as_view(), name='chats'),
    path('application/<str:application_id>/chat/<int:current_page>/<int:page_size>', views.ChatView.Page.as_view()),
    path('application/<str:application_id>/chat/<chat_id>', views.ChatView.Operate.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/', views.ChatView.ChatRecord.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<int:current_page>/<int:page_size>',
         views.ChatView.ChatRecord.Page.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<chat_record_id>',
         views.ChatView.ChatRecord.Operate.as_view()),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<str:chat_record_id>/vote',
         views.ChatView.ChatRecord.Vote.as_view(),
         name=''),
    path(
        'application/<str:application_id>/chat/<chat_id>/chat_record/<str:chat_record_id>/dataset/<str:dataset_id>/document_id/<str:document_id>/improve',
        views.ChatView.ChatRecord.Improve.as_view(),
        name=''),
    path('application/<str:application_id>/chat/<chat_id>/chat_record/<str:chat_record_id>/improve',
         views.ChatView.ChatRecord.ChatRecordImprove.as_view()),
    path('application/chat_message/<str:chat_id>', views.ChatView.Message.as_view()),
    path('application/wechat_chat_message/<str:chat_id>', views.ChatView.WechatMessage.as_view()),
    path(
        'application/<str:application_id>/chat/<chat_id>/chat_record/<str:chat_record_id>/dataset/<str:dataset_id>/document_id/<str:document_id>/improve/<str:paragraph_id>',
        views.ChatView.ChatRecord.Improve.Operate.as_view(),
        name='')
]
