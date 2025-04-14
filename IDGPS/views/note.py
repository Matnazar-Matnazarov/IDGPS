from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from IDGPS.models import Note
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404


class NoteView(LoginRequiredMixin, View):
    def get(self, request):
        notes = Note.objects.all().order_by("-sana")
        return render(request, "note.html", {"notes": notes})


class NoteAddView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "note.html")

    def post(self, request):
        user = request.user
        note_content = request.POST.get("note")
        if note_content:
            note = Note(user=user, izoh=note_content)
            note.save()
            return redirect("note-list")
        return render(request, "note.html", {"error": "Please enter a note!"})


class NoteEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        note = get_object_or_404(Note, pk=pk)
        if note.user != request.user:
            return redirect("note-list")
        return render(request, "note.html", {"note": note, "is_edit": True})

    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk)
        if note.user != request.user:
            return redirect("note-list")
        note_content = request.POST.get("note")
        if note_content:
            note.izoh = note_content
            note.save()
            return redirect("note-list")
        return render(
            request,
            "note.html",
            {"error": "Please enter a note!", "note": note, "is_edit": True},
        )


class NoteDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk)
        if note.user != request.user:
            return redirect("note-list")
        note.delete()
        return redirect("note-list")
