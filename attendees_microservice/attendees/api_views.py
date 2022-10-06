from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Attendee, ConferenceVO, AccountVO
from common.json import ModelEncoder
import json


class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = ["email", "name", "company_name", "created", "conference"]
    encoders = {
        "conference": ConferenceVODetailEncoder(),
    }

    def get_extra_data(self, o):
        # Get the count of AccountVO objects with email equal to o.email
        count = AccountVO.objects.filter(email=o.email).count()
        if count > 0:
            return {"has_account": True}
        return {"has_account": False}

        # Return a dictionary with "has_account": True if count > 0
        # Otherwise, return a dictionary with "has_account": False


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):

    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
        )

    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference_href = f"/api/conferences/{conference_vo_id}/"
            conference = ConferenceVO.objects.get(import_href=conference_href)
            content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, pk):

    if request.method == "GET":
        try:
            attendee = Attendee.objects.get(id=pk)
            return JsonResponse(
                attendee,
                encoder=AttendeeDetailEncoder,
                safe=False,
            )
        except Attendee.DoesNotExist:
            return JsonResponse({"message": "This is an invlaid attendee ID"})
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            Attendee.objects.filter(id=pk).update(**content)

            attendee = Attendee.objects.get(id=pk)
            return JsonResponse(
                attendee, encoder=AttendeeDetailEncoder, safe=False
            )
        except Attendee.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Conference ID or Invalid attendee ID"}
            )
