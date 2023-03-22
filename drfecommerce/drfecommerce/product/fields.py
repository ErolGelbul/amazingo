from django.core import checks
from django.db import models

from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):

    description = "Ordering field on a unique field"

    def __init__(self, unique_for_field=None, *args, **kwargs):
        self.unique_for_field = unique_for_field
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_for_field_attribute(**kwargs),
        ]

    def _check_for_field_attribute(self, **kwargs):
        if self.unique_for_field is None:
            return [
                checks.Error("OrderField must define a 'unique_for_field' attribute")
            ]
        elif self.unique_for_field not in [
            f.name for f in self.model._meta.get_fields()
        ]:
            return [
                checks.Error("OrderField entered does not match any field on the model")
            ]
        return []

    def pre_save(self, model_instance, add):
        # If there is no value, we generate one
        # query: build the query string
        if getattr(model_instance, self.attname) is None:
            qs = self.model.objects.all()
            try:
                query = {
                    self.unique_for_field: getattr(
                        model_instance, self.unique_for_field
                    )
                }
                qs = qs.filter(**query)
                # grab the highest order value and make it the last by adding
                # one
                last_item = qs.latest(self.attname)
                value = last_item.order + 1

            # if there is no value, we set it to 1
            except ObjectDoesNotExist:
                value = 1
            return value
        else:
            return super().pre_save(model_instance, add)
