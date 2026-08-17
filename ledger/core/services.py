import logging
from typing import Any

from django.db import IntegrityError, models
from django.db.models import ProtectedError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, NotFound, ValidationError

from ledger.core.types import DjangoModelType

logger = logging.getLogger(__name__)


def model_update(
    *,
    instance: DjangoModelType,
    fields: list[str],
    data: dict[str, Any],
    auto_updated_at: bool = True,
    full_clean: bool = True,
) -> tuple[DjangoModelType, bool]:
    """Update a model instance with the provided field data.

    Only keys present in both ``fields`` and ``data`` are applied. Many-to-many
    fields are assigned after the instance is saved. Foreign keys given as
    integer PKs are resolved to related objects.

    Args:
        instance (DjangoModelType): The model instance to update.
        fields (list[str]): Field names that are allowed to change.
        data (dict[str, Any]): Mapping of field names to new values.
        auto_updated_at (bool, optional): Whether to stamp ``updated_at`` when
            any field changes. Defaults to True.
        full_clean (bool, optional): Whether to call ``full_clean()`` before
            save. Defaults to True.

    Returns:
        tuple[DjangoModelType, bool]: The instance and whether any field
            actually changed.

    Raises:
        ValidationError: When a related object is missing, a constraint is
            violated, or model validation fails.
        APIException: For unexpected errors during update.
    """
    try:
        has_updated = False
        m2m_data: dict[str, Any] = {}
        update_fields: list[str] = []

        model_fields = {field.name: field for field in instance._meta.get_fields()}

        for field in fields:
            if field not in data:
                continue

            model_field = model_fields.get(field)
            assert model_field is not None, f"{field} is not part of {instance.__class__.__name__} fields."

            if isinstance(model_field, models.ManyToManyField):
                m2m_data[field] = data[field]
                continue

            value_to_set = data[field]

            if isinstance(model_field, models.ForeignKey):
                related_model = model_field.related_model
                if isinstance(value_to_set, int):
                    try:
                        value_to_set = related_model.objects.get(pk=value_to_set)
                    except related_model.DoesNotExist as exc:
                        raise NotFound(f"{related_model.__name__} not found") from exc

            if getattr(instance, field) != value_to_set:
                has_updated = True
                update_fields.append(field)
                setattr(instance, field, value_to_set)

        if has_updated:
            if auto_updated_at and "updated_at" in model_fields and "updated_at" not in update_fields:
                update_fields.append("updated_at")
                instance.updated_at = timezone.now()

            if full_clean:
                instance.full_clean()

            instance.save(update_fields=update_fields)

        for field_name, value in m2m_data.items():
            getattr(instance, field_name).set(value)
            has_updated = True

        return instance, has_updated
    except IntegrityError as exc:
        logger.error("Integrity error updating %s: %s", instance.__class__.__name__, exc)
        raise ValidationError(_("A database constraint was violated.")) from exc
    except NotFound as exc:
        raise ValidationError(str(exc.detail)) from exc
    except ValidationError:
        raise
    except Exception as exc:
        logger.error("Error updating %s: %s", instance.__class__.__name__, exc)
        raise APIException(
            _("An error occurred while updating %(model)s, error: %(error)s")
            % {"model": instance.__class__.__name__, "error": exc}
        ) from exc


def model_delete(*, instance: DjangoModelType) -> None:
    """Hard-delete a model instance from the database.

    Args:
        instance (DjangoModelType): The model instance to delete.

    Raises:
        ValidationError: When deletion is blocked by protected relations or a
            database constraint.
        APIException: For unexpected errors during deletion.
    """
    try:
        instance.delete()
    except ProtectedError as exc:
        protected_objects = exc.protected_objects
        model_name = instance.__class__.__name__
        related_models = {obj.__class__.__name__ for obj in protected_objects} if protected_objects else set()
        related_info = ", ".join(related_models) if related_models else _("related objects")
        raise ValidationError(
            _(
                "Cannot delete %(model)s because it is referenced by protected "
                "%(related)s. Please remove related records first."
            )
            % {"model": model_name, "related": related_info}
        ) from exc
    except IntegrityError as exc:
        logger.error("Integrity error deleting %s: %s", instance.__class__.__name__, exc)
        raise ValidationError(_("A database constraint was violated.")) from exc
    except Exception as exc:
        model_name = instance.__class__.__name__
        logger.error("Error deleting %s: %s", model_name, exc)
        raise APIException(
            _("An unexpected error occurred while deleting %(model)s, error: %(error)s")
            % {"model": model_name, "error": exc}
        ) from exc
