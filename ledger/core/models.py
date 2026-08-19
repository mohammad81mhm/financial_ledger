from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Abstract base model with creation and update timestamps."""

    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        help_text="Date and time when this record was created.",
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated at"),
        help_text="Date and time when this record was last updated.",
        auto_now=True,
        editable=False,
    )

    class Meta:
        abstract = True
