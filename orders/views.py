from django.views.generic import DetailView, FormView, ListView


class OrderDetailView(DetailView):
    pass


class OrderProgressView(FormView, DetailView):
    pass


class OrderListView(ListView):
    pass