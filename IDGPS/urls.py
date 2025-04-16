from django.urls import path
from .views.hodim import (
    HodimCreateView,
    HodimDeleteView,
    HodimListView,
    HodimUpdateView,
)
from .views.user import Loginview, LogoutView, Home
from .views.note import NoteAddView, NoteDeleteView, NoteEditView, NoteView
from .views.umumiy import MijozlarView, StatistikaView, GPSAddExcelView
from .views.rasxod import (
    RasxodAddView,
    RasxodDeleteView,
    RasxodListView,
    RasxodUpdateView,
)
from .views.sotish import (
    SotishAddView,
    SotishDeleteView,
    SotishListView,
    SotishUpdateView,
)
from .views.sklad import (
    SkladAddView,
    SkladDeleteView,
    SkladUpdateView,
    SkladView,
    sklad_list,
)
from .views.bugaltiriya import (
    UpdateBugalteriyaView,
    BugalteriyaView,
    Bugalteriya_ListView,
)

urlpatterns = [
    path("", Loginview.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("home/", Home.as_view(), name="home"),
    path("sklad/", SkladView.as_view(), name="sklad-list"),
    path("sklad/add/", SkladAddView.as_view(), name="skladadd"),
    path("sklad-filter/", sklad_list, name="filter-sklad"),
    path("sklad/update/<int:pk>/", SkladUpdateView.as_view(), name="sklad_update"),
    path("sklad/delete/<int:pk>/", SkladDeleteView.as_view(), name="sklad_delete"),
    path("sotuv/", SotishListView.as_view(), name="sotish_list"),
    path("sotuv/add/", SotishAddView.as_view(), name="sotish_add"),
    path("sotuv/update/<int:pk>/", SotishUpdateView.as_view(), name="sotish_update"),
    path("sotuv/delete/<int:pk>/", SotishDeleteView.as_view(), name="sotish_delete"),
    path("rasxod/", RasxodListView.as_view(), name="rasxod_list"),
    path("rasxod/add/", RasxodAddView.as_view(), name="rasxod_add"),
    path("rasxod/update/<int:pk>/", RasxodUpdateView.as_view(), name="rasxod_update"),
    path("rasxod/delete/<int:pk>/", RasxodDeleteView.as_view(), name="rasxod_delete"),
    path("mijozlar/", MijozlarView.as_view(), name="mijozlar"),
    path("statistika/", StatistikaView.as_view(), name="statistika"),
    path("bugalteriya/", BugalteriyaView.as_view(), name="bugalteriya"),
    path("bugalteriya/detail/<int:id>/", BugalteriyaView.as_view(), name="bugalteriya-detail"),
    path(
        "update_bugalteriya/",
        UpdateBugalteriyaView.as_view(),
        name="update_bugalteriya",
    ),
    path(
        "bugalteriya/update/<int:record_id>/",
        UpdateBugalteriyaView.as_view(),
        name="bugalteriya_update",
    ),
    path("hodimlar/", HodimListView.as_view(), name="hodim-list"),
    path("hodimlar/create/", HodimCreateView.as_view(), name="hodim-create"),
    path("hodimlar/update/<int:pk>/", HodimUpdateView.as_view(), name="hodim-update"),
    path("hodimlar/delete/<int:pk>/", HodimDeleteView.as_view(), name="hodim-delete"),
    path("note/", NoteView.as_view(), name="note-list"),
    path("note/add/", NoteAddView.as_view(), name="note-add"),
    path("note/update/<int:pk>/", NoteEditView.as_view(), name="note-update"),
    path("note/delete/<int:pk>/", NoteDeleteView.as_view(), name="note-delete"),
    path("sklad/add-excel/", GPSAddExcelView.as_view(), name="gps-add-excel"),
    path("bugalteriya-list/", Bugalteriya_ListView.as_view(), name="bugalteriya-list"),
]
