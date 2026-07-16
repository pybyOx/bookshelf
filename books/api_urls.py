from .views import BookViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = router.urls
