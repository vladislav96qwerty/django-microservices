from rest_framework import permissions


class IsOrderOwner(permissions.BasePermission):
    """Object-level permission: only the order's owner may act on it.

    Staff users bypass the check so they can manage any order via the admin
    or via DRF endpoints if their group grants the model-level permissions.
    """

    message = "You can only act on your own orders."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user_id == request.user.id


class IsReviewAuthorOrReadOnly(permissions.BasePermission):
    """Anyone authenticated may post a review; only the author may edit/delete."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return obj.user_id == request.user.id
