from django.urls import path
from . import views
from rest_framework_nested import routers
from pprint import pprint 

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')
router.register('address', views.AddressViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

customers_router = routers.NestedDefaultRouter(router, 'customers', lookup='customer')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls + customers_router.urls