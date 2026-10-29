from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('community/', views.community, name='community'),
    path('collections/<uuid:share_id>/', views.collection_detail, name='collection_detail'),
    path('api/favorites/toggle/', views.api_favorite_toggle, name='api_favorite_toggle'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('checkout/<slug:slug>/', views.checkout, name='checkout_product'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<str:tracking_code>/', views.order_success, name='order_success'),
    path('track/', views.track_order, name='track_order'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('balance/topup/', views.top_up_balance, name='topup_balance'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('oauth/google/', views.oauth_google_login, name='oauth_google'),
    path('oauth/google/callback/', views.oauth_google_callback, name='oauth_google_callback'),
    path('oauth/github/', views.oauth_github_login, name='oauth_github'),
    path('oauth/github/callback/', views.oauth_github_callback, name='oauth_github_callback'),
    path('api/product/<slug:slug>/price-history/', views.api_product_price_history, name='api_price_history'),
    path('api/notifications/', views.api_notifications_list, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.api_notification_mark_read, name='api_notification_read'),
    path('api/notifications/read-all/', views.api_notifications_read_all, name='api_notifications_read_all'),
    path('seller/<str:username>/', views.seller_profile, name='seller_profile'),
    path('seller/<str:username>/review/', views.submit_seller_review, name='submit_seller_review'),
    path('seller/<str:username>/report/', views.submit_seller_report, name='submit_seller_report'),
    path('api/purchase/', views.api_purchase_skins, name='api_purchase'),
    path('api/balance/', views.api_get_balance, name='api_balance'),
    path('api/game/reward/', views.api_game_claim_reward, name='api_game_reward'),
    path('api/upgrade/skins/', views.api_upgrade_skins, name='api_upgrade_skins'),
    path('api/upgrade/chance/', views.api_upgrade_chance, name='api_upgrade_chance'),
    path('game/', views.game_view, name='game'),
    path('upgrade/', views.skin_upgrade, name='skin_upgrade'),
]
