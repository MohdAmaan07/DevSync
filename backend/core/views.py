from rest_framework import generics


class SingletonUserView(generics.RetrieveUpdateAPIView):
    """
    Handles models that have a OneToOne relationship with the User.
    """

    def get_object(self):
        queryset = self.get_queryset()
        obj, _ = queryset.get_or_create(user=self.request.user)
        return obj
