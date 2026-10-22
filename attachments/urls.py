from rest_framework.routers import DefaultRouter
from .views import TaskAttachmentViewSet

router = DefaultRouter()
router.register(r"", TaskAttachmentViewSet, basename="attachment")

urlpatterns = router.urls
