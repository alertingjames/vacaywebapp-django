"""vacaywebapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from vacay import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^vacay/', include('vacay.urls')),
    url(r'^$', views.welcome, name='welcome'),
    url(r'^employee_login_page', views.employee_login_page, name='employee_login_page'),
    url(r'^login_user', views.login_user, name='login_user'),
    url(r'^employee_update_profile', views.employee_update_profile, name='employee_update_profile'),
    url(r'^myloc/$', views.myloc, name='myloc'),
    url(r'^getloc/$', views.getloc, name='getloc'),
    url(r'^employee_post_profile', views.employee_post_profile, name='employee_post_profile'),
    url(r'^home', views.home, name='home'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^weather', views.weather, name='weather'),
    url(r'^nearby', views.nearby, name='nearby'),
    url(r'^services_nearby', views.services_nearby, name='services_nearby'),
    url(r'^show_weather', views.show_weather, name='show_weather'),
    url(r'^get_all_users', views.get_all_users, name='get_all_users'),
    url(r'^contactors', views.contactors, name='contactors'),
    url(r'^chat_contactor/(?P<contactor_id>[0-9]+)/$', views.chat_contactor, name='chat_contactor'),
    url(r'^mailcontactor/(?P<contactor_id>[0-9]+)/$', views.mailcontactor, name='mailcontactor'),
    url(r'^friend_profile_chat/(?P<friend_id>[0-9]+)/$', views.friend_profile_chat, name='friend_profile_chat'),
    url(r'^friend_profile_mail/(?P<friend_id>[0-9]+)/$', views.friend_profile_mail, name='friend_profile_mail'),
    url(r'^userloc/$', views.userloc, name='userloc'),
    url(r'^match_friend', views.match_friend, name='match_friend'),
    url(r'^mail_inbox', views.mail_inbox, name='mail_inbox'),
    url(r'^sent_mail', views.sent_mail, name='sent_mail'),
    url(r'^mail_compose', views.mail_compose, name='mail_compose'),
    url(r'^send_mail_tofriend', views.send_mail_tofriend, name='send_mail_tofriend'),
    url(r'^map_attach', views.map_attach, name='map_attach'),
    url(r'^attach_loc', views.attach_loc, name='attach_loc'),
    url(r'^mail_detail/(?P<mail_id>[0-9]+)/$', views.mail_detail, name='mail_detail'),
    url(r'^reply_mail/(?P<mail_id>[0-9]+)/$', views.reply_mail, name='reply_mail'),
    url(r'^sentmail_detail/(?P<mail_id>[0-9]+)/$', views.sentmail_detail, name='sentmail_detail'),
    url(r'^requested_loc', views.requested_loc, name='requested_loc'),
    url(r'^view_mailimage/(?P<mail_id>[0-9]+)/$', views.view_mailimage, name='view_mailimage'),
    url(r'^sentrequested_loc', views.sentrequested_loc, name='sentrequested_loc'),
    url(r'^view_sentmailimage/(?P<mail_id>[0-9]+)/$', views.view_sentmailimage, name='view_sentmailimage'),
    url(r'^map_chat', views.map_chat, name='map_chat'),
    url(r'^submit_chatloc', views.submit_chatloc, name='submit_chatloc'),
    url(r'^show_chatloc', views.show_chatloc, name='show_chatloc'),
    url(r'^myprofile', views.myprofile, name='myprofile'),
    url(r'^proprofile', views.proprofile, name='proprofile'),
    url(r'^get_notifications', views.get_notifications, name='get_notifications'),
    url(r'^chat_page', views.chat_page, name='chat_page'),
    url(r'^eat_entry', views.eat_entry, name='eat_entry'),
    url(r'^eat', views.eat, name='eat'),
    url(r'^drink', views.drink, name='drink'),
    url(r'^denver', views.denver, name='denver'),
    url(r'^den_eddetail/(?P<eatdrink_id>[0-9]+)/$', views.den_eddetail, name='den_eddetail'),
    url(r'^sanfran', views.sanfran, name='sanfran'),
    url(r'^san_eddetail/(?P<eatdrink_id>[0-9]+)/$', views.san_eddetail, name='san_eddetail'),
    url(r'^get_jobs', views.get_jobs, name='get_jobs'),
    url(r'^job_detail_(?P<job_id>[0-9]+)', views.job_detail, name='job_detail'),
    url(r'^job_media/(?P<job_id>[0-9]+)/$', views.job_media, name='job_media'),
    url(r'^get_announces', views.get_announces, name='get_announces'),
    url(r'^announce_detail_(?P<announce_id>[0-9]+)', views.announce_detail, name='announce_detail'),
    url(r'^announce_media/(?P<announce_id>[0-9]+)/$', views.announce_media, name='announce_media'),
    url(r'^announce_signup/(?P<announce_id>[0-9]+)/$', views.announce_signup, name='announce_signup'),
    url(r'^get_wc', views.get_wc, name='get_wc'),
    url(r'^watercooler_setup', views.watercooler_setup, name='watercooler_setup'),
    url(r'^upload_watercooler', views.upload_watercooler, name='upload_watercooler'),
    url(r'^comments/(?P<wc_id>[0-9]+)', views.comments, name='comments'),
    url(r'^add_wc_comment/(?P<wc_id>[0-9]+)', views.add_wc_comment, name='add_wc_comment'),
    url(r'^editcomment/(?P<wc_id>[0-9]+)/(?P<comment_id>[0-9]+)', views.editcomment, name='editcomment'),
    url(r'^delcomment/(?P<comment_id>[0-9]+)', views.delcomment, name='delcomment'),
    url(r'^editwc/(?P<wc_id>[0-9]+)', views.editwc, name='editwc'),
    url(r'^delwc/(?P<wc_id>[0-9]+)', views.delwc, name='delwc'),
    url(r'^updatewatercooler/(?P<wc_id>[0-9]+)', views.updatewatercooler, name='updatewatercooler'),
    url(r'^drawing', views.drawing, name='drawing'),
    url(r'^returnfromdrawing', views.returnfromdrawing, name='returnfromdrawing'),
    url(r'^wc_comment_upload', views.wc_comment_upload, name='wc_comment_upload'),
    url(r'^beauty_entry', views.beauty_entry, name='beauty_entry'),
    url(r'^women_beauty', views.women_beauty, name='women_beauty'),
    url(r'^men_beauty', views.men_beauty, name='men_beauty'),
    url(r'^beauty', views.beauty, name='beauty'),
    url(r'^b_loc', views.b_loc, name='b_loc'),
    url(r'^service_detail/(?P<service_id>[0-9]+)', views.service_detail, name='service_detail'),
    url(r'^brequest/(?P<service_id>[0-9]+)', views.brequest, name='brequest'),
    url(r'^filter_beauties', views.filter_beauties, name='filter_beauties'),
    url(r'^get_schedule/(?P<proid>[0-9]+)', views.get_schedule, name='get_schedule'),
    url(r'^service_media/(?P<service_id>[0-9]+)/$', views.service_media, name='service_media'),
    url(r'^get_products/(?P<proid>[0-9]+)', views.get_products, name='get_products'),
    url(r'^product_detail/(?P<itemid>[0-9]+)', views.product_detail, name='product_detail'),
    url(r'^product_media/(?P<itemid>[0-9]+)/$', views.product_media, name='product_media'),
    url(r'^request_beauty', views.request_beauty, name='request_beauty'),
    url(r'^bucks', views.bucks, name='bucks'),
    url(r'^updateBuck', views.updateBuck, name='updateBuck'),
    url(r'^check_payment', views.check_payment, name='check_payment'),
    url(r'^inbox', views.inbox, name='inbox'),
    url(r'^indetail/(?P<mail_id>[0-9]+)/$', views.indetail, name='indetail'),
    url(r'^inloc', views.inloc, name='inloc'),
    url(r'^sentbox', views.sentbox, name='sentbox'),
    url(r'^sentdetail/(?P<mail_id>[0-9]+)/$', views.sentdetail, name='sentdetail'),
    url(r'^sentloc', views.sentloc, name='sentloc'),
    url(r'^incompose', views.incompose, name='incompose'),
    url(r'^inreply/(?P<mail_id>[0-9]+)/$', views.inreply, name='inreply'),
    url(r'^intofriend', views.intofriend, name='intofriend'),
    url(r'^inattachloc', views.inattachloc, name='inattachloc'),
    url(r'^mapinattach', views.mapinattach, name='mapinattach'),
    url(r'^infriends', views.infriends, name='infriends'),
    url(r'^tobox/(?P<user_id>[0-9]+)/$', views.tobox, name='tobox'),
    url(r'^incontactor/(?P<contactor_id>[0-9]+)/$', views.inboxcontactor, name='inboxcontactor'),
    url(r'^accept', views.accept, name='accept'),
    url(r'^acchat', views.acchat, name='acchat'),
    url(r'^provider_login_page', views.provider_login_page, name='provider_login_page'),
    url(r'^pay_to_provider', views.pay_to_provider, name='pay_to_provider'),
    url(r'^new_pay_to_provider', views.new_pay_to_provider, name='new_pay_to_provider'),
    url(r'^chatfriends', views.chatfriends, name='chatfriends'),
    url(r'^chatfriend', views.chatfriend, name='chatfriend'),
    url(r'^vacay_job_detail_(?P<job_id>[0-9]+)', views.vacay_job_detail, name='vacay_job_detail'),
    url(r'^vacayjob_media_(?P<job_id>[0-9]+)/$', views.vacay_job_media, name='job_media'),
    url(r'^vjob_loc/$', views.vacay_job_loc, name='vacay_job_loc'),
    url(r'^vacayalljobs/$', views.vacay_all_jobs, name='vacay_all_jobs'),
    url(r'^proservices/$', views.proservices, name='proservices'),
    url(r'^proproducts/$', views.proproducts, name='proproducts'),
    url(r'^proprodetail/(?P<itemid>[0-9]+)', views.proprodetail, name='proprodetail'),
    url(r'^procalendar/$', views.procalendar, name='procalendar'),
    url(r'^uploadproviderschedule', views.upload_provider_schedule, name='upload_provider_schedule'),
    url(r'^deleteschedule/(?P<availableid>[0-9]+)', views.deleteschedule, name='deleteschedule'),
    url(r'^searchvacayjobs', views.search_vacayjobs, name='search_vacayjobs'),
    url(r'^proaccept/(?P<mailid>[0-9]+)', views.proaccept, name='proaccept'),
    url(r'^prodecline/(?P<mailid>[0-9]+)', views.prodecline, name='prodecline'),
    url(r'^manager_register', views.manager_register, name='manager_register'),
    url(r'^register_manager', views.register_manager, name='register_manager'),
    url(r'^manager_login', views.manager_login, name='manager_login'),
    url(r'^managerlogin', views.managerlogin, name='managerlogin'),
    url(r'^loginmanager', views.login_manager, name='login_manager'),
    url(r'^managerhome', views.manager_home, name='manager_home'),
    url(r'^serviceproviders', views.service_providers, name='service_providers'),
    url(r'^verify_account/(?P<proid>[0-9]+)', views.verify_account, name='verify_account'),
    url(r'^complete_account', views.complete_account, name='complete_account'),
    url(r'^bmanager_payment', views.bmanager_payment, name='bmanager_payment'),
    url(r'^bpayment_update', views.bpayment_update, name='bpayment_update'),
    url(r'^managerprofile', views.managerprofile, name='managerprofile'),
    url(r'^retailmenu', views.retailmenu, name='retailmenu'),
    url(r'^getretailinfo', views.getretailinfo, name='getretailinfo'),
    url(r'^retaildetail/(?P<retailid>[0-9]+)', views.retaildetail, name='retaildetail'),
    url(r'^retail_media/(?P<retailid>[0-9]+)', views.retail_media, name='retail_media'),
    url(r'^employees', views.employees, name='employees'),
    url(r'^chatemployee', views.chatemployee, name='chatemployee'),
    url(r'^signmailemployee', views.signmailemployee, name='signmailemployee'),
    url(r'^companyjobs', views.companyjobs, name='companyjobs'),
    url(r'^companyannounces', views.companyannounces, name='companyannounces'),
    url(r'^respondeds', views.respondeds, name='respondeds'),
    url(r'^recorder', views.recorder, name='recorder'),
    url(r'^activities', views.activities, name='activities'),
    url(r'^actmenu', views.actmenu, name='actmenu'),
    url(r'^act', views.act, name='act'),
    url(r'^retail2detail/(?P<retailid>[0-9]+)', views.retail2detail, name='retail2detail'),
    url(r'^checkretailpayment', views.checkretailpayment, name='checkretailpayment'),
    url(r'^paytoretailer', views.paytoretailer, name='paytoretailer'),
    url(r'^linkedin_login', views.linkedin_login, name='linkedin_login'),
    url(r'^getlinkedin', views.getlinkedin, name='getlinkedin'),
    url(r'^linkedin', views.linkedin, name='linkedin'),
    url(r'^getinfo', views.getinfo, name='getinfo'),
    url(r'^editprofilepicture', views.editprofilepicture, name='editprofilepicture'),
    url(r'^providereditprofilepicture', views.providereditprofilepicture, name='providereditprofilepicture'),

    url(r'^testmap', views.testmap, name='testmap'),
]

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns=format_suffix_patterns(urlpatterns)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

































