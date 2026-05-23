from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model extending AbstractUser."""

    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(_("phone"), max_length=32, blank=True)
    address = models.CharField(_("address"), max_length=255, blank=True)
    avatar = models.ImageField(_("avatar"), upload_to="avatars/", blank=True, null=True)
    preferred_language = models.CharField(
        _("preferred language"),
        max_length=8,
        choices=(("en", "English"), ("uk", "Ukrainian")),
        default="en",
    )
    is_verified = models.BooleanField(_("verified"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.username or self.email
